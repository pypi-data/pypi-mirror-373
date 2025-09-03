"""
Unified process killing functionality for portndock.
"""

import os
import platform
import signal
from typing import List, Set, Tuple, Optional

from .config import CRITICAL_PROCESSES
from .subprocess_utils import run_command


class ProcessKiller:
    """Unified process killing with platform-specific optimizations."""
    
    def kill_by_pid(self, pid: int, sig: int = signal.SIGTERM, dry_run: bool = False) -> Tuple[bool, str]:
        """Kill a process by PID with tree killing."""
        try:
            if dry_run:
                return True, f"Would send signal {sig} to PID {pid}"
            
            if platform.system() == "Windows":
                return self._kill_tree_windows(pid, sig == signal.SIGKILL)
            else:
                self._kill_tree_posix(pid, sig)
                return True, f"Sent signal {sig} to PID {pid}"
        
        except ProcessLookupError:
            return True, f"PID {pid} not found (already terminated)"
        except PermissionError:
            return False, f"Permission denied for PID {pid}"
        except Exception as e:
            return False, f"Failed to kill PID {pid}: {e}"
    
    def kill_multiple(self, pids: List[int], sig: int = signal.SIGTERM, dry_run: bool = False) -> int:
        """Kill multiple processes, return success count."""
        success_count = 0
        for pid in pids:
            success, _ = self.kill_by_pid(pid, sig, dry_run)
            if success:
                success_count += 1
        return success_count
    
    def _collect_children_posix(self, root_pid: int) -> Set[int]:
        """Collect all child PIDs recursively on POSIX systems."""
        children = set()
        try:
            if platform.system() == "Linux":
                success, stdout, stderr = run_command(["pgrep", "-P", str(root_pid)], timeout=3.0)
                if success:
                    for line in stdout.strip().split('\n'):
                        if line.strip():
                            child_pid = int(line.strip())
                            children.add(child_pid)
                            children.update(self._collect_children_posix(child_pid))
            else:  # Darwin/macOS
                success, stdout, stderr = run_command(["ps", "-eo", "pid,ppid"], timeout=3.0)
                if success:
                    pid_map = {}
                    for line in stdout.strip().split('\n')[1:]:  # Skip header
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            try:
                                pid, ppid = int(parts[0]), int(parts[1])
                                if ppid not in pid_map:
                                    pid_map[ppid] = []
                                pid_map[ppid].append(pid)
                            except ValueError:
                                continue
                    
                    def collect_recursive(parent_pid):
                        result = set()
                        for child in pid_map.get(parent_pid, []):
                            result.add(child)
                            result.update(collect_recursive(child))
                        return result
                    
                    children = collect_recursive(root_pid)
        except Exception:
            pass
        return children
    
    def _kill_tree_posix(self, root_pid: int, sig: int) -> None:
        """Kill a process tree on POSIX systems."""
        children = self._collect_children_posix(root_pid)
        
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
    
    def _kill_tree_windows(self, root_pid: int, force: bool) -> Tuple[bool, str]:
        """Kill a process tree on Windows."""
        args = ["taskkill", "/PID", str(root_pid), "/T"]
        if force:
            args.append("/F")
        
        try:
            success, stdout, stderr = run_command(args, timeout=10.0)
            message = stdout.strip() or stderr.strip()
            return success, message
        except Exception as e:
            return False, str(e)


def parse_signal(sig_str: str) -> int:
    """Parse signal string to signal number."""
    sig_str = sig_str.upper()
    signal_map = {
        "TERM": signal.SIGTERM, "SIGTERM": signal.SIGTERM,
        "KILL": signal.SIGKILL, "SIGKILL": signal.SIGKILL, "9": signal.SIGKILL,
        "INT": signal.SIGINT, "SIGINT": signal.SIGINT, "2": signal.SIGINT,
        "HUP": signal.SIGHUP, "SIGHUP": signal.SIGHUP, "1": signal.SIGHUP,
        "USR1": signal.SIGUSR1, "SIGUSR1": signal.SIGUSR1,
        "USR2": signal.SIGUSR2, "SIGUSR2": signal.SIGUSR2
    }
    
    if sig_str in signal_map:
        return signal_map[sig_str]
    elif sig_str.isdigit():
        return int(sig_str)
    else:
        raise ValueError(f"Unknown signal: {sig_str}")


# Global instance
process_killer = ProcessKiller()