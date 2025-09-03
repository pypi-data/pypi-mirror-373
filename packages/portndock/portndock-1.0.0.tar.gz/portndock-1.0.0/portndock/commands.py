"""
Command line interface implementations for portndock.
"""

import argparse
import sys
from typing import List, Tuple

from .core import ListeningSocket, find_pids_by_port, list_open_ports, print_table, is_dev_port, _is_port_free, enrich_with_docker_info
from .docker_manager import docker_manager
from .process_killer import process_killer, parse_signal
from .subprocess_utils import find_executable


def cmd_clean(args: argparse.Namespace) -> int:
    """Clean up processes related to the current project."""
    print("Project cleanup functionality temporarily disabled during refactoring")
    return 1


def cmd_free(args: argparse.Namespace) -> int:
    """Free a port by stopping its owner (process or container)."""
    port = args.port
    protocol = getattr(args, 'protocol', 'tcp')
    dry_run = getattr(args, 'dry_run', False)
    force = getattr(args, 'force', False)
    
    print(f"Attempting to free {protocol.upper()}/{port}...")
    
    # Check if port is already free
    if _is_port_free(port, protocol):
        print(f"Port {protocol}/{port} is already free")
        return 0
    
    # Check if container maps this port
    container_name = docker_manager.get_container_by_port(port, protocol)
    if container_name and docker_manager.is_available():
        print(f"Found Docker container '{container_name}' using port {port}")
        
        if dry_run:
            print(f"Would docker stop {container_name} (port {port})")
            return 0
        
        success, output = docker_manager.stop_container(container_name)
        if success:
            print(f"docker stop {container_name}")
        else:
            print(f"docker stop failed: {output}")
        
        # Check if port is now free
        if _is_port_free(port, protocol):
            print(f"Port {protocol}/{port} is now free")
            return 0
        else:
            print(f"Port {protocol}/{port} still busy after stopping container")
    
    # No container mapping; fallback to PID kill flow
    pids = find_pids_by_port(port, protocol)
    if not pids:
        print(f"No processes found using port {port}")
        return 1
    
    sig = parse_signal("KILL" if force else "TERM")
    
    success_count = 0
    for pid, process_name in pids:
        if pid is None:
            continue
        
        try:
            ok, msg = process_killer.kill_by_pid(pid, sig, dry_run=dry_run)
            
            if ok:
                action = "Would kill" if dry_run else "Killed"
                print(f"{action} PID {pid} ({process_name or 'unknown'})")
                success_count += 1
            else:
                print(f"Failed to kill PID {pid} ({process_name or 'unknown'}): {msg}")
        except Exception as e:
            print(f"Error killing PID {pid} ({process_name or 'unknown'}): {e}")
    
    if dry_run:
        print(f"\nDry run complete. Would attempt to kill {success_count}/{len(pids)} processes")
        return 0
    
    # Check if port is now free
    if success_count > 0:
        if _is_port_free(port, protocol):
            print(f"\nPort {protocol}/{port} is now free")
            return 0
        else:
            print(f"\nPort {protocol}/{port} may still be busy (check with 'portndock list')")
            return 1
    else:
        print(f"\nNo processes were killed")
        return 1


def cmd_list(args: argparse.Namespace) -> int:
    """List all listening processes."""
    protocol = getattr(args, 'protocol', 'all')
    dev_mode = getattr(args, 'dev', 'all')
    
    # Use early filtering for better performance
    sockets = list_open_ports(protocol, dev_mode)
    
    if not sockets:
        print("No listening processes found.")
        return 0
    
    enrich_with_docker_info(sockets)
    print_table(sockets)
    return 0


def cmd_kill(args: argparse.Namespace) -> int:
    """Kill process by PID or port."""
    if args.pid:
        # Kill by PID
        sig = parse_signal(getattr(args, 'signal', 'TERM'))
        ok, msg = process_killer.kill_by_pid(args.pid, sig, dry_run=getattr(args, 'dry_run', False))
        if ok:
            print(f"Killed PID {args.pid}")
            return 0
        else:
            print(f"Failed to kill PID {args.pid}: {msg}")
            return 1
    
    elif args.port:
        # Kill by port
        protocol = getattr(args, 'protocol', 'tcp')
        pids = find_pids_by_port(args.port, protocol)
        
        if not pids:
            print(f"No processes found on port {args.port}")
            return 1
        
        if len(pids) > 1 and not args.all and not args.interactive:
            print(
                "Multiple processes found on that port. Use --interactive to choose or --all to kill all.",
                file=sys.stderr,
            )
            return 1
        
        if args.interactive and len(pids) > 1:
            print("Multiple processes found:")
            for i, (pid, name) in enumerate(pids, 1):
                print(f"  {i}. PID {pid} ({name or 'unknown'})")
            
            try:
                choice = input("Select number to kill (or 'a' for all, 'q' to cancel): ").strip()
                if choice.lower() in ('q', 'quit', 'cancel'):
                    print("Cancelled")
                    return 0
                elif choice.lower() in ('a', 'all'):
                    selected_pids = pids
                else:
                    idx = int(choice) - 1
                    if 0 <= idx < len(pids):
                        selected_pids = [pids[idx]]
                    else:
                        print("Invalid selection")
                        return 1
            except (ValueError, KeyboardInterrupt, EOFError):
                print("Cancelled")
                return 1
        else:
            selected_pids = pids
        
        sig = parse_signal(getattr(args, 'signal', 'TERM'))
        success_count = 0
        
        for pid, name in selected_pids:
            if pid is None:
                continue
            ok, msg = process_killer.kill_by_pid(pid, sig, dry_run=getattr(args, 'dry_run', False))
            if ok:
                action = "Would kill" if getattr(args, 'dry_run', False) else "Killed"
                print(f"{action} PID {pid} ({name or 'unknown'})")
                success_count += 1
            else:
                print(f"Failed to kill PID {pid} ({name or 'unknown'}): {msg}")
        
        return 0 if success_count > 0 else 1
    
    else:
        print("Must specify either --pid or --port")
        return 1


def _format_indexed_table(rows: List[ListeningSocket]) -> str:
    """Format a table with row numbers for interactive selection."""
    if not rows:
        return "No processes found."
    
    headers = ["#", "PROTO", "PORT", "PID", "USER", "PROCESS", "CONTAINER"]
    
    # Prepare data
    data: List[List[str]] = []
    for idx, s in enumerate(rows, start=1):
        container = s.container_name or s.container_id or "-"
        data.append([
            str(idx),
            s.protocol,
            str(s.local_port),
            str(s.pid or "-"),
            s.user_name or "-",
            s.process_name or "-",
            container,
        ])
    
    # Calculate column widths
    all_rows = [headers] + data
    col_widths = [max(len(str(row[i])) for row in all_rows) for i in range(len(headers))]
    
    # Format output
    lines = []
    
    # Header
    header_row = "  ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    lines.append(header_row)
    lines.append("-" * len(header_row))
    
    # Data rows
    for row in data:
        data_row = "  ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(row)))
        lines.append(data_row)
    
    return "\n".join(lines)


def _parse_selection(selection: str, max_index: int) -> List[int]:
    """Parse user selection string into list of indices."""
    if selection.lower() in ('a', 'all'):
        return list(range(1, max_index + 1))
    
    indices = []
    for part in selection.split(','):
        part = part.strip()
        if '-' in part:
            # Range selection like "2-5"
            try:
                start_str, end_str = part.split('-', 1)
                start = int(start_str.strip())
                end = int(end_str.strip())
                indices.extend(range(start, end + 1))
            except ValueError:
                continue
        else:
            # Single number
            try:
                indices.append(int(part))
            except ValueError:
                continue
    
    # Filter valid indices
    return [i for i in indices if 1 <= i <= max_index]


def cmd_pick(args: argparse.Namespace) -> int:
    """Interactive picker to select processes to kill."""
    protocol = getattr(args, 'protocol', 'all')
    dev_mode = getattr(args, 'dev', 'all')
    
    sockets = list_open_ports(protocol, dev_mode)
    # Only sockets with a PID can be killed
    killable = [s for s in sorted(sockets, key=lambda x: (x.protocol, x.local_port, x.pid or 0)) if s.pid is not None]
    if not killable:
        print("No killable listening processes found. Try running with sudo.")
        return 0
    
    print(_format_indexed_table(killable))
    print()
    
    try:
        selection_input = input("Select number(s) to kill (e.g. 1,3-5; 'a' for all; 'q' to cancel): ").strip()
        if selection_input.lower() in ('q', 'quit', 'cancel', ''):
            print("Cancelled")
            return 0
        
        indices = _parse_selection(selection_input, len(killable))
        if not indices:
            print("No valid selection")
            return 0
        
        selected_processes = [killable[i - 1] for i in indices]
        
        # Show what will be killed
        print(f"\nWill kill {len(selected_processes)} processes:")
        for s in selected_processes:
            print(f"  PID {s.pid}: {s.process_name or 'unknown'} (port {s.local_port})")
        
        # Confirm unless --yes flag
        if not getattr(args, 'yes', False):
            confirm = input(f"\nProceed? [y/N]: ").strip().lower()
            if confirm not in ('y', 'yes'):
                print("Cancelled")
                return 0
        
        # Kill selected processes
        sig = parse_signal(getattr(args, 'signal', 'TERM'))
        success_count = 0
        
        for s in selected_processes:
            if s.pid is None:
                continue
            ok, msg = process_killer.kill_by_pid(s.pid, sig, dry_run=getattr(args, 'dry_run', False))
            if ok:
                action = "Would kill" if getattr(args, 'dry_run', False) else "Killed"
                print(f"{action} PID {s.pid} ({s.process_name or 'unknown'})")
                success_count += 1
            else:
                print(f"Failed to kill PID {s.pid} ({s.process_name or 'unknown'}): {msg}")
        
        if getattr(args, 'dry_run', False):
            print(f"\nDry run complete. Would kill {success_count}/{len(selected_processes)} processes")
        else:
            print(f"\nKilled {success_count}/{len(selected_processes)} processes")
        
        return 0
    
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled")
        return 0