"""
Docker-related utilities for portndock.
"""

import os
import re
import shutil
import subprocess
from typing import Dict, List, Optional, Tuple


def _docker_ps_map() -> Tuple[dict, dict]:
    """Return two maps: pid->(container_id, name) and container_id->name.

    Uses 'docker ps --format' and 'docker inspect'. If docker is unavailable or fails, returns empty maps.
    """
    pid_to_container: dict[int, Tuple[str, str]] = {}
    id_to_name: dict = {}

    docker = shutil.which("docker")
    if not docker:
        return pid_to_container, id_to_name

    try:
        cp = subprocess.run(
            [docker, "ps", "--format", "{{.ID}} {{.Names}}"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        container_lines = [ln.strip().split(" ", 1) for ln in cp.stdout.splitlines() if ln.strip()]
        for cid, name in container_lines:
            id_to_name[cid] = name
        # Try to map host PIDs for each container via 'docker inspect'
        for cid in id_to_name.keys():
            try:
                cp_inspect = subprocess.run(
                    [docker, "inspect", "--format", "{{.State.Pid}}", cid],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                host_pid_str = cp_inspect.stdout.strip()
                if host_pid_str.isdigit():
                    host_pid = int(host_pid_str)
                    pid_to_container[host_pid] = (cid, id_to_name.get(cid, cid))
            except subprocess.CalledProcessError:
                continue
    except subprocess.CalledProcessError:
        pass

    return pid_to_container, id_to_name


def _docker_host_port_map() -> dict:
    """Map host port -> container details using `docker ps`.

    Returns a dict like:
      { 3000: { 'id': 'abcd...', 'name': 'svc', 'image': 'repo/img:tag',
                'container_port': '3000/tcp', 'host_ip': '0.0.0.0',
                'compose_project': 'proj', 'compose_service': 'web' } }
    """
    docker = shutil.which("docker")
    if not docker:
        return {}
    fmt = "{{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Label \"com.docker.compose.project\"}}\t{{.Label \"com.docker.compose.service\"}}"
    try:
        cp = subprocess.run(
            [docker, "ps", "--format", fmt],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError:
        return {}
    mapping: dict[int, dict] = {}
    for line in cp.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 6:
            # pad missing labels
            parts += [""] * (6 - len(parts))
        cid, name, image, ports_str, comp_proj, comp_svc = parts[:6]
        ports_str = ports_str or ""
        # Parse entries separated by comma
        for entry in [p.strip() for p in ports_str.split(",") if p.strip()]:
            # Examples:
            # 0.0.0.0:8080->80/tcp, :::8080->80/tcp, 127.0.0.1:5432->5432/tcp
            m = re.search(r"(?:(?P<ip>[\[\]a-fA-F0-9:.*]+):)?(?P<host>\d+)->(?P<cport>\d+/(?:tcp|udp))", entry)
            if not m:
                continue
            host_port = int(m.group("host"))
            host_ip = m.group("ip") or "*"
            container_port = m.group("cport")
            mapping[host_port] = {
                "id": cid,
                "name": name,
                "image": image,
                "container_port": container_port,
                "host_ip": host_ip,
                "compose_project": comp_proj or None,
                "compose_service": comp_svc or None,
            }
    return mapping


def _docker_container_by_host_port(port: int, protocol: str = "tcp") -> Optional[str]:
    """Return container name if host port is mapped to a container."""
    docker = shutil.which("docker")
    if not docker:
        return None

    try:
        # Use docker ps filter publish for robust mapping
        filt = f"publish={port}/{protocol}"
        cp = subprocess.run(
            [docker, "ps", "--filter", filt, "--format", "{{.Names}}"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        names = [line.strip() for line in cp.stdout.splitlines() if line.strip()]
        return names[0] if names else None
    except subprocess.CalledProcessError:
        return None


def _docker_compose_base() -> Optional[List[str]]:
    """Return the base command for docker compose (either 'docker compose' or 'docker-compose')."""
    docker = shutil.which("docker")
    if docker:
        try:
            cp = subprocess.run([docker, "compose", "version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if cp.returncode == 0:
                return [docker, "compose"]
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    dc = shutil.which("docker-compose")
    return [dc] if dc else None


def _docker_disable_restart(container: str) -> None:
    """Disable restart policy for a container before stopping it."""
    docker = shutil.which("docker")
    if not docker:
        return
    try:
        subprocess.run([docker, "update", "--restart=no", container], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass


def _docker_stop_or_remove(container: str, force: bool) -> Tuple[bool, str]:
    """Stop or remove a Docker container."""
    docker = shutil.which("docker")
    if not docker:
        return False, "docker not found"
    
    try:
        if force:
            _docker_disable_restart(container)
            cp = subprocess.run([docker, "rm", "-f", container], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        else:
            cp = subprocess.run([docker, "stop", container], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        ok = cp.returncode == 0
        return ok, (cp.stdout.strip() or cp.stderr.strip() or ("stopped" if ok else "failed"))
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False, "docker command failed"


def _compose_file_in_dir(dir_path: str) -> Optional[str]:
    """Find a compose file in the given directory."""
    compose_files = [
        "docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"
    ]
    for cf in compose_files:
        full_path = os.path.join(dir_path, cf)
        if os.path.isfile(full_path):
            return full_path
    return None


def _find_compose_dir(start_path: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """Find docker-compose file by walking up from start_path."""
    if not start_path or not os.path.isdir(start_path):
        return None, None
    
    current = os.path.abspath(start_path)
    while True:
        compose_file = _compose_file_in_dir(current)
        if compose_file:
            return current, compose_file
        parent = os.path.dirname(current)
        if parent == current:  # Reached root
            break
        current = parent
    return None, None


def _docker_compose_service(project: Optional[str], service: Optional[str], force: bool, 
                          project_dir: Optional[str] = None, compose_file: Optional[str] = None) -> Tuple[bool, str]:
    """Stop a docker-compose service."""
    base = _docker_compose_base()
    if not base:
        return False, "docker-compose not found"
    
    cmd = base[:]
    
    if project_dir:
        # If docker compose (not legacy), we can pass --project-directory
        if len(base) > 1 and base[1] == "compose":
            cmd.extend(["--project-directory", project_dir])
        else:
            # Legacy docker-compose: pass -f compose_file if we have it
            if compose_file:
                cmd.extend(["-f", compose_file])
    
    if project:
        cmd.extend(["-p", project])
    
    if force:
        if service:
            cmd.extend(["rm", "-f", service])
        else:
            cmd.extend(["down", "--remove-orphans"])
    else:
        if service:
            cmd.extend(["stop", service])
        else:
            cmd.extend(["stop"])
    
    try:
        cp = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        ok = cp.returncode == 0
        output = cp.stdout.strip() or cp.stderr.strip() or ("success" if ok else "failed")
        return ok, output
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False, "docker-compose command failed"


def enrich_with_docker_info(sockets: List['ListeningSocket']) -> None:
    """Enrich socket objects with Docker container information."""
    from .core import ListeningSocket
    
    # Docker mapping (best effort)
    pid_to_container, id_to_name = _docker_ps_map()
    host_port_map = _docker_host_port_map()

    for s in sockets:
        # Container info via cgroup
        if s.pid:
            cgroup_path = f"/proc/{s.pid}/cgroup"
            if os.path.exists(cgroup_path):
                try:
                    with open(cgroup_path, "r") as f:
                        cgroup_content = f.read()
                    # Look for docker style container ID (64 hex) in the path
                    m = re.search(r'/docker[/-]([a-f0-9]{64})', cgroup_content)
                    if m:
                        cid = m.group(1)
                        s.container_id = cid[:12]
                        s.container_name = id_to_name.get(cid, id_to_name.get(cid[:12]))
                except (IOError, OSError):
                    pass
        
        # Fallback to docker inspect State.Pid mapping
        if s.container_id is None and s.pid in pid_to_container:
            cid, name = pid_to_container[s.pid]
            s.container_id = cid[:12]
            s.container_name = name
        
        # Host->container port mapping enrichment
        port_info = host_port_map.get(s.local_port)
        if port_info is not None:
            s.container_host_ip = port_info.get("host_ip")
            s.container_port = port_info.get("container_port")
            s.container_image = port_info.get("image")
            s.compose_project = port_info.get("compose_project")
            s.compose_service = port_info.get("compose_service")
            if s.container_id is None:
                s.container_id = (port_info.get("id") or "")[:12] or None
            if s.container_name is None:
                s.container_name = port_info.get("name")