"""
Process management utilities for portndock.
"""

import os
import platform
import signal
import subprocess
import time
from pathlib import Path
from typing import List, Set, Tuple, Optional

from .core import CRITICAL_PROCESS_DENYLIST


def parse_signal(sig_str: str) -> int:
    """Parse signal string to signal number."""
    sig_str = sig_str.upper()
    if sig_str in ("TERM", "SIGTERM"):
        return signal.SIGTERM
    elif sig_str in ("KILL", "SIGKILL", "9"):
        return signal.SIGKILL
    elif sig_str in ("INT", "SIGINT", "2"):
        return signal.SIGINT
    elif sig_str in ("HUP", "SIGHUP", "1"):
        return signal.SIGHUP
    elif sig_str in ("USR1", "SIGUSR1"):
        return signal.SIGUSR1
    elif sig_str in ("USR2", "SIGUSR2"):
        return signal.SIGUSR2
    elif sig_str.isdigit():
        return int(sig_str)
    else:
        raise ValueError(f"Unknown signal: {sig_str}")


def kill_pid(pid: int, sig: int, dry_run: bool = False) -> Tuple[bool, str]:
    """Kill a process by PID."""
    try:
        if dry_run:
            return True, f"Would send signal {sig} to PID {pid}"
        
        if platform.system() == "Windows":
            if sig == signal.SIGKILL:
                return _kill_tree_windows(pid, force=True, dry_run=dry_run)
            else:
                return _kill_tree_windows(pid, force=False, dry_run=dry_run)
        else:
            _kill_tree_posix(pid, sig, dry_run=dry_run)
            return True, f"Sent signal {sig} to PID {pid}"
    
    except ProcessLookupError:
        return True, f"PID {pid} not found (already terminated)"
    except PermissionError:
        return False, f"Permission denied for PID {pid}"
    except Exception as e:
        return False, f"Failed to kill PID {pid}: {e}"


def _sleep(seconds: float) -> None:
    """Sleep for given seconds."""
    time.sleep(seconds)


def _collect_children_linux(root_pid: int) -> Set[int]:
    """Collect all child PIDs recursively on Linux."""
    children = set()
    try:
        # Use pgrep to find children
        result = subprocess.run(
            ["pgrep", "-P", str(root_pid)],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    child_pid = int(line.strip())
                    children.add(child_pid)
                    # Recursively collect grandchildren
                    children.update(_collect_children_linux(child_pid))
    except (subprocess.CalledProcessError, ValueError, FileNotFoundError):
        pass
    return children


def _collect_children_darwin(root_pid: int) -> Set[int]:
    """Collect all child PIDs recursively on macOS."""
    children = set()
    try:
        # Use ps to find children  
        result = subprocess.run(
            ["ps", "-eo", "pid,ppid"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            pid_map = {}
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 2:
                    try:
                        pid, ppid = int(parts[0]), int(parts[1])
                        if ppid not in pid_map:
                            pid_map[ppid] = []
                        pid_map[ppid].append(pid)
                    except ValueError:
                        continue
            
            # Recursively collect all descendants
            def collect_recursive(parent_pid):
                result = set()
                for child in pid_map.get(parent_pid, []):
                    result.add(child)
                    result.update(collect_recursive(child))
                return result
            
            children = collect_recursive(root_pid)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return children


def _kill_tree_posix(root_pid: int, sig: int, dry_run: bool = False) -> None:
    """Kill a process tree on POSIX systems."""
    if dry_run:
        print(f"Would kill process tree starting from PID {root_pid} with signal {sig}")
        return
    
    system = platform.system()
    
    # Collect all child PIDs first
    if system == "Linux":
        children = _collect_children_linux(root_pid)
    elif system == "Darwin":
        children = _collect_children_darwin(root_pid)
    else:
        children = set()
    
    # Kill children first (reverse topological order)
    for child_pid in children:
        try:
            os.kill(child_pid, sig)
        except (ProcessLookupError, PermissionError):
            pass
    
    # Finally kill the root process
    try:
        os.kill(root_pid, sig)
    except (ProcessLookupError, PermissionError):
        pass


def _kill_tree_windows(root_pid: int, force: bool, dry_run: bool = False) -> Tuple[bool, str]:
    """Kill a process tree on Windows."""
    args = ["taskkill", "/PID", str(root_pid), "/T"]
    if force:
        args.append("/F")
    
    if dry_run:
        return True, f"Would run: {' '.join(args)}"
    
    try:
        result = subprocess.run(args, capture_output=True, text=True)
        success = result.returncode == 0
        message = result.stdout.strip() or result.stderr.strip()
        return success, message
    except FileNotFoundError:
        return False, "taskkill command not found"


def _detect_project_processes(project_path: str) -> List[Tuple[int, str, str]]:
    """Detect processes that appear to be related to a project directory."""
    processes = []
    
    try:
        if platform.system() == "Windows":
            # Windows process detection using wmic
            result = subprocess.run([
                "wmic", "process", "get", "ProcessId,Name,CommandLine", "/format:csv"
            ], capture_output=True, text=True)
            
            for line in result.stdout.splitlines()[1:]:  # Skip header
                if not line.strip():
                    continue
                parts = line.split(',')
                if len(parts) >= 4:
                    try:
                        pid = int(parts[3])
                        name = parts[2] or "unknown"
                        cmdline = parts[1] or ""
                        if _is_process_in_project(pid, project_path, cmdline):
                            processes.append((pid, name, cmdline))
                    except (ValueError, IndexError):
                        continue
        else:
            # Unix-like systems using ps
            result = subprocess.run([
                "ps", "axo", "pid,comm,args"
            ], capture_output=True, text=True)
            
            for line in result.stdout.splitlines()[1:]:  # Skip header
                if not line.strip():
                    continue
                parts = line.strip().split(None, 2)
                if len(parts) >= 3:
                    try:
                        pid = int(parts[0])
                        name = parts[1]
                        cmdline = parts[2]
                        if _is_process_in_project(pid, project_path, cmdline):
                            processes.append((pid, name, cmdline))
                    except (ValueError, IndexError):
                        continue
    
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    return processes


def _is_process_in_project(pid: int, project_path: str, cmdline: str) -> bool:
    """Check if a process appears to be related to a project."""
    if not cmdline:
        return False
    
    # Normalize paths
    project_path = os.path.abspath(project_path)
    
    # Skip obviously unrelated processes
    skip_processes = {
        "kernel", "kthreadd", "systemd", "init", "launchd",
        "WindowServer", "loginwindow", "Dock", "Finder",
        "explorer.exe", "dwm.exe", "winlogon.exe", "csrss.exe"
    }
    
    process_name = os.path.basename(cmdline.split()[0] if cmdline.split() else "")
    if process_name.lower() in skip_processes:
        return False
    
    # Check if command line contains project path
    if project_path in cmdline:
        return True
    
    # Check if process is running from project directory
    try:
        if platform.system() != "Windows":
            cwd_path = f"/proc/{pid}/cwd"
            if os.path.exists(cwd_path):
                real_cwd = os.path.realpath(cwd_path)
                if real_cwd.startswith(project_path):
                    return True
    except (OSError, IOError):
        pass
    
    # Check for common development processes
    dev_indicators = [
        "node", "npm", "yarn", "pnpm", "bun",
        "python", "django", "flask", "gunicorn", "uvicorn",
        "ruby", "rails", "puma",
        "go", "cargo", "rust",
        "webpack", "vite", "rollup", "parcel",
        "jest", "mocha", "cypress",
        "docker", "docker-compose"
    ]
    
    if any(indicator in cmdline.lower() for indicator in dev_indicators):
        # Further check if it's actually related to our project
        project_name = os.path.basename(project_path)
        if project_name.lower() in cmdline.lower():
            return True
    
    return False


def _get_current_project_path() -> Optional[str]:
    """Get the current project path by walking up from cwd looking for common project files."""
    current = os.getcwd()
    project_indicators = [
        "package.json", "Cargo.toml", "go.mod", "requirements.txt", "setup.py", "pyproject.toml",
        ".git", ".gitignore", "Makefile", "docker-compose.yml", "Dockerfile"
    ]
    
    while True:
        for indicator in project_indicators:
            if os.path.exists(os.path.join(current, indicator)):
                return current
        
        parent = os.path.dirname(current)
        if parent == current:  # Reached root
            break
        current = parent
    
    return None


def _find_related_processes(port_processes: List[int]) -> List[int]:
    """Find processes related to the ones using ports (same project, children, etc)."""
    if not port_processes:
        return []
    
    project_path = _get_current_project_path()
    if not project_path:
        return port_processes
    
    # Get all processes that might be related to this project
    project_processes = _detect_project_processes(project_path)
    related_pids = [pid for pid, name, cmdline in project_processes]
    
    # Combine port processes with related project processes
    all_related = list(set(port_processes + related_pids))
    
    return all_related


def _kill_related_processes(force: bool = False) -> int:
    """Kill processes related to the current project."""
    project_path = _get_current_project_path()
    if project_path:
        return _kill_project_processes(project_path, force)
    return 0


def _kill_project_processes(project_path: str, force: bool = False) -> int:
    """Kill all processes related to a project. Returns count of killed processes."""
    processes = _detect_project_processes(project_path)
    
    if not processes:
        return 0
    
    print(f"Found {len(processes)} processes related to project:")
    for pid, name, cmdline in processes:
        short_cmd = cmdline[:60] + "..." if len(cmdline) > 60 else cmdline
        print(f"  PID {pid}: {name} - {short_cmd}")
    
    # Filter out critical processes
    safe_processes = []
    for pid, name, cmdline in processes:
        if name.lower() not in CRITICAL_PROCESS_DENYLIST:
            safe_processes.append((pid, name, cmdline))
        else:
            print(f"Skipping critical process: PID {pid} ({name})")
    
    if not safe_processes:
        print("No safe processes to kill.")
        return 0
    
    sig = signal.SIGKILL if force else signal.SIGTERM
    killed_count = 0
    
    for pid, name, cmdline in safe_processes:
        try:
            success, msg = kill_pid(pid, sig, dry_run=False)
            if success:
                print(f"Killed PID {pid} ({name})")
                killed_count += 1
            else:
                print(f"Failed to kill PID {pid} ({name}): {msg}")
        except Exception as e:
            print(f"Error killing PID {pid} ({name}): {e}")
    
    return killed_count