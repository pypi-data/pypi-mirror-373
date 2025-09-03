"""
FINAL FIXED UI - Only redraws when absolutely necessary.
"""

import curses
import time
from typing import List, Optional

from .core import ListeningSocket, is_dev_port, list_open_ports, enrich_sockets_with_process_info, CRITICAL_PROCESS_DENYLIST, enrich_with_docker_info
from .docker_manager import docker_manager
from .process_killer import process_killer, parse_signal
from .config import UI_REFRESH_INTERVAL, UI_TIMEOUT_MS


def _cycle_protocol(proto: str) -> str:
    """Cycle through protocol filters."""
    order = ["all", "tcp", "udp"]
    try:
        i = order.index(proto.lower())
    except ValueError:
        i = 0
    return order[(i + 1) % len(order)]


def _get_process_color(socket: ListeningSocket) -> int:
    """Get color pair for a process based on its safety level."""
    if not curses.has_colors():
        return 0
        
    # Docker containers
    if socket.container_name:
        return curses.color_pair(3)  # Blue
        
    # Critical processes
    if socket.process_name and socket.process_name in CRITICAL_PROCESS_DENYLIST:
        return curses.color_pair(7)  # Red
        
    # User processes
    if socket.user_name and socket.user_name not in ('root', 'SYSTEM', r'NT AUTHORITY\SYSTEM'):
        return curses.color_pair(6)  # Green
        
    # System processes
    return curses.color_pair(2)  # Yellow


def draw_ui(stdscr, killable, selected_index, protocol, dev_mode, hide_ipv6, show_related, status_msg):
    """Draw the complete UI - only called when redraw is needed."""
    stdscr.erase()
    height, width = stdscr.getmaxyx()
    
    # Title and instructions
    title = "portndock - Kill processes using your ports"
    if curses.has_colors():
        stdscr.attron(curses.color_pair(4) | curses.A_BOLD)
    stdscr.addnstr(0, 0, title, width - 1)
    if curses.has_colors():
        stdscr.attroff(curses.color_pair(4) | curses.A_BOLD)
    
    instructions = "Use arrows to select - ENTER to kill process - ? for help - Q to quit"
    stdscr.addnstr(1, 0, instructions, width - 1)
    
    # Process count info with status
    if killable:
        ipv6_status = "IPv6 hidden" if hide_ipv6 else "IPv6 shown"
        related_status = "related shown" if show_related else "ports only"
        count_info = f"Found {len(killable)} processes - {protocol.upper()} - {dev_mode} filter - {ipv6_status} - {related_status}"
        if curses.has_colors():
            stdscr.attron(curses.color_pair(5))
        stdscr.addnstr(2, 0, count_info, width - 1)
        if curses.has_colors():
            stdscr.attroff(curses.color_pair(5))
    
    # Show status message if any
    if status_msg:
        if curses.has_colors():
            stdscr.attron(curses.color_pair(6))
        stdscr.addnstr(3, 0, status_msg, width - 1)
        if curses.has_colors():
            stdscr.attroff(curses.color_pair(6))
    
    # Headers
    headers = "PROTO  PORT    PID      USER     PROCESS                    CONTAINER"
    if curses.has_colors():
        stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
    stdscr.addnstr(4, 0, headers, width - 1)
    stdscr.addnstr(5, 0, "-" * min(len(headers), width - 1), width - 1)
    if curses.has_colors():
        stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
    
    # Data rows
    start_y = 6
    visible_count = min(len(killable), height - start_y - 3)
    
    for i in range(visible_count):
        s = killable[i]
        
        # Better container/service display
        container_bits = []
        if s.container_name:
            container_bits.append(s.container_name)
        if s.compose_service and s.compose_service != s.container_name:
            container_bits.append(f"({s.compose_service})")
        container_display = " ".join(container_bits) if container_bits else "-"
        
        # Enhanced process name
        proc_display = s.process_name or "-"
        if s.repo_name and s.process_name:
            proc_display = f"{s.process_name} ({s.repo_name})"
        
        # Format row
        port_display = str(s.local_port) if s.local_port > 0 else "-"
        row = f"{s.protocol:<6} {port_display:<7} {s.pid or '-':<8} {s.user_name or '-':<8} {proc_display:<26} {container_display}"
        
        y = start_y + i
        
        # Get process color
        process_color = _get_process_color(s)
        
        # Highlight selected row
        if i == selected_index:
            if curses.has_colors():
                stdscr.attron(curses.A_REVERSE)
            stdscr.addnstr(y, 0, row, width - 1)
            if curses.has_colors():
                stdscr.attroff(curses.A_REVERSE)
        else:
            if process_color and curses.has_colors():
                stdscr.attron(process_color)
            stdscr.addnstr(y, 0, row, width - 1)
            if process_color and curses.has_colors():
                stdscr.attroff(process_color)
    
    # Status lines
    if killable and selected_index < len(killable):
        s = killable[selected_index]
        details = f"Selected: {s.process_name or 'Unknown'} (PID {s.pid or 'N/A'}) on port {s.local_port}"
        if s.container_name:
            details += f" [Container: {s.container_name}]"
        stdscr.addnstr(height - 3, 0, details, width - 1)
        
        # Command line on separate line
        if s.cmdline:
            cmd_line = f"Command: {s.cmdline}"
            stdscr.addnstr(height - 2, 0, cmd_line, width - 1)
    
    stdscr.refresh()


def fixed_ui_loop(stdscr, args) -> int:
    """FIXED UI loop - only redraws when necessary."""
    
    # Basic setup
    try:
        curses.curs_set(0)
    except Exception:
        pass
        
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_WHITE, -1)
        curses.init_pair(2, curses.COLOR_YELLOW, -1)
        curses.init_pair(3, curses.COLOR_BLUE, -1)
        curses.init_pair(4, curses.COLOR_CYAN, -1)
        curses.init_pair(5, curses.COLOR_MAGENTA, -1)
        curses.init_pair(6, curses.COLOR_GREEN, -1)
        curses.init_pair(7, curses.COLOR_RED, -1)
    
    stdscr.nodelay(True)
    stdscr.timeout(UI_TIMEOUT_MS)
    
    selected_index = 0
    last_refresh = 0
    interval = float(getattr(args, "interval", UI_REFRESH_INTERVAL))
    protocol = getattr(args, "protocol", "all")
    dev_mode = getattr(args, "dev", "stack")
    hide_ipv6 = True
    show_related = False
    status_msg = ""
    
    killable = []
    need_redraw = True  # Start with initial draw
    
    # Show help screen on startup
    def show_help():
        stdscr.erase()
        help_lines = [
            "***********************************",
            "*    PORTNDOCK HELP GUIDE         *",
            "***********************************",
            "",
            "CONTROLS:",
            "  Up/Down arrows - Navigate up/down",
            "  ENTER          - Kill selected process", 
            "  P              - Cycle protocols (tcp/udp/all)",
            "  V              - Cycle dev filters (app/stack/all)",
            "  X              - Toggle IPv6 duplicates",
            "  E              - Toggle related processes (Electron renderers)",
            "  R              - Refresh process list",
            "  Q              - Quit portndock",
            "",
            "PROCESS TYPES (color coded):",
            "  Blue    - Docker containers (safe to kill)",
            "  Green   - Your user processes (usually safe)",
            "  Yellow  - System processes (be careful!)",
            "  Red     - Critical processes (dangerous!)",
            "",
            "Press ANY KEY to continue"
        ]
        
        height, width = stdscr.getmaxyx()
        for i, line in enumerate(help_lines):
            y = 2 + i
            if y >= height - 1:
                break
            x = 2
            if line.endswith(":"):
                if curses.has_colors():
                    stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
                stdscr.addnstr(y, x, line, width - x - 1)
                if curses.has_colors():
                    stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
            else:
                stdscr.addnstr(y, x, line, width - x - 1)
        
        stdscr.refresh()
        stdscr.nodelay(False)
        stdscr.getch()
        stdscr.nodelay(True)
    
    show_help()  # Show help on startup
    
    while True:
        now = time.time()
        
        # Refresh data every interval or on filter change
        if now - last_refresh >= interval or not killable or status_msg:
            sockets = list_open_ports(protocol, dev_mode, show_related)
            enrich_with_docker_info(sockets)
            enrich_sockets_with_process_info(sockets)
            
            # Handle IPv6 filtering
            if hide_ipv6:
                v4_ports = {s.local_port for s in sockets if s.local_ip == '0.0.0.0'}
                sockets = [s for s in sockets if not (s.local_ip == '::' and s.local_port in v4_ports)]
            
            killable = sorted(sockets, key=lambda s: (s.protocol, s.local_port, s.pid or 0))
            last_refresh = now
            
            if selected_index >= len(killable):
                selected_index = max(0, len(killable) - 1)
            
            need_redraw = True  # Data changed
        
        # CRITICAL: Only redraw when necessary!
        if need_redraw:
            draw_ui(stdscr, killable, selected_index, protocol, dev_mode, hide_ipv6, show_related, status_msg)
            status_msg = ""  # Clear after showing
            need_redraw = False
        
        # Handle input
        ch = stdscr.getch()
        
        # Skip loop if no input
        if ch == -1:
            continue
        
        if ch == ord('q') or ch == ord('Q'):
            return 0
            
        elif ch == curses.KEY_UP and selected_index > 0:
            selected_index -= 1
            # INSTANT navigation - bypass all flags and redraw immediately
            draw_ui(stdscr, killable, selected_index, protocol, dev_mode, hide_ipv6, show_related, "")
            
        elif ch == curses.KEY_DOWN and selected_index < len(killable) - 1:
            selected_index += 1
            # INSTANT navigation - bypass all flags and redraw immediately  
            draw_ui(stdscr, killable, selected_index, protocol, dev_mode, hide_ipv6, show_related, "")
            
        elif ch in (10, 13, curses.KEY_ENTER):  # ENTER key (LF, CR, or KEY_ENTER)
            if killable and selected_index < len(killable):
                s = killable[selected_index]
                
                # Show confirmation dialog
                stdscr.nodelay(False)  # Enable blocking input for confirmation
                try:
                    if s.pid and s.container_name:
                        # Both process and container
                        prompt = f"Kill PID {s.pid} ({s.process_name or 'unknown'}) or stop container {s.container_name}? [y/N]: "
                    elif s.pid:
                        # Process only
                        prompt = f"Kill PID {s.pid} ({s.process_name or 'unknown'}) on port {s.local_port}? [y/N]: "
                    elif s.container_name:
                        # Container only
                        prompt = f"Stop container {s.container_name} on port {s.local_port}? [y/N]: "
                    else:
                        status_msg = "No PID or container to kill"
                        need_redraw = True
                        stdscr.nodelay(True)
                        continue
                    
                    # Clear screen and show prompt
                    stdscr.erase()
                    stdscr.addstr(0, 0, "PORTNDOCK - KILL CONFIRMATION")
                    stdscr.addstr(2, 0, prompt)
                    stdscr.refresh()
                    
                    # Get user input
                    response = ""
                    while True:
                        ch_confirm = stdscr.getch()
                        if ch_confirm in (10, 13):  # ENTER
                            break
                        elif ch_confirm == 27:  # ESC
                            response = "n"
                            break
                        elif ch_confirm in (ord('y'), ord('Y')):
                            response = "y"
                            break
                        elif ch_confirm in (ord('n'), ord('N'), ord('q'), ord('Q')):
                            response = "n"
                            break
                    
                    if response.lower() == 'y':
                        # User confirmed - proceed with kill
                        if s.container_name:
                            # Stop Docker container (preferred for Docker processes)
                            try:
                                force = getattr(args, 'force', False)
                                success, output = docker_manager.stop_container(s.container_name, force)
                                if success:
                                    status_msg = f"Stopped container {s.container_name}"
                                    last_refresh = 0
                                else:
                                    status_msg = f"Failed to stop container: {output}"
                            except Exception as e:
                                status_msg = f"Error stopping container: {e}"
                        elif s.pid:
                            # Kill process (for non-container processes)
                            try:
                                sig = parse_signal(getattr(args, 'signal', 'TERM'))
                                success, msg = process_killer.kill_by_pid(s.pid, sig, dry_run=getattr(args, 'dry_run', False))
                                if success:
                                    status_msg = f"Killed PID {s.pid} ({s.process_name or 'unknown'})"
                                    last_refresh = 0
                                else:
                                    status_msg = f"Failed to kill PID {s.pid}: {msg}"
                            except Exception as e:
                                status_msg = f"Error killing PID {s.pid}: {e}"
                    else:
                        # User cancelled
                        status_msg = "Cancelled"
                    
                finally:
                    stdscr.nodelay(True)  # Restore non-blocking input
                    need_redraw = True
            
        elif ch in (ord('p'), ord('P')):
            protocol = _cycle_protocol(protocol)
            status_msg = f"Now showing {protocol.upper()} processes only"
            last_refresh = 0
            need_redraw = True
            
        elif ch in (ord('v'), ord('V')):
            dev_mode = 'stack' if dev_mode == 'app' else ('all' if dev_mode == 'stack' else 'app')
            if dev_mode == 'app':
                status_msg = "Showing app development ports (3000s, 8000s, etc.)"
            elif dev_mode == 'stack':
                status_msg = "Showing app + database ports (includes Redis, Postgres, etc.)"
            else:
                status_msg = "Showing ALL ports (including system services)"
            last_refresh = 0
            need_redraw = True
            
        elif ch in (ord('x'), ord('X')):
            hide_ipv6 = not hide_ipv6
            if hide_ipv6:
                status_msg = "Hiding IPv6 duplicates - cleaner view!"
            else:
                status_msg = "Showing all IPv6 entries"
            last_refresh = 0
            need_redraw = True
            
        elif ch in (ord('e'), ord('E')):
            show_related = not show_related
            if show_related:
                status_msg = "Showing related processes (like Electron renderers)!"
            else:
                status_msg = "Showing only port-listening processes"
            last_refresh = 0
            need_redraw = True
            
        elif ch in (ord('r'), ord('R')):
            status_msg = "Refreshed! Showing current processes"
            last_refresh = 0
            need_redraw = True
            
        elif ch == ord('?'):
            # Show help screen
            show_help()
            need_redraw = True


def cmd_ui(args) -> int:
    """Run the optimized TUI with instant navigation!"""
    try:
        return curses.wrapper(fixed_ui_loop, args)
    except KeyboardInterrupt:
        return 0
    except Exception as e:
        print(f"TUI error: {e}")
        return 1