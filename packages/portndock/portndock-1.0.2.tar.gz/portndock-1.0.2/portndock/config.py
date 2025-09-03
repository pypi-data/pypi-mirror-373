"""
Configuration constants for portndock.
"""

# Cache settings
DOCKER_CACHE_TTL = 5.0  # seconds

# Timeouts
DEFAULT_TIMEOUT = 5.0
DOCKER_TIMEOUT = 10.0
PROCESS_TIMEOUT = 3.0

# Development port ranges
DEV_PORTS = {
    'app': {3000, 3001, 3002, 8000, 8080, 8081, 9000, 9090, 4200, 5173},
    'database': {3306, 5432, 6379, 27017, 28017, 9200, 9300, 11211},
    'system': set(range(1, 1024))  # Privileged ports
}

# All stack ports (app + database)
DEV_PORTS['stack'] = DEV_PORTS['app'] | DEV_PORTS['database']

# Critical processes that should never be killed
CRITICAL_PROCESSES = {
    'systemd', 'init', 'kernel', 'kthreadd', 'launchd',
    'WindowServer', 'loginwindow', 'explorer.exe', 'dwm.exe', 
    'winlogon.exe', 'csrss.exe', 'svchost.exe'
}

# Project file indicators
PROJECT_FILES = [
    'package.json', 'Cargo.toml', 'go.mod', 'requirements.txt', 
    'setup.py', 'pyproject.toml', '.git', 'Makefile', 
    'docker-compose.yml', 'Dockerfile'
]

# UI settings
UI_REFRESH_INTERVAL = 2.0
UI_TIMEOUT_MS = 1000