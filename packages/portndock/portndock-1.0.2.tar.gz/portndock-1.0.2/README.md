# portndock

A cross-platform terminal tool for developers to easily find and kill processes using ports. Perfect for fixing **"port already in use"** errors!

## Features

- **Find processes by port** - See what's using any port
- **Docker aware** - Handles containers intelligently  
- **Interactive TUI** - Color-coded safety levels
- **Related processes** - Find Electron renderers and background processes
- **Safe by default** - Warns about dangerous processes
- **Cross-platform** - Windows, macOS, Linux
- **Zero dependencies** - Pure Python

## Installation

```bash
# Recommended (handles environment isolation)
pipx install portndock

# Upgrade to latest version
pipx upgrade portndock

# Alternatives
pip install portndock --user
python3 -m venv env && source env/bin/activate && pip install portndock
```

## Local Development

```bash
# Clone the repository
git clone https://github.com/decentaro/portndock.git
cd portndock

# Run directly from source (no installation needed)
python3 -m portndock
# or with sudo for system processes
sudo python3 -m portndock ui

# Install in development mode (optional)
pip install -e .
```

## Usage

```bash
# Interactive mode (recommended)
portndock

# Command line
portndock kill --port 3000
portndock list
portndock free --port 8080
```

## Interactive Controls

- **↑/↓** - Navigate • **Enter** - Kill process • **D** - Stop container
- **V** - Filter ports • **P** - Filter protocols • **E** - Toggle related processes
- **X** - Toggle IPv6 • **?** - Help • **Q** - Quit

## Color Coding

- **Blue** - Docker containers (safe)
- **Green** - Your processes (safe)
- **Yellow** - System processes (careful) 
- **Red** - Critical processes (danger)

## Examples

```bash
portndock ui                   # Interactive TUI
portndock kill --port 3000     # Kill by port
portndock kill --pid 12345     # Kill by PID  
portndock list --protocol tcp  # List TCP only
portndock free --port 8080     # Free port (Docker-aware)
```

## Requirements

Python 3.8+ • No dependencies • Cross-platform

## License

MIT