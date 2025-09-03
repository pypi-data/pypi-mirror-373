"""
Main entry point and argument parser for portndock.
"""

import argparse
import sys
from typing import List, Optional

from .commands import cmd_clean, cmd_free, cmd_list, cmd_kill, cmd_pick
from .ui import cmd_ui


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for portndock."""
    parser = argparse.ArgumentParser(
        prog="portndock",
        description="Dev-focused port watcher/killer with Docker awareness and live TUI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  portndock ui                    # Interactive TUI (recommended)
  portndock list                  # List all listening processes  
  portndock kill --port 3000      # Kill process on port 3000
  portndock free --port 8080      # Free port 8080 (container-aware)
  portndock clean                 # Clean project processes
  portndock pick                  # Interactive process picker
  
For more help: https://github.com/decentaro/portndock
        """,
    )

    # Global options
    parser.add_argument(
        "--version",
        action="version", 
        version="portndock 1.0.0"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Clean command
    p_clean = subparsers.add_parser("clean", help="Clean up project-related processes")
    p_clean.add_argument(
        "--force",
        action="store_true",
        help="Use SIGKILL instead of SIGTERM",
    )
    p_clean.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not actually stop/kill; just print actions",
    )
    p_clean.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Skip confirmation prompt"
    )
    p_clean.set_defaults(func=cmd_clean)

    # Free command  
    p_free = subparsers.add_parser("free", help="Free a port by stopping its owner (proc or container)")
    p_free.add_argument("--port", type=int, required=True, help="Port to free")
    p_free.add_argument(
        "--protocol",
        choices=["tcp", "udp"],
        default="tcp",
        help="Protocol (default: tcp)",
    )
    p_free.add_argument(
        "--force",
        action="store_true", 
        help="Use SIGKILL instead of SIGTERM for processes",
    )
    p_free.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be killed without actually doing it"
    )
    p_free.set_defaults(func=cmd_free)

    # Interactive picker to select processes to kill
    p_pick = subparsers.add_parser("pick", help="Interactively select listening processes to kill")
    p_pick.add_argument(
        "--protocol",
        choices=["tcp", "udp", "all"],
        default="all",
        help="Protocol filter (default: all)",
    )
    p_pick.add_argument(
        "--dev",
        choices=["app", "stack", "all"],
        default="stack",
        help="Development port filter (default: stack)",
    )
    p_pick.add_argument(
        "--signal",
        default="TERM",
        help="Signal to send (default: TERM)",
    )
    p_pick.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not actually kill, just print actions",
    )
    p_pick.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Do not prompt for confirmation before killing",
    )
    p_pick.set_defaults(func=cmd_pick)

    # List command
    p_list = subparsers.add_parser("list", help="List all listening processes")
    p_list.add_argument(
        "--protocol",
        choices=["tcp", "udp", "all"],
        default="all",
        help="Protocol filter (default: all)",
    )
    p_list.add_argument(
        "--dev", 
        choices=["app", "stack", "all"],
        default="all",
        help="Development port filter (default: all)"
    )
    p_list.set_defaults(func=cmd_list)

    # Kill command
    p_kill = subparsers.add_parser("kill", help="Kill process by PID or port")
    p_kill.add_argument("--pid", type=int, help="PID to kill")
    p_kill.add_argument("--port", type=int, help="Port to find and kill its owner")
    p_kill.add_argument(
        "--protocol",
        choices=["tcp", "udp"],
        default="tcp",
        help="Protocol when killing by port (default: tcp)",
    )
    p_kill.add_argument(
        "--signal",
        default="TERM",
        help="Signal to send for kills (e.g. TERM, KILL, 9)",
    )
    p_kill.add_argument(
        "--all",
        action="store_true",
        help="When killing by --port, kill all matching PIDs",
    )
    p_kill.add_argument(
        "--interactive",
        action="store_true",
        help="Interactively choose which PID to kill if multiple",
    )
    p_kill.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not actually kill, just print actions",
    )
    p_kill.set_defaults(func=cmd_kill)

    # UI command (default when no subcommand)
    p_ui = subparsers.add_parser("ui", help="Interactive TUI that auto-refreshes and allows killing with Enter")
    p_ui.add_argument(
        "--protocol",
        choices=["tcp", "udp", "all"],
        default="all",
        help="Protocol filter (default: all)",
    )
    p_ui.add_argument(
        "--dev",
        choices=["app", "stack", "all"],
        default="stack",
        help="Development port filter: app=3000s,8000s; stack=+databases; all=everything (default: stack)",
    )
    p_ui.add_argument(
        "--interval",
        type=float,
        default=2.0,
        help="Refresh interval in seconds (default: 2.0)",
    )
    p_ui.add_argument(
        "--signal",
        default="TERM",
        help="Signal to send for kills (e.g. TERM, KILL, 9)",
    )
    p_ui.add_argument(
        "--force",
        action="store_true",
        help="Use SIGKILL by default instead of SIGTERM",
    )
    p_ui.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not actually kill, just show actions",
    )
    p_ui.set_defaults(func=cmd_ui)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for portndock."""
    parser = build_parser()
    
    # If no arguments provided, default to UI mode
    if not argv:
        argv = sys.argv[1:]
    
    if not argv:
        argv = ["ui"]
    
    args = parser.parse_args(argv)
    
    if hasattr(args, 'func'):
        try:
            return args.func(args)
        except KeyboardInterrupt:
            print("\nInterrupted", file=sys.stderr)
            return 130
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())