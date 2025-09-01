# vmaudit

Analyzes Virtual Memory Area (VMA) utilization to provide data-driven
recommendations for system administrators and developers.

[![PyPI Package](https://badge.fury.io/py/vmaudit.svg)](https://pypi.org/project/vmaudit/)


## Understanding Linux Virtual Memory Areas (VMAs)

### Key Concepts

- **What are VMAs?**
    - A Virtual Memory Area (VMA) is a contiguous region of virtual memory within
      a process's address space.
    - VMAs are used for the application's code, data/text segments, stack, heap,
      and any memory-mapped files (including anonymous regions) or shared libraries.
    - You can view the VMAs for a specific process by inspecting its `/proc/<pid>/maps`
      file. Each line represents a `struct vm_area_struct` (VMA) in the kernel.
    - **File descriptors are not VMAs.** File descriptors (`struct file` in the
      kernel) don't create VMAs on their own. Instead, they count against the
      file descriptor limit (`ulimit -n`), **not** the `vm.max_map_count` limit.
      This is a common point of confusion since memory-mapped files do create
      VMAs. You can view the file descriptors for a process by listing its `fd`
      allocations via `ls -l /proc/<pid>/fd`.
    - **Synchronization primitives are not VMAs.** Things like futexes, mutexes,
      semaphores, pipes and sockets don't create VMAs unless they're backed by
      shared memory mappings.


- **The `vm.max_map_count` Kernel Limit**
    - That kernel setting defines the **maximum number of VMAs a single process**
      **can have**.
    - It is a **per-process limit**, not a system-wide total.
    - The VMA count of a child process (including `fork()`) is separate and does
      **not** count towards its parent's limit.
    - If a process reaches the limit, it will not be allowed to allocate any
      further memory. Allocation attempts will then be rejected with "out of
      memory" (`ENOMEM`) as the reason, even if the system still has plenty
      of available memory.


### Typical VMA Usage

The number of VMAs a process uses can vary significantly depending on the application.

- **Typical Linux Processes:**
    - Most command-line tools and normal applications use **fewer than 1,000** VMAs.
    - Heavier desktop applications (such as Electron-/Chromium-based applications)
      or development tools might in very rare cases use up to **10,000** VMAs,
      but they're typically below **4,000** VMAs.

- **Gaming (via Wine/Proton):**
    - Most games use between **5,000 and 35,000** VMAs.
    - A few exceptionally demanding games are known to push this limit much higher:
        - **Counter-Strike 2**, **Hogwarts Legacy**, and **Star Citizen** can use
          between **30,000 and 80,000** VMAs.

- **Specialized Software:**
    - **Elasticsearch** requires a VMA limit of **262,144** (their arbitrarily
      selected number; simply 64x 4096). Their official packages [automatically](https://www.elastic.co/docs/deploy-manage/deploy/self-managed/vm-max-map-count)
      configure this VMA limit for your system upon installation. This number
      was determined to be safe by Elasticsearch, and is verified by a bootstrap
      check on every startup, to ensure that your system is suitable for
      production use.
    - **Docker Desktop** on Mac/Windows internally sets every container's limit
      to **262,144**, to accommodate running Elasticsearch inside a container.
      However, all native containers (whether Docker or Podman or something else)
      share the Linux kernel with the host machine. Therefore, if you're running on
      a Linux host, the container always inherits the exact same value as the host.


### Recommended VMA Limit

- If you want a custom-tailored recommendation for your own system, you can use
  `vmaudit` to analyze your system. Otherwise, use the recommendations below.
- For **general Linux desktop** use, the kernel's default `vm.max_map_count` value
  of **65,530** is incredibly generous and will always work.
- For **Wine/Proton gaming** use, setting `vm.max_map_count` to **120,000** is
  a safe and very generous value that will prevent issues with even the most
  VMA-intensive games and applications.
- For **Elasticsearch** use, set `vm.max_map_count` to **262,144** (or **300,000**
  if you want a nice, round number), since it's the officially required value
  and provides plenty of headroom for very demanding search engine servers.
- The value **does not need to be a power of two**. Any sufficiently large integer
  is correct.


### Why Not Go Higher?

- Setting `vm.max_map_count` to a very high number is dangerous. Each VMA is
  a non-swappable kernel data structure that consumes a small amount of memory.
  While negligible for a single VMA, this overhead can accumulate rapidly. This
  can exhaust the kernel's slab memory, leading to **kernel crashes**. High
  limits also degrade system performance, as managing and traversing millions
  of VMAs can **severely slow down** essential kernel operations such as regular
  housekeeping and common syscalls like `mmap()` and `munmap()`.
- To make matters worse, the kernel's OOM (out-of-memory) handler doesn't take
  the kernel's internal VMA structs into account when deciding which processes
  to terminate, and will instead start terminating various high-memory desktop
  processes (or important background services) when the system is running out of
  memory. The malicious or misbehaving process that's responsible for allocating
  all the VMAs usually won't be terminated until it's too late.
- This attack has been demonstrated with a proof-of-concept DoS (denial-of-service)
  application, which runs entirely in user-mode and is capable of crashing Linux
  by simply allocating lots of VMAs. It is especially dangerous for shared
  multi-user machines, such as servers, where a hostile user could then run
  a malicious binary to crash the entire server. The proof-of-concept attack
  code is available on [Fedora's mailing list](https://lists.fedoraproject.org/archives/list/devel@lists.fedoraproject.org/message/YGTDBA2XENG7GSMHFYZQNIIGCGS3LQCD/).
- In summary, setting the limit to an extreme value creates a **Denial-of-Service (DoS)**
  vulnerability, where a single **misbehaving or malicious user-space process**
  can consume vast amounts of kernel memory and very high CPU usage, thus bringing
  the entire system to a **crash or severe slowdown**.
- While a moderate increase from the kernel's default 65,530 to something like
  120,000 or 300,000 is reasonable for a few specific, very heavy workloads;
  raising the limit blindly to millions or billions of VMAs is mostly **cargo-cult**
  **paranoia**, and is both absolutely **pointless** and **poses a stability risk**.
  Always remember that typical Linux processes use less than 2,000 VMAs!


### Changing Your System's VMA Limit

- To view your current VMA limit, execute any of the following commands (or
  run `vmaudit`, which also analyzes your current limit).

```sh
sysctl vm.max_map_count

cat /proc/sys/vm/max_map_count
```

- You can change the active limit for the current, running system by executing
  the following command (with your own value). This change will take effect
  immediately, but will be lost after a reboot.

```sh
sudo sysctl -w vm.max_map_count=120000
```

- You can make the change permanent by executing the following command, and then
  rebooting your system.

```sh
echo "vm.max_map_count=120000" | sudo tee /etc/sysctl.d/90-vm_max_map_count.conf
```


## How to Install `vmaudit`

- **Recommended:** Installing the package via pip.

```sh
# Only for the current user (will only be able to scan the current user's processes):
pip install vmaudit

# Alternative: Global install to be able to scan all system processes (recommended).
sudo pip install vmaudit
```

- **Alternative:** Installing the package directly from source.

```sh
git clone https://github.com/Arcitec/vmaudit.git
cd vmaudit

# User installation.
pip install .

# Alternative: Global installation (recommended).
sudo pip install .
```

- Note: In all of these examples, it's recommended to replace the `pip` command
  with [pipx](https://pipx.pypa.io/stable/installation/) instead, which installs
  CLI tools into isolated environments for improved reliability. However, you
  should never run "sudo pipx", since the per-user pipx installation is runnable
  as root without needing to be installed globally.

- If you ever want to remove the package again, run the `uninstall` command.

```sh
# User installation.
pip uninstall vmaudit

# Alternative: If you've installed it globally.
sudo pip uninstall vmaudit
```

- You can also run the package directly from source code without installing it.
  See the next section.


## How to Use `vmaudit`

- Running the virtual memory analyzer when it has been **installed as a package**.

```sh
# Scanning the current user's processes:
vmaudit

# Scanning all processes on the system:
# NOTE: Only works if you've installed vmaudit via "sudo pip".
sudo vmaudit

# Alternative: Scanning all processes on the system (only for "pipx" installs):
sudo "$(which vmaudit)"
```

- Alternative: Running **directly from source code**. Supports both user and
  system scans.

```sh
# Scanning the current user's processes:
python src/vmaudit

# Scanning all processes on the system:
sudo python src/vmaudit
```

- If you know the **maximum number of VMAs** observed or expected for a process,
  then you can provide it directly to receive a custom recommendation.

```sh
vmaudit --vma 80000
```

- There are several other options to tweak the algorithm. However, the defaults
  are already correct, so most people will have no reason to change the parameters.

```sh
vmaudit -h
```

- Note: By default, the recommendation algorithm uses a very generous, overkill
  "50% additional headroom" recommendation to allow for huge, unpredictable
  memory usage fluctuations. If your workload is predictable, a headroom
  of "25%" is more reasonable, if you want to further optimize the limit for
  your particular usage.


---

This project is licensed under the GPLv2 License.
See the [LICENSE](LICENSE) file for details.

Find out how to [contribute](CONTRIBUTING.md) to this project.
