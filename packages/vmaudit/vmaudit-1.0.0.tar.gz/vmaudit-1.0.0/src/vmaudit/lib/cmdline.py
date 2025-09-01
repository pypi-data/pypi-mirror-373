# vmaudit
# Author: Arcitec
# Project Site: https://github.com/Arcitec/vmaudit
# SPDX-License-Identifier: GPL-2.0-only


import re
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class CmdLine:
    args: List[str]

    def to_string(self) -> str:
        """Return the command-line as a shell-escaped string."""
        return shlex.join(self.args)

    @classmethod
    def from_pid(cls, pid: int) -> "CmdLine":
        """Get the command-line for the given process."""
        proc_dir = Path(f"/proc/{pid}")

        try:
            cmdline_path = proc_dir / "cmdline"
            raw = cmdline_path.read_bytes()  # Bytes, usually NUL-separated args.
            # Split into bytes-chunks on NUL, decode and strip each part.
            parts: List[str] = [
                part.decode("utf-8", errors="replace").strip()
                for part in raw.split(b"\x00")
                if part  # Skip empty bytes chunks quickly.
            ]
            if parts:
                # Handle special case: Uses spaces instead of NUL-separated args.
                # NOTE: Can happen with some containerized processes.
                # NOTE: The processing is nasty since there's *nothing* that tells
                # us where the command ends and the arguments begin.
                if len(parts) == 1:
                    # First attempt to split on Windows ".exe", so that we never
                    # end up misdetecting Windows executable paths.
                    # NOTE: If there's nothing after the divider, we get an empty
                    # second element. But at least we've detected that it's an exe.
                    arg_split: List[str]
                    is_windows = re.search(r"^[a-zA-Z]:[\/\\]", parts[0]) is not None
                    if is_windows:
                        # Only attempt ".exe" split if path began with drive letter.
                        arg_split = re.split(r"(?i)(\.exe)\b\s*", parts[0], maxsplit=1)
                        if len(arg_split) == 3:
                            # When splitting with a capture, it captures the divider
                            # as a separate entry, so we need to join them again.
                            arg_split = [f"{arg_split[0]}{arg_split[1]}", arg_split[2]]
                    if not is_windows or len(arg_split) != 2:
                        # If we didn't find a ".exe", attempt to split on earliest
                        # "[whitespace][dash][not whitespace]" to find arguments.
                        # NOTE: There's no better way to do this. The command
                        # is stored without any quoted paths, so we can't tell the
                        # difference between a flag or a directory named "/a - b/"
                        # in the path, so the best we can do is restrict it to
                        # flags that are followed by a non-whitespace character.
                        # NOTE: This will have false negatives whenever the argument
                        # is not preceded by a "-", but there's no way solve that.
                        # NOTE: We can't split via shlex directly, since it would
                        # instantly split on the first whitespace, which is wrong.
                        arg_split = re.split(r"\s+(-\S)", parts[0], maxsplit=1)
                        if len(arg_split) == 3:
                            # Join the split-divider with the arguments again.
                            arg_split = [arg_split[0], f"{arg_split[1]}{arg_split[2]}"]

                    # If we've split on ".exe" or arguments, post-process the args.
                    if len(arg_split) == 2:
                        if len(arg_split[1]) == 0:
                            # Remove empty trailing split element.
                            arg_split.pop()
                        else:
                            # Post-process the argument-string via shlex to split
                            # into individual arguments.
                            # NOTE: Shlex really hates Windows backslashes in paths
                            # and erases them, which happens whenever Wine apps
                            # use Windows paths in any of their arguments. :/
                            try:
                                extra_args = shlex.split(arg_split[1])
                                # Replace the extra arguments with the shlex split.
                                arg_split.pop()
                                arg_split.extend(extra_args)
                            except ValueError:
                                # Fallback: Keep as single argument if shlex fails.
                                pass

                        # Place the final command and args in the list.
                        parts = arg_split

                return cls(parts)
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            pass

        # Fallback to "comm" parsing (single command, no arguments).
        try:
            comm_path = proc_dir / "comm"
            comm = comm_path.read_text(encoding="utf-8").strip()
            if comm:
                return cls([comm])
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            pass

        return cls([f"[pid {pid}]"])


def detect_app(cmdline: CmdLine) -> str:
    """
    Detect the "real" application from complex command-line arguments.

    The parsing is pretty basic, but good enough for the purpose.
    """

    args = cmdline.args

    # Ignore the bwrap Flatpak sandboxing wrapper.
    if args and args[0] == "/usr/bin/bwrap":
        try:
            bwrap_cmdsep = args.index("--")  # Separated by double dash.
            args = args[bwrap_cmdsep + 1 :]
        except ValueError:
            # No "--" found; keep as-is.
            pass

    # Ignore the zypak Chromium/Electron Flatpak integration helper.
    if args and args[0] == "/app/bin/zypak-helper":
        try:
            zypak_cmdsep = args.index("-")  # Separated by single dash.
            args = args[zypak_cmdsep + 1 :]
        except ValueError:
            # No "-" found; keep as-is.
            pass

    # Ignore the Python2/3 interpreter and detect actual script name instead.
    if args and re.search(r"(?:^|\/)python[\d.]*$", args[0]):
        # Attempt to find the first non-flag Python argument.
        for i, arg in enumerate(args[1:], start=1):
            if not arg.startswith("-"):
                args = args[i:]
                if "\n" in args[0]:
                    # Python has been executed with "-c" code. Only keep line 1.
                    py_code = args[0].splitlines()
                    return f'[Python Code "{py_code[0].strip()}"...]'
                break

    if not args:
        return "[unknown]"

    # Detect a very common Electron subprocess wrapper.
    is_electron_subproc = args[0] == "/proc/self/exe"

    # Analyze the individual arguments/tokens to learn more about the process.
    for t in args:
        if ".asar" in t:
            # Handle "--flag=/path/to/app.asar".
            if t.startswith("--") and "=" in t:
                after_eq = t.split("=", 1)[1]  # Empty "" if nothing after "=".
                if ".asar" in after_eq:
                    t = after_eq
            # It's an Electron ".asar" app package.
            return f'[Electron App "{t}"]'
        elif is_electron_subproc and t.startswith("--user-data-dir="):
            # Anonymous Electron child process. Identify via its data dir.
            return f'[Electron Helper for "{t[16:]}"]'

    # Use the first argument (the Linux/Wine application path).
    app_name = args[0]
    if re.search(r"\.exe$", app_name, re.IGNORECASE):
        return f'[Wine App "{app_name}"]'
    return app_name
