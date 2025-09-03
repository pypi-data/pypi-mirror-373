"""
Centralized subprocess utilities for portndock.
"""

import shutil
import subprocess
from typing import Tuple, List, Optional


def run_command(cmd: List[str], timeout: float = 5.0, capture_output: bool = True) -> Tuple[bool, str, str]:
    """Run a command and return (success, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        return False, "", str(e)


def run_docker_command(args: List[str], timeout: float = 10.0) -> Tuple[bool, str]:
    """Run a docker command and return (success, output)."""
    docker = shutil.which("docker")
    if not docker:
        return False, "docker not found"
    
    success, stdout, stderr = run_command([docker] + args, timeout=timeout)
    output = stdout or stderr or ("success" if success else "failed")
    return success, output


def run_system_command(args: List[str], shell: bool = False, timeout: float = 10.0) -> subprocess.CompletedProcess:
    """Run a system command with standard options."""
    return subprocess.run(
        args,
        shell=shell,
        capture_output=True,
        text=True,
        timeout=timeout
    )


def find_executable(name: str) -> Optional[str]:
    """Find an executable in PATH."""
    return shutil.which(name)


def is_docker_available() -> bool:
    """Check if Docker is available and running."""
    docker = find_executable("docker")
    if not docker:
        return False
    
    success, _, _ = run_command([docker, "version"], timeout=3.0)
    return success