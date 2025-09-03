"""
Batch process information collection for better performance.
"""

import platform
from typing import Dict, List, Set
from .subprocess_utils import run_command


def get_all_process_info_batch(pids: Set[int]) -> Dict[int, Dict[str, str]]:
    """Get process info for multiple PIDs in one call."""
    if not pids:
        return {}
    
    result = {}
    system = platform.system()
    
    if system == "Linux":
        return _get_linux_process_batch(pids)
    elif system == "Darwin":
        return _get_darwin_process_batch(pids)
    elif system == "Windows":
        return _get_windows_process_batch(pids)
    
    return result


def _get_linux_process_batch(pids: Set[int]) -> Dict[int, Dict[str, str]]:
    """Batch get Linux process info using single ps call."""
    pid_list = ",".join(str(pid) for pid in pids)
    
    try:
        # Single ps call to get user, command, and other info
        success, stdout, _ = run_command([
            'ps', '-p', pid_list, '-o', 'pid,user,comm,args', '--no-headers'
        ], timeout=3.0)
        
        if not success:
            return {}
        
        result = {}
        for line in stdout.strip().split('\n'):
            if not line.strip():
                continue
                
            parts = line.strip().split(None, 3)
            if len(parts) >= 4:
                pid = int(parts[0])
                result[pid] = {
                    'user': parts[1],
                    'process_name': parts[2],
                    'cmdline': parts[3]
                }
        
        return result
        
    except Exception:
        return {}


def _get_darwin_process_batch(pids: Set[int]) -> Dict[int, Dict[str, str]]:
    """Batch get macOS process info."""
    pid_list = ",".join(str(pid) for pid in pids)
    
    try:
        success, stdout, _ = run_command([
            'ps', '-p', pid_list, '-o', 'pid,user,comm,command', '-c'
        ], timeout=3.0)
        
        if not success:
            return {}
        
        result = {}
        lines = stdout.strip().split('\n')[1:]  # Skip header
        
        for line in lines:
            parts = line.strip().split(None, 3)
            if len(parts) >= 4:
                pid = int(parts[0])
                result[pid] = {
                    'user': parts[1],
                    'process_name': parts[2],
                    'cmdline': parts[3]
                }
        
        return result
        
    except Exception:
        return {}


def _get_windows_process_batch(pids: Set[int]) -> Dict[int, Dict[str, str]]:
    """Batch get Windows process info using PowerShell."""
    pid_list = ",".join(str(pid) for pid in pids)
    
    ps_cmd = f"""
    Get-Process -Id {pid_list} -ErrorAction SilentlyContinue | 
    Select-Object Id,ProcessName,@{{Name="Owner";Expression={{""SYSTEM""}}}} |
    ConvertTo-Json
    """
    
    try:
        success, stdout, _ = run_command(["powershell", "-Command", ps_cmd], timeout=5.0)
        if not success:
            return {}
        
        import json
        data = json.loads(stdout)
        if not isinstance(data, list):
            data = [data]
        
        result = {}
        for item in data:
            pid = item.get('Id')
            if pid:
                result[pid] = {
                    'user': item.get('Owner', 'SYSTEM'),
                    'process_name': item.get('ProcessName', 'unknown'),
                    'cmdline': item.get('ProcessName', 'unknown')
                }
        
        return result
        
    except Exception:
        return {}