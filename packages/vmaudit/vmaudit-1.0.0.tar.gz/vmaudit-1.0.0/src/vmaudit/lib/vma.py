# vmaudit
# Author: Arcitec
# Project Site: https://github.com/Arcitec/vmaudit
# SPDX-License-Identifier: GPL-2.0-only


import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from vmaudit.lib.cmdline import CmdLine, detect_app

# The kernel's default VMA limit is 65530, which is the max value that fits
# in an unsigned 16-bit integer (65535), minus 5 for some headroom. They
# chose that number because coredumps are written in ELF format, where the
# ELF "section" counter uses an unsigned 16-bit integer. So it's the highest
# amount of VMAs that can fit in a backwards-compatible ELF coredump.
# SEE: https://github.com/torvalds/linux/blob/v5.18/include/linux/mm.h#L178-L195
# NOTE: Higher values CAN be used, but will create a newer, "extended ELF" file.
KERNEL_DEFAULT_VMA_LIMIT = 65530


def get_vm_map_limit() -> int:
    """Return the maximum per-process VMA map limit used by the system."""
    try:
        limit_path = Path("/proc/sys/vm/max_map_count")
        limit = limit_path.read_text(encoding="utf-8").strip()
        if limit and limit.isdigit():
            return int(limit, 10)
    except (FileNotFoundError, PermissionError, ProcessLookupError):
        pass
    return 0


def get_vma_count(pid: int) -> int:
    """Return the number of VMAs (lines in `/proc/<pid>/maps`)."""
    # NOTE: The `maps` lines contain filenames and metadata, making it possible
    # to analyze exactly which shared `.so` libs and files are loaded.
    maps_path = Path(f"/proc/{pid}/maps")
    try:
        # Count newlines. Behavior matches "wc -l". Operates on 16x 4K blocks.
        with maps_path.open("rb") as f:  # Binary mode for speed.
            return sum(chunk.count(b"\n") for chunk in iter(lambda: f.read(65536), b""))
    except (FileNotFoundError, PermissionError, ProcessLookupError):
        return 0


@dataclass
class VMAreaStruct_Stats:
    active: int
    total: int


def read_slabinfo() -> Optional[VMAreaStruct_Stats]:
    """Try to read the Kernel's `/proc/slabinfo` and extract `vm_area_struct` stats."""
    # NOTE: Every VMA is allocated in the Kernel's slab cache, and is counted
    # in the slab cache's info, accessible via the following file.
    slabinfo_path = Path("/proc/slabinfo")
    if not slabinfo_path.is_file():
        return None

    try:
        with slabinfo_path.open("rt", encoding="utf-8") as f:
            for line in f:
                if line.startswith("vm_area_struct"):
                    parts = line.split()  # Split on consecutive whitespace runs.
                    if len(parts) >= 3:
                        # slabinfo format: name active_objs num_objs ...
                        return VMAreaStruct_Stats(active=int(parts[1], 10), total=int(parts[2], 10))
    except (PermissionError, FileNotFoundError):
        return None

    return None


@dataclass
class ProcessInfo:
    pid: int
    cmdline: CmdLine
    app_path: str
    vma_count: int


@dataclass
class VMA_ScanResults:
    processes: List[ProcessInfo]
    app_stats: Dict[str, List[int]]


def scan_vma_usage() -> VMA_ScanResults:
    """Return VMA statistics for all running processes."""
    processes: List[ProcessInfo] = []
    app_stats: Dict[str, List[int]] = defaultdict(list)

    for entry in Path("/proc").iterdir():
        if entry.name.isdigit():
            pid = int(entry.name, 10)
            vma_count = get_vma_count(pid)
            if vma_count > 0:
                cmdline = CmdLine.from_pid(pid)
                app_path = detect_app(cmdline)
                processes.append(ProcessInfo(pid, cmdline, app_path, vma_count))
                app_stats[app_path].append(vma_count)

    # Sort processes by highest VMA count (descending), then by name (ascending).
    # NOTE: The caller can easily get the "top process" since it'll be the 1st entry.
    processes.sort(key=lambda x: (-x.vma_count, x.app_path))

    return VMA_ScanResults(processes, app_stats)


@dataclass
class VMAOptimizer:
    """Performs analysis and optimization for the Linux kernels's VMA limit."""

    # Maximum number of VMAs observed or expected for a process.
    vma_peak: int

    def __post_init__(self) -> None:
        if self.vma_peak < 1:
            raise ValueError("VMA Peak must be a positive number.")

    def calculate_max_map_count(
        self, headroom_factor: float = 1.25, rounding_multiple: int = 10000
    ) -> int:
        """
        Calculates a recommended `vm.max_map_count` for the Linux kernel.

        That setting controls the maximum number of virtual memory areas (VMAs)
        a process can have. Applications that use many memory-mapped files or shared
        libraries, such as databases, search engines, or certain heavy Windows games,
        might need that limit increased.

        Note that the `vm.max_map_count` limit is just an integer, and isn't
        restricted to "powers of 2" or any other special rules.

        Args:
            headroom_factor: Multiplier for the safety margin. Defaults to 1.25 (25%).
            rounding_multiple: Produces nicely rounded recommendations. Set to 1 to
                disable. Defaults to 10000.

        Returns:
            The recommended integer value for the `vm.max_map_count` sysctl setting.
        """

        if headroom_factor < 1.2:
            raise ValueError(
                "Headroom factor should never be lower than 1.2 (20%), to ensure that processes have enough headroom for fluctuations."
            )

        if rounding_multiple < 1:
            raise ValueError("Rounding multiple must be 1 or higher.")

        # Determine the raw recommendation via the headroom factor.
        recommended = self.vma_peak * headroom_factor

        # Suggest the kernel's own default if the recommended number fits.
        if recommended <= KERNEL_DEFAULT_VMA_LIMIT:
            return KERNEL_DEFAULT_VMA_LIMIT
        else:
            # Round upwards to produce a nicer number.
            if rounding_multiple > 1:
                recommended = math.ceil(recommended / rounding_multiple) * rounding_multiple

            # Ensure it's never in the kernel's reserved 16-bit ELF header range.
            # NOTE: Replicates the kernel's "65535 - 5 reserved = 65530" behavior,
            # since other ELF data requires a few free slots in the 16-bit ELF range.
            if KERNEL_DEFAULT_VMA_LIMIT < recommended <= 65535:
                # Since the recommendation was in the reserved 16-bit ELF range, they
                # aren't using any rounding. So just push the recommendation above
                # a 16-bit number to force a kernel switch to "extended ELF" format.
                recommended = 65536

            return int(recommended)

    def calculate_vma_limit_headroom(self, vma_limit: int) -> float:
        """Return the remaining VMA limit headroom as a percentage."""
        return ((vma_limit - self.vma_peak) / vma_limit) * 100
