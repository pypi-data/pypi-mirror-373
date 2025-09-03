"""
Core data structures and port detection functionality for portndock.
"""

import os
import platform
import re
import shutil
import sys
from dataclasses import dataclass
from typing import List, Optional, Tuple, Iterable

from .config import DEV_PORTS, CRITICAL_PROCESSES
from .subprocess_utils import run_command, find_executable


def is_dev_port(port: int, mode: str) -> bool:
    """Check if a port is considered a development port based on mode."""
    if mode == "all":
        return True
    
    # Common dev ranges
    dev_ranges = [
        (3000, 3999),  # React, Node.js dev servers
        (8000, 8999),  # Django, Flask, various dev servers
        (5000, 5999),  # Flask default, various dev tools
        (4000, 4999),  # Angular, Webpack dev server alternatives
        (9000, 9999),  # Various dev tools and proxies
        (1337, 1337),  # Popular dev port
        (8080, 8080),  # Common alternative HTTP port
        (3001, 3001),  # Common alternative to 3000
    ]
    
    # Database and infrastructure ports (stack mode)
    stack_ports = {5432, 3306, 6379, 27017, 9200, 5984, 5672, 15672, 6380, 6381, 
                   3307, 3308, 5433, 5434, 27018, 27019, 9300, 9043, 9160}
    
    if mode == "app":
        return any(start <= port <= end for start, end in dev_ranges)
    elif mode == "stack":
        return (any(start <= port <= end for start, end in dev_ranges) or 
                port in stack_ports)
    
    return False


@dataclass
class ListeningSocket:
    """Represents a listening socket with associated process information."""
    protocol: str
    local_ip: str
    local_port: int
    pid: Optional[int] = None
    process_name: Optional[str] = None
    user_name: Optional[str] = None
    cmdline: Optional[str] = None
    
    # Process hierarchy
    ppid: Optional[int] = None
    parent_process_name: Optional[str] = None
    container_id: Optional[str] = None
    container_name: Optional[str] = None
    # More context for safety and docker/compose mapping
    repo_name: Optional[str] = None
    container_image: Optional[str] = None
    compose_project: Optional[str] = None
    compose_service: Optional[str] = None
    container_port: Optional[str] = None  # e.g., "5000/tcp" mapped from host port
    container_host_ip: Optional[str] = None
    
    def __post_init__(self):
        if self.process_name and "/" in self.process_name:
            self.process_name = os.path.basename(self.process_name)


# Legacy alias for compatibility
CRITICAL_PROCESS_DENYLIST = CRITICAL_PROCESSES


def ensure_ss_available() -> None:
    """Ensure 'ss' command is available on Linux."""
    if platform.system() == "Linux" and not find_executable("ss"):
        print("Error: 'ss' command not found. Please install iproute2 package.", file=sys.stderr)
        print("  Ubuntu/Debian: sudo apt install iproute2", file=sys.stderr)
        print("  RHEL/CentOS/Fedora: sudo yum install iproute2 (or dnf)", file=sys.stderr)
        sys.exit(1)


def parse_ss_line(line: str, protocol: str) -> Optional[ListeningSocket]:
    """Parse a line from 'ss' output into a ListeningSocket."""
    # ss output format varies, but generally:
    # tcp   LISTEN  0  128   0.0.0.0:22   0.0.0.0:*   users:(("sshd",pid=1234,fd=3))
    parts = line.strip().split()
    if len(parts) < 4:
        return None
    
    proto = parts[0]
    state = parts[1] if len(parts) > 1 else ""
    
    # TCP uses LISTEN, UDP uses UNCONN (unconnected)
    if proto.lower() == "tcp" and state != "LISTEN":
        return None
    elif proto.lower() == "udp" and state != "UNCONN":
        return None
        
    # Find local address (usually 4th column, but can vary)
    local_addr = None
    for i, part in enumerate(parts[2:6], 2):  # Check columns 2-5
        if ":" in part and not part.startswith("users:"):
            local_addr = part
            break
    
    if not local_addr:
        return None
        
    try:
        ip, port = extract_ip_port(local_addr)
    except (ValueError, IndexError):
        return None
    
    # Extract PID and process info from users:(...) 
    pid = None
    process_name = None
    
    users_match = re.search(r'users:\(\("([^"]+)",pid=(\d+)', line)
    if users_match:
        process_name = users_match.group(1)
        pid = int(users_match.group(2))
    
    # If no process info from ss, try alternative methods
    if not pid or not process_name:
        fallback_info = get_process_by_port(port, proto)
        if fallback_info:
            fallback_pid, fallback_name = fallback_info
            if not pid:
                pid = fallback_pid
            if not process_name:
                process_name = fallback_name
    
    # Get user name from PID if available
    user_name = None
    if pid:
        user_name = get_process_user(pid)
    
    # If no process name and it's a system port, try to get the service name
    if not process_name or process_name == "-":
        system_service = get_system_service_name(port, proto)
        if system_service:
            process_name = system_service
    
    # Use the protocol parameter passed from the calling function, not the ss output
    actual_protocol = protocol if protocol in ['tcp', 'udp'] else proto.lower()
    
    return ListeningSocket(
        protocol=actual_protocol,
        local_ip=ip,
        local_port=port,
        pid=pid,
        process_name=process_name,
        user_name=user_name
    )


def get_process_user(pid: int) -> Optional[str]:
    """Get the username of the process owner from PID."""
    try:
        # Try reading from /proc/PID/status (Linux)
        with open(f'/proc/{pid}/status', 'r') as f:
            for line in f:
                if line.startswith('Uid:'):
                    # Uid: 1000    1000    1000    1000
                    uid = int(line.split()[1])
                    # Convert UID to username
                    import pwd
                    return pwd.getpwuid(uid).pw_name
    except (FileNotFoundError, PermissionError, ValueError, KeyError, OSError):
        # Fallback: try ps command
        try:
            success, stdout, _ = run_command(['ps', '-o', 'user=', '-p', str(pid)])
            if success and stdout.strip():
                return stdout.strip()
        except Exception:
            pass
    
    return None


def get_system_service_name(port: int, protocol: str = "tcp") -> Optional[str]:
    """Get likely service name for common system ports."""
    common_services = {
        22: "sshd",
        53: "systemd-resolved", 
        80: "apache2/nginx",
        443: "apache2/nginx", 
        631: "cupsd",
        3306: "mysqld",
        5432: "postgres",
        6379: "redis-server",
        27017: "mongod",
    }
    return common_services.get(port)


def get_process_by_port(port: int, protocol: str = "tcp") -> Optional[Tuple[Optional[int], str]]:
    """Get process info for a port using alternative methods when ss fails."""
    # First try common system services
    service_name = get_system_service_name(port, protocol)
    if service_name:
        return None, service_name  # No PID but we have a service name
    
    # Try lsof for user processes  
    try:
        success, stdout, _ = run_command(['lsof', f'-i{protocol}:{port}', '-t'])
        if success and stdout.strip():
            pids = [int(p) for p in stdout.strip().split('\n') if p.isdigit()]
            if pids:
                pid = pids[0]  # Take first PID
                try:
                    with open(f'/proc/{pid}/comm', 'r') as f:
                        process_name = f.read().strip()
                        return pid, process_name
                except:
                    pass
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    return None


def extract_ip_port(addr: str) -> Tuple[str, int]:
    """Extract IP and port from address string like '0.0.0.0:22' or '[::]:80'."""
    if addr.startswith('['):
        # IPv6 format: [::1]:8080
        match = re.match(r'\[([^\]]+)\]:(\d+)', addr)
        if not match:
            raise ValueError(f"Invalid IPv6 address format: {addr}")
        return match.group(1), int(match.group(2))
    else:
        # IPv4 format: 0.0.0.0:22
        if addr.count(':') != 1:
            raise ValueError(f"Invalid IPv4 address format: {addr}")
        ip, port_str = addr.rsplit(':', 1)
        return ip, int(port_str)


def run_ss_listening(protocol: str) -> List[ListeningSocket]:
    """Get listening sockets using 'ss' command (Linux)."""
    ensure_ss_available()
    
    # Build ss command
    if protocol == "tcp":
        cmd = ["ss", "-tlnp"]
    elif protocol == "udp":
        cmd = ["ss", "-ulnp"]
    else:  # protocol == "all"
        cmd = ["ss", "-tulnp"]
    
    try:
        success, stdout, _ = run_command(cmd)
        if not success:
            return []
        lines = stdout.strip().split('\n')[1:]  # Skip header
    except Exception:
        return []
    
    sockets = []
    for line in lines:
        if not line.strip():
            continue
        socket = parse_ss_line(line, protocol)
        if socket:
            sockets.append(socket)
    
    return sockets


def deduplicate_sockets(sockets: Iterable[ListeningSocket]) -> List[ListeningSocket]:
    """Remove duplicate sockets based on protocol, IP, port, and PID."""
    seen = set()
    result = []
    for s in sockets:
        key = (s.protocol, s.local_ip, s.local_port, s.pid)
        if key not in seen:
            seen.add(key)
            result.append(s)
    return result


def find_related_processes(sockets: List[ListeningSocket]) -> List[ListeningSocket]:
    """Find related processes (like Electron renderers) that don't listen on ports."""
    related = []
    
    # Group processes by name to find related ones
    process_names = set()
    for s in sockets:
        if s.process_name:
            process_names.add(s.process_name)
    
    # Find processes with similar names (electron, node, etc.)
    for proc_name in process_names:
        if proc_name in ['node', 'electron', 'Electron']:
            try:
                success, stdout, _ = run_command(['pgrep', '-f', proc_name], timeout=3.0)
                if success:
                    for line in stdout.strip().split('\n'):
                        if line.strip():
                            pid = int(line.strip())
                            # Check if this PID is already in our sockets
                            if not any(s.pid == pid for s in sockets):
                                # Create a fake socket entry for UI display
                                related.append(ListeningSocket(
                                    protocol="proc",
                                    local_ip="-",
                                    local_port=0,
                                    pid=pid,
                                    process_name=proc_name,
                                    user_name=_get_process_user(pid)
                                ))
            except Exception:
                pass
    
    return related


def list_open_ports(protocol_filter: str, dev_filter: str = "all", include_related: bool = False) -> List[ListeningSocket]:
    """Get all listening sockets using the appropriate method for the OS."""
    system = platform.system()
    
    if system == "Linux":
        sockets = run_ss_listening(protocol_filter)
    elif system in ("Darwin", "FreeBSD", "OpenBSD", "NetBSD"):
        sockets = run_lsof_listening(protocol_filter)
    elif system == "Windows":
        sockets = run_windows_listening(protocol_filter)
    else:
        # Fallback to lsof for unknown Unix-like systems
        sockets = run_lsof_listening(protocol_filter)
    
    # Early filtering to reduce processing overhead
    if dev_filter != "all":
        sockets = [s for s in sockets if is_dev_port(s.local_port, dev_filter)]
    
    # Add related processes if requested
    if include_related:
        related = find_related_processes(sockets)
        sockets.extend(related)
    
    return deduplicate_sockets(sockets)


def run_lsof_listening(protocol_filter: str) -> List[ListeningSocket]:
    """Get listening sockets using 'lsof' command (macOS, BSD, Unix)."""
    if not shutil.which("lsof"):
        return []
    
    # Build lsof command for listening sockets
    if protocol_filter == "tcp":
        cmd = ["lsof", "-nP", "-iTCP", "-sTCP:LISTEN"]
    elif protocol_filter == "udp":
        cmd = ["lsof", "-nP", "-iUDP"]  # UDP doesn't have LISTEN state
    else:  # "all"
        # Get both TCP listening and all UDP
        tcp_cmd = ["lsof", "-nP", "-iTCP", "-sTCP:LISTEN"]
        udp_cmd = ["lsof", "-nP", "-iUDP"]
        
        tcp_sockets = []
        udp_sockets = []
        
        try:
            success, stdout, _ = run_command(tcp_cmd)
            if success:
                tcp_sockets = _parse_lsof_output(stdout, "tcp")
        except Exception:
            pass
        
        try:
            success, stdout, _ = run_command(udp_cmd)
            if success:
                udp_sockets = _parse_lsof_output(stdout, "udp")
        except Exception:
            pass
        
        return tcp_sockets + udp_sockets
    
    try:
        success, stdout, _ = run_command(cmd)
        if success:
            return _parse_lsof_output(stdout, protocol_filter)
    except Exception:
        pass
    return []


def _parse_lsof_output(output: str, protocol: str) -> List[ListeningSocket]:
    """Parse lsof output into ListeningSocket objects."""
    sockets = []
    lines = output.strip().split('\n')
    
    if not lines:
        return sockets
    
    # Skip header line if present
    if lines and lines[0].startswith('COMMAND'):
        lines = lines[1:]
    
    for line in lines:
        if not line.strip():
            continue
        
        # lsof output format: COMMAND PID USER FD TYPE DEVICE SIZE/OFF NODE NAME
        parts = line.split(None, 8)  # Split into max 9 parts
        if len(parts) < 9:
            continue
        
        process_name = parts[0]
        pid = int(parts[1]) if parts[1].isdigit() else None
        user_name = parts[2]
        name = parts[8]  # This contains the address info
        
        # Parse address from NAME field (e.g., "*:8080", "127.0.0.1:3000", "[::1]:8080")
        if not (":" in name and ("TCP" in name or "UDP" in name or "*:" in name or "localhost:" in name)):
            continue
        
        # Extract protocol from the TYPE or NAME field
        detected_proto = "tcp" if "TCP" in line else "udp"
        
        # Skip if protocol doesn't match filter
        if protocol not in ("all", detected_proto):
            continue
        
        try:
            # Handle different address formats in lsof output
            if "*:" in name:
                # Format: *:8080 (LISTEN)
                port = int(name.split(":")[1].split()[0])
                ip = "0.0.0.0"
            elif "localhost:" in name:
                ip = "127.0.0.1"
                port = int(name.split(":")[1].split()[0])
            elif "[" in name and "]:" in name:
                # IPv6 format: [::1]:8080
                match = re.search(r'\[([^\]]+)\]:(\d+)', name)
                if match:
                    ip = match.group(1)
                    port = int(match.group(2))
                else:
                    continue
            elif ":" in name:
                # Standard format: 127.0.0.1:8080
                addr_part = name.split()[0] if " " in name else name
                ip, port_str = addr_part.rsplit(":", 1)
                port = int(port_str)
            else:
                continue
        
        except (ValueError, IndexError):
            continue
        
        # If no process name and it's a system port, try to get the service name
        if not process_name or process_name == "-":
            system_service = get_system_service_name(port, detected_proto)
            if system_service:
                process_name = system_service
        
        sockets.append(ListeningSocket(
            protocol=detected_proto,
            local_ip=ip,
            local_port=port,
            pid=pid,
            process_name=process_name,
            user_name=user_name
        ))
    
    return sockets


def _run_powershell_json(command: str) -> Optional[object]:
    """Run a PowerShell command and parse JSON output."""
    try:
        import json
        success, stdout, _ = run_command(["powershell", "-Command", command])
        if success and stdout.strip():
            return json.loads(stdout.strip())
        return []
    except (json.JSONDecodeError, Exception):
        return None


def run_windows_listening(protocol_filter: str) -> List[ListeningSocket]:
    """Get listening sockets on Windows using PowerShell."""
    # PowerShell command to get network connections with process info
    ps_cmd = """
    Get-NetTCPConnection | Where-Object {$_.State -eq 'Listen'} | 
    ForEach-Object {
        $proc = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
        [PSCustomObject]@{
            Protocol = 'tcp'
            LocalAddress = $_.LocalAddress
            LocalPort = $_.LocalPort
            PID = $_.OwningProcess
            ProcessName = if($proc) {$proc.ProcessName} else {'Unknown'}
        }
    } | ConvertTo-Json
    """
    
    udp_cmd = """
    Get-NetUDPEndpoint | 
    ForEach-Object {
        $proc = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
        [PSCustomObject]@{
            Protocol = 'udp'
            LocalAddress = $_.LocalAddress
            LocalPort = $_.LocalPort
            PID = $_.OwningProcess
            ProcessName = if($proc) {$proc.ProcessName} else {'Unknown'}
        }
    } | ConvertTo-Json
    """
    
    sockets = []
    
    if protocol_filter in ("tcp", "all"):
        tcp_data = _run_powershell_json(ps_cmd)
        if tcp_data:
            # Handle both single object and array results
            tcp_connections = tcp_data if isinstance(tcp_data, list) else [tcp_data]
            for conn in tcp_connections:
                if isinstance(conn, dict):
                    sockets.append(ListeningSocket(
                        protocol="tcp",
                        local_ip=conn.get("LocalAddress", ""),
                        local_port=int(conn.get("LocalPort", 0)),
                        pid=int(conn.get("PID", 0)) if conn.get("PID") else None,
                        process_name=conn.get("ProcessName")
                    ))
    
    if protocol_filter in ("udp", "all"):
        udp_data = _run_powershell_json(udp_cmd)
        if udp_data:
            udp_connections = udp_data if isinstance(udp_data, list) else [udp_data]
            for conn in udp_connections:
                if isinstance(conn, dict):
                    sockets.append(ListeningSocket(
                        protocol="udp", 
                        local_ip=conn.get("LocalAddress", ""),
                        local_port=int(conn.get("LocalPort", 0)),
                        pid=int(conn.get("PID", 0)) if conn.get("PID") else None,
                        process_name=conn.get("ProcessName")
                    ))
    
    return sockets


def print_table(rows: List[ListeningSocket]) -> None:
    """Print a formatted table of listening sockets."""
    if not rows:
        print("No listening processes found.")
        return
    
    headers = ["PROTO", "PORT", "PID", "USER", "PROCESS", "ADDRESS"]
    
    # Calculate column widths
    data = []
    for s in rows:
        data.append([
            s.protocol,
            str(s.local_port),
            str(s.pid or "-"),
            s.user_name or "-",
            s.process_name or "-",
            s.local_ip,
        ])
    
    # Add headers to data for width calculation
    all_rows = [headers] + data
    col_widths = [max(len(str(row[i])) for row in all_rows) for i in range(len(headers))]
    
    # Print header
    header_row = "  ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    print(header_row)
    print("-" * len(header_row))
    
    # Print data rows
    for row in data:
        data_row = "  ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(row)))
        print(data_row)


def find_pids_by_port(port: int, protocol: str) -> List[Tuple[int, Optional[str]]]:
    """Find all PIDs using a specific port."""
    sockets = list_open_ports(protocol)
    return [(s.pid, s.process_name) for s in sockets 
            if s.local_port == port and s.pid is not None]


def _is_port_free(port: int, protocol: str, dev_mode: str = "all") -> bool:
    """Check if a port is free (not being used by any process)."""
    sockets = [s for s in list_open_ports(protocol) if is_dev_port(s.local_port, dev_mode)]
    return not any(s.local_port == port for s in sockets)


def _read_file_safely(path: str) -> Optional[str]:
    """Safely read a file, returning None if it fails."""
    try:
        with open(path, 'r') as f:
            return f.read().strip()
    except (OSError, IOError):
        return None


# Simple cache for expensive process lookups (PID -> (timestamp, result))
_process_cache = {}
_cache_ttl = 1.0  # 1 second cache

def _cleanup_cache():
    """Remove stale entries from process cache."""
    import time
    now = time.time()
    to_remove = [k for k, (timestamp, _) in _process_cache.items() if now - timestamp > _cache_ttl * 3]
    for k in to_remove:
        del _process_cache[k]

def _get_process_cmdline(pid: int) -> Optional[str]:
    """Get the command line for a process by PID."""
    if not pid:
        return None
    
    # Check cache first
    import time
    now = time.time()
    cache_key = f"cmdline_{pid}"
    if cache_key in _process_cache:
        timestamp, result = _process_cache[cache_key]
        if now - timestamp < _cache_ttl:
            return result
    
    result = None
    if platform.system() == "Linux":
        # Read from /proc/PID/cmdline
        cmdline_path = f"/proc/{pid}/cmdline"
        try:
            with open(cmdline_path, 'rb') as f:
                cmdline_bytes = f.read()
                # Convert null-separated arguments to space-separated
                cmdline = cmdline_bytes.replace(b'\x00', b' ').decode('utf-8', errors='ignore').strip()
                result = cmdline if cmdline else None
        except (OSError, IOError):
            pass
        
        # Fallback: try ps command
        if result is None:
            try:
                success, stdout, _ = run_command(['ps', '-p', str(pid), '-o', 'cmd='], timeout=5.0)
                if success:
                    cmd = stdout.strip()
                    result = cmd if cmd else None
            except Exception:
                pass
    
    elif platform.system() == "Darwin":  # macOS
        try:
            success, stdout, _ = run_command(['ps', '-p', str(pid), '-o', 'command='], timeout=5.0)
            if success:
                cmd = stdout.strip()
                result = cmd if cmd else None
        except Exception:
            pass
    
    elif platform.system() == "Windows":
        try:
            # Use PowerShell to get process command line
            ps_cmd = f"Get-Process -Id {pid} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty CommandLine"
            success, stdout, _ = run_command(["powershell", "-Command", ps_cmd], timeout=5.0)
            if success and stdout.strip():
                result = stdout.strip()
        except Exception:
            pass
    
    # Cache the result and return
    _process_cache[cache_key] = (now, result)
    return result


def _get_process_user(pid: int) -> Optional[str]:
    """Get the user that owns a process by PID."""
    if not pid:
        return None
    
    # Check cache first
    import time
    now = time.time()
    cache_key = f"user_{pid}"
    if cache_key in _process_cache:
        timestamp, result = _process_cache[cache_key]
        if now - timestamp < _cache_ttl:
            return result
    
    result = None
    if platform.system() == "Linux":
        # Read from /proc/PID/status
        status_path = f"/proc/{pid}/status"
        try:
            with open(status_path, 'r') as f:
                for line in f:
                    if line.startswith('Uid:'):
                        # Get the real UID (first number)
                        uid = line.split()[1]
                        # Convert UID to username
                        import pwd
                        try:
                            return pwd.getpwuid(int(uid)).pw_name
                        except (KeyError, ValueError):
                            return uid  # Return UID if username lookup fails
        except (OSError, IOError):
            pass
        
        # Fallback: try ps command
        try:
            success, stdout, _ = run_command(['ps', '-p', str(pid), '-o', 'user='], timeout=2.0)
            if success:
                user = stdout.strip()
                return user if user else None
        except Exception:
            pass
    
    elif platform.system() == "Darwin":  # macOS
        try:
            success, stdout, _ = run_command(['ps', '-p', str(pid), '-o', 'user='], timeout=2.0)
            if success:
                user = stdout.strip()
                result = user if user else None
        except Exception:
            pass
    
    elif platform.system() == "Windows":
        try:
            # Use PowerShell to get process owner
            ps_cmd = f"Get-Process -Id {pid} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty ProcessName"
            success, _, _ = run_command(["powershell", "-Command", ps_cmd], timeout=5.0)
            # Windows doesn't easily give process owner, return generic
            result = "SYSTEM" if success else None
        except Exception:
            pass
    
    # Cache the result and return
    _process_cache[cache_key] = (now, result)
    return result


def enrich_with_docker_info(sockets: List[ListeningSocket]) -> None:
    """Enrich socket objects with Docker container information."""
    from .docker_manager import docker_manager
    for socket in sockets:
        docker_manager.enrich_socket_with_container_info(socket)


def enrich_sockets_with_process_info(sockets: List[ListeningSocket]) -> None:
    """Enrich ListeningSocket objects with additional process information like cmdline."""
    # Occasionally clean up stale cache entries
    if len(_process_cache) > 100:
        _cleanup_cache()
    
    # Batch optimization: collect all PIDs that need info
    pids_needing_info = set()
    for socket in sockets:
        if socket.pid and (not socket.cmdline or not socket.user_name):
            pids_needing_info.add(socket.pid)
    
    # Skip batch processing if only a few PIDs (not worth the overhead)
    if len(pids_needing_info) > 3:
        from .process_batch import get_all_process_info_batch
        batch_info = get_all_process_info_batch(pids_needing_info)
        
        # Apply batch results
        for socket in sockets:
            if socket.pid and socket.pid in batch_info:
                info = batch_info[socket.pid]
                if not socket.user_name:
                    socket.user_name = info.get('user')
                if not socket.cmdline:
                    socket.cmdline = info.get('cmdline')
                if not socket.process_name and info.get('process_name'):
                    socket.process_name = info.get('process_name')
    else:
        # Fall back to individual calls for small numbers
        for socket in sockets:
            if socket.pid:
                if not socket.cmdline:
                    socket.cmdline = _get_process_cmdline(socket.pid)
                if not socket.user_name:
                    socket.user_name = _get_process_user(socket.pid)