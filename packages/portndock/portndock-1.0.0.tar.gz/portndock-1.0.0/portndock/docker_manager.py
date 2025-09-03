"""
Centralized Docker operations for portndock.
"""

import os
import re
import time
from typing import Dict, List, Optional, Tuple, NamedTuple

from .config import DOCKER_CACHE_TTL, DOCKER_TIMEOUT
from .subprocess_utils import run_docker_command, is_docker_available


class ContainerInfo(NamedTuple):
    """Container information structure."""
    id: str
    name: str
    image: str
    container_port: str
    host_ip: str
    compose_project: Optional[str] = None
    compose_service: Optional[str] = None


class DockerManager:
    """Centralized Docker operations with caching."""
    
    def __init__(self):
        self._ps_cache = {"timestamp": 0, "data": ({}, {})}
        self._port_cache = {"timestamp": 0, "data": {}}
    
    def is_available(self) -> bool:
        """Check if Docker is available."""
        return is_docker_available()
    
    def get_pid_to_container_map(self) -> Tuple[Dict[int, Tuple[str, str]], Dict[str, str]]:
        """Get maps: pid->(container_id, name) and container_id->name."""
        now = time.time()
        if now - self._ps_cache["timestamp"] < DOCKER_CACHE_TTL:
            return self._ps_cache["data"]
        
        pid_to_container = {}
        id_to_name = {}
        
        if not self.is_available():
            self._ps_cache["data"] = (pid_to_container, id_to_name)
            self._ps_cache["timestamp"] = now
            return pid_to_container, id_to_name
        
        # Get container list
        success, output = run_docker_command(["ps", "--format", "{{.ID}} {{.Names}}"], timeout=DOCKER_TIMEOUT)
        if success:
            for line in output.splitlines():
                if line.strip():
                    parts = line.strip().split(" ", 1)
                    if len(parts) == 2:
                        cid, name = parts
                        id_to_name[cid] = name
            
            # Get PIDs for each container
            for cid in id_to_name.keys():
                success, pid_str = run_docker_command(["inspect", "--format", "{{.State.Pid}}", cid], timeout=5.0)
                if success and pid_str.isdigit():
                    host_pid = int(pid_str)
                    pid_to_container[host_pid] = (cid, id_to_name[cid])
        
        # Cache the result
        self._ps_cache["data"] = (pid_to_container, id_to_name)
        self._ps_cache["timestamp"] = now
        return pid_to_container, id_to_name
    
    def get_port_mappings(self) -> Dict[int, ContainerInfo]:
        """Get host port -> container mappings."""
        now = time.time()
        if now - self._port_cache["timestamp"] < DOCKER_CACHE_TTL:
            return self._port_cache["data"]
        
        mapping = {}
        if not self.is_available():
            self._port_cache["data"] = mapping
            self._port_cache["timestamp"] = now
            return mapping
        
        fmt = "{{.ID}}\\t{{.Names}}\\t{{.Image}}\\t{{.Ports}}\\t{{.Label \"com.docker.compose.project\"}}\\t{{.Label \"com.docker.compose.service\"}}"
        success, output = run_docker_command(["ps", "--format", fmt], timeout=DOCKER_TIMEOUT)
        
        if success:
            for line in output.splitlines():
                if not line.strip():
                    continue
                parts = line.split("\t")
                if len(parts) < 6:
                    parts += [""] * (6 - len(parts))
                
                cid, name, image, ports_str, comp_proj, comp_svc = parts[:6]
                
                # Parse port mappings
                for entry in [p.strip() for p in ports_str.split(",") if p.strip()]:
                    m = re.search(r"(?:(?P<ip>[\[\]a-fA-F0-9:.*]+):)?(?P<host>\d+)->(?P<cport>\d+/(?:tcp|udp))", entry)
                    if m:
                        host_port = int(m.group("host"))
                        host_ip = m.group("ip") or "*"
                        container_port = m.group("cport")
                        
                        mapping[host_port] = ContainerInfo(
                            id=cid,
                            name=name,
                            image=image,
                            container_port=container_port,
                            host_ip=host_ip,
                            compose_project=comp_proj or None,
                            compose_service=comp_svc or None
                        )
        
        # Cache the result
        self._port_cache["data"] = mapping
        self._port_cache["timestamp"] = now
        return mapping
    
    def get_container_by_port(self, port: int, protocol: str = "tcp") -> Optional[str]:
        """Get container name using a specific host port."""
        success, output = run_docker_command(
            ["ps", "--filter", f"publish={port}/{protocol}", "--format", "{{.Names}}"],
            timeout=5.0
        )
        if success:
            names = [line.strip() for line in output.splitlines() if line.strip()]
            return names[0] if names else None
        return None
    
    def stop_container(self, container: str, force: bool = False) -> Tuple[bool, str]:
        """Stop or remove a Docker container."""
        if force:
            # Disable restart policy first
            run_docker_command(["update", "--restart=no", container], timeout=5.0)
            return run_docker_command(["rm", "-f", container], timeout=DOCKER_TIMEOUT)
        else:
            return run_docker_command(["stop", container], timeout=DOCKER_TIMEOUT)
    
    def enrich_socket_with_container_info(self, socket) -> None:
        """Enrich a socket object with container information."""
        # Try cgroup detection first
        if socket.pid:
            cgroup_path = f"/proc/{socket.pid}/cgroup"
            if os.path.exists(cgroup_path):
                try:
                    with open(cgroup_path, "r") as f:
                        cgroup_content = f.read()
                    # Look for docker container ID
                    m = re.search(r'/docker[/-]([a-f0-9]{64})', cgroup_content)
                    if m:
                        cid = m.group(1)
                        socket.container_id = cid[:12]
                        _, id_to_name = self.get_pid_to_container_map()
                        socket.container_name = id_to_name.get(cid, id_to_name.get(cid[:12]))
                except (IOError, OSError):
                    pass
        
        # Fallback to PID mapping
        if socket.container_id is None and socket.pid:
            pid_to_container, _ = self.get_pid_to_container_map()
            if socket.pid in pid_to_container:
                cid, name = pid_to_container[socket.pid]
                socket.container_id = cid[:12]
                socket.container_name = name
        
        # Port mapping enrichment
        port_mappings = self.get_port_mappings()
        port_info = port_mappings.get(socket.local_port)
        if port_info:
            socket.container_host_ip = port_info.host_ip
            socket.container_port = port_info.container_port
            socket.container_image = port_info.image
            socket.compose_project = port_info.compose_project
            socket.compose_service = port_info.compose_service
            
            if socket.container_id is None:
                socket.container_id = port_info.id[:12] if port_info.id else None
            if socket.container_name is None:
                socket.container_name = port_info.name
        
        # Set process name from container info
        if socket.container_name and not socket.process_name:
            if socket.compose_service:
                socket.process_name = socket.compose_service
            elif socket.container_image:
                # Extract from image name (e.g., "redis:7-alpine" -> "redis")
                socket.process_name = socket.container_image.split(':')[0].split('/')[-1]
            elif any(name in socket.container_name.lower() for name in ['postgres', 'redis', 'nginx', 'apache']):
                name_map = {'postgres': 'postgres', 'redis': 'redis-server', 'nginx': 'nginx', 'apache': 'apache2'}
                for key, value in name_map.items():
                    if key in socket.container_name.lower():
                        socket.process_name = value
                        break
        
        # Set container user
        if socket.container_name and not socket.user_name:
            socket.user_name = 'docker'


# Global instance
docker_manager = DockerManager()