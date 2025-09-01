# vmaudit
# Author: Arcitec
# Project Site: https://github.com/Arcitec/vmaudit
# SPDX-License-Identifier: GPL-2.0-only

import argparse
import getpass
import os
import re
import statistics
import sys
from typing import Optional, Union

from vmaudit.lib.cmdline import CmdLine
from vmaudit.lib.color import Color
from vmaudit.lib.vma import (
    KERNEL_DEFAULT_VMA_LIMIT,
    VMAOptimizer,
    get_vm_map_limit,
    read_slabinfo,
    scan_vma_usage,
)

ANONYMIZE = True

REAL_USERNAME = os.environ.get("SUDO_USER", getpass.getuser())

RGX_USERNAME = re.compile(re.escape(REAL_USERNAME), re.IGNORECASE)


def format_cmdline(cmdline: Union[CmdLine, str]) -> str:
    """Return a formatted and optionally anonymized command-line."""
    if isinstance(cmdline, CmdLine):
        cmdline = cmdline.to_string()

    if ANONYMIZE:
        # Very basic, but false positives don't matter here.
        # NOTE: Doesn't anonymize other names if running as root on multi-user
        # systems, but almost nobody uses personal computers like that.
        cmdline = RGX_USERNAME.sub("<user>", cmdline)

    return cmdline


def analyze_vma_usage(
    top_limit: int = 10,
    headroom_factor: float = 1.5,
    rounding_multiple: int = 10000,
    custom_vma_count: Optional[int] = None,
) -> None:
    """Analyze the system's current VMA usage and provide recommendations."""

    # Always show at least one detailed process (the heaviest process).
    if top_limit <= 0:
        top_limit = 1

    # Analyze all running processes.
    if os.geteuid() != 0:
        print(
            Color.RED(
                "** WARNING: This script is not running as root. "
                "You must run it as root if you want to scan all processes on the system. **"
            )
        )

    vma_stats = scan_vma_usage()

    if not vma_stats.processes:
        raise RuntimeError("No processes detected.")

    # The "VMA"-heaviest processes on the system.
    print(Color.LIGHT_BLUE(f"\n\n=== Top {top_limit} processes by VMA usage: ===\n"))
    print(
        Color.RED(
            "(WARNING: Do not share the detailed process top-list below. Their process arguments may contain SECRETS!)\n",
        )
    )
    print(
        f"{Color.BOLD_YELLOW.pad('VMA Count', 10)} "
        f"{Color.CYAN.pad('PID', 7)} "
        f"{Color.MAGENTA('Command')}"
    )
    print(Color.LIGHT_BLUE("-" * 80))

    for proc in vma_stats.processes[:top_limit]:
        print(
            f"{Color.BOLD_YELLOW.pad(proc.vma_count, 10)} "
            f"{Color.CYAN.pad(proc.pid, 7)} "
            f"{Color.MAGENTA(format_cmdline(proc.cmdline))}"
        )

    print(
        Color.RED(
            "\n(WARNING: Do not share the detailed process top-list above. Their process arguments may contain SECRETS!)",
        )
    )

    # Analyze per-application statistics.
    # NOTE: The kernel's VMA usage limit is per-process, not system-wide. Therefore,
    # the only thing that matters is the maximum VMA usage within a SINGLE process.
    # NOTE: When `fork()`-ing, child processes copy the parent's VMAs, but they
    # are independent COPIES and NOT counted as part of the parent's VMAs.
    # NOTE: Subprocess VMA usage does not count towards the parent's limit.
    print(Color.LIGHT_BLUE("\n\n=== Per-application VMA statistics: ===\n"))
    print(
        f"{Color.CYAN.pad('Instances', 10)} "
        f"{Color.BOLD_YELLOW.pad('Max VMAs', 10)} "
        f"{Color.GREEN.pad('Avg VMAs', 10)} "
        f"{Color.GREEN.pad('Min VMAs', 10)} "
        f"{Color.MAGENTA('Application')}"
    )
    print(Color.LIGHT_BLUE("-" * 80))

    for app_name, instance_vmas in sorted(
        vma_stats.app_stats.items(),
        # Sort apps by highest VMA count (descending), then by name (ascending).
        # NOTE: There's always at least one app-instance, so the list is never empty.
        key=lambda kv: (-max(kv[1]), kv[0]),
    ):
        instances = len(instance_vmas)
        app_vma_max = max(instance_vmas)
        app_vma_avg = round(statistics.mean(instance_vmas))
        app_vma_min = min(instance_vmas)

        print(
            f"{Color.CYAN.pad(instances, 10)} "
            f"{Color.BOLD_YELLOW.pad(app_vma_max, 10)} "
            f"{Color.GREEN.pad(app_vma_avg, 10)} "
            f"{Color.GREEN.pad(app_vma_min, 10)} "
            f"{Color.MAGENTA(format_cmdline(app_name))}"
        )

    total_vmas = sum(proc.vma_count for proc in vma_stats.processes)

    print(Color.LIGHT_BLUE("-" * 80))
    print(f"Total VMA count across all detected processes: {Color.BOLD_YELLOW(total_vmas)}")

    # Analyze the kernel's true VMA metadata count and limit.
    print(Color.LIGHT_BLUE("\n\n=== Kernel VMA metadata statistics: ===\n"))
    slabinfo = read_slabinfo()
    slabinfo_msg = (
        f"active={Color.BOLD_YELLOW(slabinfo.active)}, total={Color.BOLD_YELLOW(slabinfo.total)}"
        if slabinfo
        else "slabinfo not available (need to run as root to see kernel statistics)"
    )
    print(f"{Color.CYAN.pad('vm_area_struct:', 18)}  {slabinfo_msg}")

    vm_map_limit = get_vm_map_limit()
    print(f"{Color.CYAN.pad('vm.max_map_count:', 18)}  limit={Color.BOLD_YELLOW(vm_map_limit)}\n")

    print(
        f"(INFO: The kernel VMA max limit is {Color.CYAN('per-process')}. "
        f"The system's combined, {Color.CYAN('total')} VMA count {Color.CYAN('does not matter')}.)"
    )

    # Provide recommendations for tuning the VMA limit.
    print(Color.LIGHT_BLUE("\n\n=== Kernel VMA tuning recommendations: ===\n"))
    top_process = vma_stats.processes[0]

    add_divider = False
    for process_title, vma_count in [
        (top_process.app_path, top_process.vma_count),
        ("custom --vma value", custom_vma_count),
    ]:
        if vma_count is None:
            continue

        if add_divider:
            print(Color.LIGHT_BLUE(f"{'-' * 80}\n"))
        add_divider = True

        print(f"{Color.CYAN.pad('top process:', 18)}  {Color.MAGENTA(process_title)}")
        print(f"{Color.CYAN.pad('VMA usage:', 18)}  {Color.BOLD_YELLOW(vma_count)}\n")

        vma_optimizer = VMAOptimizer(vma_count)

        recommended_limit = vma_optimizer.calculate_max_map_count(
            headroom_factor, rounding_multiple
        )

        for title, limit in [
            ("current limit", vm_map_limit),
            ("recommended", recommended_limit),
        ]:
            headroom_percent = vma_optimizer.calculate_vma_limit_headroom(limit)
            if headroom_percent >= 20.0:
                headroom_color = Color.GREEN
            elif headroom_percent >= 5.0:
                headroom_color = Color.YELLOW
            else:
                headroom_color = Color.RED

            title_color = Color.GREEN if title == "recommended" else Color.CYAN

            print(
                f"{title_color.pad(f'{title}:', 18)}  vm.max_map_count={Color.BOLD_YELLOW(limit)} "
                f"({'kernel default' if limit == KERNEL_DEFAULT_VMA_LIMIT else 'custom value'})"
            )
            print(
                f"{Color.CYAN.pad('headroom:', 18)}  free VMAs={Color.BOLD_YELLOW(limit - vma_count)}, "
                f"free percent={headroom_color(f'{headroom_percent:.1f}%')}\n"
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="vmaudit",
        description="Analyzes Virtual Memory Area (VMA) utilization to provide data-driven recommendations for system administrators and developers.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("--top", type=int, default=20, help="how many processes to display")

    # Use a very generous, overkill "50% additional headroom" recommendation
    # to allow huge, unpredictable fluctuations. If a workload is predictable,
    # a headroom of "25%" is more reasonable.
    parser.add_argument("--headroom", type=float, default=1.5, help="headroom multiplier")

    parser.add_argument("--round", type=int, default=10000, help="headroom rounding multiple")

    # Allow the user to specify a custom VMA value to also calculate.
    parser.add_argument(
        "--vma", type=int, help="optional: largest expected VMA usage for a process"
    )

    args = parser.parse_args()

    try:
        analyze_vma_usage(args.top, args.headroom, args.round, args.vma)
    except Exception as e:
        # Detect the file and line number that threw the exception.
        exc_type, exc_value, exc_traceback = sys.exc_info()
        last_frame = exc_traceback
        while last_frame is not None and last_frame.tb_next:
            last_frame = last_frame.tb_next
        line_number = last_frame.tb_lineno if last_frame else -1
        file_name = last_frame.tb_frame.f_code.co_filename if last_frame else "?"

        # Show a simplified error message with enough information.
        print(Color.RED(f'ERROR: ["{os.path.basename(file_name)}:{line_number}"] {e}'))

        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
