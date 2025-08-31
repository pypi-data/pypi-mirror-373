"""
Terminal User Interface (TUI) for portndock.
"""

import curses
import time
from typing import List, Optional

from .core import ListeningSocket, is_dev_port, list_open_ports, CRITICAL_PROCESS_DENYLIST
from .docker_utils import enrich_with_docker_info, _docker_stop_or_remove
from .process_utils import kill_pid, parse_signal


def _truncate(text: str, max_len: int) -> str:
    """Smart text truncation."""
    if len(text) <= max_len:
        return text
    if max_len <= 3:
        return text[:max_len]
    
    # Smart truncation for common patterns
    if "-" in text and max_len >= 8:
        # For names like "systemd-resolve", keep both parts if possible
        parts = text.split("-")
        if len(parts) == 2:
            first, second = parts
            if len(first) + len(second) + 1 <= max_len - 1:
                return text[: max_len - 1] + "…"
            # Try to keep meaningful parts
            if len(first) <= 6 and len(second) > 6:
                return first + "-" + second[: max_len - len(first) - 2] + "…"
    
    return text[: max_len - 1] + "…"


def _cycle_protocol(proto: str) -> str:
    """Cycle through protocol filters."""
    order = ["all", "tcp", "udp"]
    try:
        i = order.index(proto.lower())
    except ValueError:
        i = 0
    return order[(i + 1) % len(order)]


def _show_help_overlay(stdscr: "curses._CursesWindow", protocol: str, dev_mode: str) -> None:
    """Show a helpful overlay with all available commands."""
    height, width = stdscr.getmaxyx()
    
    help_text = [
        "***********************************",
        "*    PORTNDOCK HELP GUIDE         *",
        "***********************************",
        "",
        "CONTROLS:",
        "  Up/Down arrows - Navigate up/down",
        "  ENTER          - Kill selected process", 
        "  D              - Stop Docker container",
        "  R              - Refresh process list",
        "  Q              - Quit portndock",
        "",
        "PROCESS TYPES (color coded):",
        "  Blue    - Docker containers (safe to kill)",
        "  Green   - Your user processes (usually safe)",
        "  Yellow  - System processes (be careful!)",
        "  Red     - Critical processes (dangerous!)",
        "",
        "QUICK TIPS:",
        "  V = cycle filters, P = protocols, X = IPv6 toggle",
        "",
        "",
        "Press ANY KEY to continue"
    ]
    
    try:
        # Clear screen and show help
        stdscr.erase()
        
        # Start from top with some padding, don't center vertically
        start_y = 2
        
        for i, line in enumerate(help_text):
            y = start_y + i
            if y >= height - 1:
                break
                
            # Left-align all text
            x = 2
            
            # Simple title display without special colors
            if i == 0:  # Title
                stdscr.addnstr(y, x, line, width - x - 1)
            elif line.endswith(":"):  # Section headers
                if curses.has_colors():
                    stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
                stdscr.addnstr(y, x, line, width - x - 1)
                if curses.has_colors():
                    stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
            else:
                stdscr.addnstr(y, x, line, width - x - 1)
        
        stdscr.refresh()
        
        # Wait for any key
        stdscr.nodelay(False)
        stdscr.timeout(-1)
        stdscr.getch()
        
    except Exception:
        pass
    finally:
        # Restore normal mode
        stdscr.nodelay(True)
        stdscr.timeout(1000)


def _init_colors():
    """Initialize color pairs for the TUI."""
    if not curses.has_colors():
        return
    
    curses.start_color()
    curses.use_default_colors()
    
    # Color pairs
    curses.init_pair(1, curses.COLOR_WHITE, -1)    # Default text
    curses.init_pair(2, curses.COLOR_YELLOW, -1)   # Headers
    curses.init_pair(3, curses.COLOR_BLUE, -1)     # Docker containers
    curses.init_pair(4, curses.COLOR_CYAN, -1)     # Title
    curses.init_pair(5, curses.COLOR_MAGENTA, -1)  # Meta info
    curses.init_pair(6, curses.COLOR_GREEN, -1)    # User processes
    curses.init_pair(7, curses.COLOR_RED, -1)      # Critical/dangerous


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
    if socket.user_name and socket.user_name not in ('root', 'SYSTEM', 'NT AUTHORITY\\SYSTEM'):
        return curses.color_pair(6)  # Green
        
    # System processes
    return curses.color_pair(2)  # Yellow


def _draw_ui(
    stdscr: "curses._CursesWindow",
    killable: List[ListeningSocket],
    selected_index: int,
    protocol: str,
    sig_label: str,
    force: bool,
    interval: float,
    status: str,
    details_line: str,
    is_container_row: bool = False,
    show_help: bool = False,
) -> None:
    """Draw the main TUI interface."""
    height, width = stdscr.getmaxyx()
    stdscr.erase()

    # Initialize colors
    _init_colors()
    
    # Simple, friendly header
    title = "portndock"
    subtitle = "Kill processes using your ports"
    
    # Use colors if available
    header_color = curses.color_pair(4) if curses.has_colors() else 0
    
    help_lines = [
        "Use arrows to select - ENTER to kill process - ? for help - Q to quit",
    ]
    try:
        # Left-aligned title with better formatting
        title_line = f"{title} - {subtitle}"
        if curses.has_colors():
            stdscr.attron(header_color | curses.A_BOLD)
        stdscr.addnstr(0, 0, title_line, min(len(title_line), width - 1))
        if curses.has_colors():
            stdscr.attroff(header_color | curses.A_BOLD)
        
        # Right-aligned process count info
        process_count = len(killable)
        if process_count > 0:
            count_text = f"Found {process_count} processes"
            if width > len(count_text) + 5:
                try:
                    stdscr.addnstr(0, width - len(count_text), count_text, len(count_text))
                except:
                    pass
    except Exception:
        pass

    # Clean table headers
    headers = [
        "PROTO",
        "PORT", 
        "PID",
        "USER",
        "PROC",
        "IP",
        "CONTAINER",
    ]
    # Realistic column widths for actual terminal sizes
    if width <= 80:
        # Standard 80-char terminal - no icons so more space
        base_widths = [5, 4, 6, 6, 8, 10, 12]  # Total: 51 chars
    elif width < 120:
        # Medium terminal
        base_widths = [5, 5, 6, 6, 8, 8, 12]
    else:
        # Wide terminal
        base_widths = [6, 5, 8, 8, 12, 12, 20]
    
    # Much more generous spacing between columns
    spaces_between = 3  # 3 spaces between each column
    fixed = sum(base_widths)
    separators = spaces_between * (len(base_widths) - 1)
    total_used = fixed + separators
    
    # Only use remaining space if we have plenty left
    remainder = max(0, width - total_used - 10)  # Leave 10 chars buffer
    if remainder > 15:
        # Give extra space to CONTAINER column (last one)
        col_widths = base_widths[:-1] + [base_widths[-1] + min(remainder, 15)]
    else:
        col_widths = base_widths
    # compute header line
    def fmt_cells(cells: List[str]) -> str:
        parts: List[str] = []
        # Column alignment: PROTO, PORT(right), PID(right), USER, PROC, IP, CONTAINER
        alignments = ['left', 'right', 'right', 'left', 'left', 'left', 'left']
        
        for i, cell in enumerate(cells):
            # Ensure we never exceed column width
            truncated = _truncate(str(cell), col_widths[i])
            
            # Apply alignment and pad to exact column width
            if i < len(alignments) and alignments[i] == 'right':
                formatted = truncated.rjust(col_widths[i])[:col_widths[i]]
            else:
                formatted = truncated.ljust(col_widths[i])[:col_widths[i]]
            parts.append(formatted)
        
        full_row = ("   ").join(parts)  # 3 spaces between columns
        # Hard limit: never exceed terminal width
        return _truncate(full_row, width - 2)

    # Adjust spacing for clean layout
    top_section_rows = 2 if show_help else 1  # title/count on same line, help on next
    # Ensure proper spacing for headers to be visible
    meta_y = top_section_rows + 1
    table_y = meta_y + 2  # Need space between meta and table headers
    header_line = fmt_cells(headers)
    try:
        # Left-aligned meta info - clean and simple
        meta_simple = f"{protocol.upper()} ports - {getattr(_draw_ui, 'dev_mode_label', 'stack')} filter"
        if curses.has_colors():
            stdscr.attron(curses.color_pair(5))
        stdscr.addnstr(meta_y, 0, meta_simple, width - 1)
        if curses.has_colors():
            stdscr.attroff(curses.color_pair(5))
        
        # Table header
        if curses.has_colors():
            stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
        stdscr.addstr(table_y, 0, header_line)
        if curses.has_colors():
            stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
        
        # Simple separator line that respects terminal width
        separator_line = "-" * min(len(header_line), width - 1)
        if curses.has_colors():
            stdscr.attron(curses.color_pair(3))
        stdscr.addnstr(table_y + 1, 0, separator_line, width - 1)
        if curses.has_colors():
            stdscr.attroff(curses.color_pair(3))
    except Exception as e:
        try:
            stdscr.addstr(table_y + 3, 0, f"HEADER ERROR: {e}")
        except:
            pass

    # Table body
    body_start = table_y + 2
    max_rows = max(1, height - body_start - 4)  # Reserve space for details and status

    # Handle IPv6 filtering
    ipv6_hidden_flag = getattr(_draw_ui, 'hide_ipv6', False)
    if ipv6_hidden_flag:
        # Hide IPv6 duplicates - if both v4 (0.0.0.0) and v6 (::) exist, show only v4
        v4_ports = {s.local_port for s in killable if s.local_ip == '0.0.0.0'}
        visible = [s for s in killable if not (s.local_ip == '::' and s.local_port in v4_ports)][:max_rows]
    else:
        visible = killable[:max_rows]
    for idx, s in enumerate(visible):
        is_sel = (idx == selected_index)
        
        # Simple protocol without icons
        proc_type = s.protocol
        
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
        
        row_data = [
            proc_type,  # Use the icon-enhanced protocol
            str(s.local_port),
            str(s.pid or "-"),
            s.user_name or "-",
            proc_display,
            s.local_ip,
            container_display,
        ]
        
        row = fmt_cells(row_data)
        
        try:
            # Get process-specific color
            process_color = _get_process_color(s)
            
            y = body_start + idx
            if y >= height - 3:
                break
                
            # Highlight selected row
            if is_sel:
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
        except Exception:
            pass

    # Details line (process info)
    if details_line:
        try:
            last_row_y = body_start + max(0, len(visible) - 1)
            details_y = min(height - 3, last_row_y + 3)
            stdscr.addnstr(details_y, 0, _truncate(details_line, width - 1), width - 1)
        except Exception:
            pass
    # Status placed just below details with better formatting
    if status:
        try:
            status_y = height - 2
            
            # Color status messages based on content
            status_color = None
            if curses.has_colors():
                if "error" in status.lower() or "failed" in status.lower() or "not found" in status.lower():
                    status_color = curses.color_pair(7)  # Red for errors
                elif "killed" in status.lower() or "stopped" in status.lower():
                    status_color = curses.color_pair(6)  # Green for success
                else:
                    status_color = curses.color_pair(2)  # Green for success
            
            if status_color:
                stdscr.attron(status_color | curses.A_BOLD)
            formatted_status = status
            stdscr.addnstr(status_y, 0, _truncate(formatted_status, width - 1), width - 1)
            if status_color:
                stdscr.attroff(status_color | curses.A_BOLD)
        except Exception:
            pass

    stdscr.refresh()


def _ui_loop(stdscr: "curses._CursesWindow", args) -> int:
    """Main UI loop."""
    try:
        curses.curs_set(0)
    except Exception:
        pass
    interval = float(getattr(args, "interval", 1.0))
    stdscr.nodelay(True)
    stdscr.timeout(int(interval * 1000))

    protocol = getattr(args, "protocol", "all")
    dev_mode = getattr(args, "dev", "stack")
    force = bool(getattr(args, "force", False))
    signal_str = getattr(args, "signal", "TERM")
    sig = parse_signal("KILL" if force else signal_str)
    sig_label = signal_str if not force else "KILL"

    selected_index = 0
    status = ""
    killable: List[ListeningSocket] = []
    last_refresh = 0.0
    # Simple action history (max 50 entries)
    action_history: List[str] = []

    group_by_project = False
    show_history = False
    # Default: hide IPv6 duplicates on first draw
    setattr(_draw_ui, 'hide_ipv6', True)
    setattr(_draw_ui, 'ipv6_label', 'hidden')

    # Show help guide on startup
    _show_help_overlay(stdscr, protocol, dev_mode)

    while True:
        now = time.time()
        need_refresh = now - last_refresh >= interval or not killable
        if need_refresh:
            sockets = [s for s in list_open_ports(protocol) if is_dev_port(s.local_port, dev_mode)]
            
            # Enrich with additional metadata
            enrich_with_docker_info(sockets)
            
            sort_key = lambda s: (s.protocol, s.local_port, s.pid or 0)
            killable = [s for s in sorted(sockets, key=sort_key) if s.pid is not None]
            last_refresh = now
            if selected_index >= len(killable):
                selected_index = max(0, len(killable) - 1)

        details_line = ""
        if killable:
            s = killable[selected_index]
            container_bits = [s.container_name or s.container_id, s.compose_service, s.compose_project]
            container_bits = [b for b in container_bits if b]
            container_label = "/".join(container_bits) if container_bits else "-"

            details_parts = []
            if s.user_name:
                details_parts.append(f"User: {s.user_name}")
            if s.repo_name:
                details_parts.append(f"Project: {s.repo_name}")
            if s.container_name:
                details_parts.append(f"Container: {s.container_name}")
            if s.cmdline:
                cmd_short = _truncate(s.cmdline, 60)
                details_parts.append(f"Command: {cmd_short}")
            
            details_line = " | ".join(details_parts) if details_parts else "No additional info available"

        # If history panel requested, replace details line with last few actions
        details_line_final = details_line
        if show_history and action_history:
            recent_actions = action_history[-5:]  # Last 5 actions
            details_line_final = "Recent: " + " → ".join(recent_actions)

        # Store dev_mode for display
        setattr(_draw_ui, 'dev_mode_label', dev_mode)

        # pass dev label for meta line and container/process mode
        is_container_row = False
        if killable:
            s = killable[selected_index]
            is_container_row = bool(s.container_name)
        _draw_ui(stdscr, killable, selected_index, protocol, sig_label, force, interval, status, details_line_final, is_container_row)
        status = ""

        ch = stdscr.getch()
        
        if ch in (ord('q'), ord('Q')):
            return 0
        if ch in (curses.KEY_UP, ord('k'), ord('K')):
            if selected_index > 0:
                selected_index -= 1
            continue
        if ch in (curses.KEY_DOWN, ord('j'), ord('J')):
            if selected_index < max(0, len(killable) - 1):
                selected_index += 1
            continue
        if ch in (curses.KEY_HOME, ord('g')):
            # Go to top
            selected_index = 0
            continue
        if ch in (curses.KEY_END, ord('G')):
            # Go to bottom
            selected_index = max(0, len(killable) - 1)
            continue
        if ch in (curses.KEY_NPAGE,):  # Page Down
            selected_index = min(len(killable) - 1, selected_index + 10)
            continue
        if ch in (curses.KEY_PPAGE,):  # Page Up
            selected_index = max(0, selected_index - 10)
            continue
        if ch in (ord('?'),):
            # Show help overlay
            _show_help_overlay(stdscr, protocol, dev_mode)
            continue
        if ch in (ord('p'), ord('P')):
            protocol = _cycle_protocol(protocol)
            last_refresh = 0.0
            status = f"Now showing {protocol.upper()} processes only"
            continue
        if ch in (ord('v'), ord('V')):
            # cycle dev filter: app -> stack -> all
            dev_mode = 'stack' if dev_mode == 'app' else ('all' if dev_mode == 'stack' else 'app')
            last_refresh = 0.0
            if dev_mode == 'app':
                status = "Showing app development ports (3000s, 8000s, etc.)"
            elif dev_mode == 'stack':
                status = "Showing app + database ports (includes Redis, Postgres, etc.)"
            else:
                status = "Showing ALL ports (including system services)"
            continue
        if ch in (ord('x'), ord('X')):
            # toggle IPv6 duplicates
            current = getattr(_draw_ui, 'hide_ipv6', False)
            setattr(_draw_ui, 'hide_ipv6', not current)
            setattr(_draw_ui, 'ipv6_label', 'hidden' if not current else 'shown')
            last_refresh = 0.0
            if not current:
                status = "Hiding IPv6 duplicates - cleaner view!"
            else:
                status = "Showing all IPv6 entries again"
            continue
        if ch in (ord('d'), ord('D')):
            # docker stop container
            s = killable[selected_index] if killable else None
            if s and s.container_name:
                try:
                    success, msg = _docker_stop_or_remove(s.container_name, force=False)
                    if success:
                        status = f"Container stopped: {s.container_name} (port {s.local_port} freed)"
                        action_history.append(f"STOP {s.container_name}")
                        if len(action_history) > 50:
                            action_history.pop(0)
                        last_refresh = 0.0
                    else:
                        status = f"Docker stop failed: {msg}"
                except Exception as e:
                    status = f"Docker stop failed: {str(e)}"
            else:
                status = "No container to stop"
            continue
        if ch in (ord('r'), ord('R')):
            last_refresh = 0.0
            status = "Refreshed! Showing current processes"
            continue
        if ch in (10, 13, curses.KEY_ENTER):  # Enter to kill/stop selected
            if not killable:
                status = "Nothing to kill - no processes selected"
                continue
            s = killable[selected_index]
            
            # Enhanced confirmation with better context
            height, width = stdscr.getmaxyx()
            
            # Different prompts for containers vs processes
            if s.container_name:
                action = "stop container" if not force else "remove container"
                target = f"{s.container_name} (port {s.local_port})"
            else:
                action = f"send SIG{sig_label} to"
                target = f"PID {s.pid} ({s.process_name or 'unknown'})"
            
            # Check if this is a dangerous process
            danger = (s.process_name and s.process_name in CRITICAL_PROCESS_DENYLIST) or s.user_name == "root"
            
            try:
                if danger:
                    prompt = f"DANGER! This is a system process! Really {action} {target}? Type 'YES':"
                else:
                    prompt = f"{action.title()} {target}? Press 'y' to confirm:"
                
                # Show prompt at bottom
                stdscr.move(height - 1, 0)
                stdscr.clrtoeol()
                prompt_color = curses.color_pair(7) if danger and curses.has_colors() else 0
                if prompt_color:
                    stdscr.attron(prompt_color)
                stdscr.addnstr(height - 1, 0, _truncate(prompt, width - 1), width - 1)
                if prompt_color:
                    stdscr.attroff(prompt_color)
                stdscr.refresh()
                
                # Get confirmation
                stdscr.nodelay(False)
                stdscr.timeout(-1)
                
                if danger:
                    # For dangerous processes, require typing "YES"
                    response = ""
                    while True:
                        ch2 = stdscr.getch()
                        if ch2 in (27, ord('q'), ord('Q')):  # ESC or Q
                            break
                        elif ch2 == 10 or ch2 == 13:  # Enter
                            break
                        elif ch2 == 127 or ch2 == curses.KEY_BACKSPACE:  # Backspace
                            response = response[:-1]
                        elif 32 <= ch2 <= 126:  # Printable characters
                            response += chr(ch2)
                        
                        # Update prompt with current response
                        stdscr.move(height - 1, 0)
                        stdscr.clrtoeol()
                        display_prompt = f"{prompt} {response}"
                        stdscr.addnstr(height - 1, 0, _truncate(display_prompt, width - 1), width - 1)
                        stdscr.refresh()
                    
                    if response.upper() != "YES":
                        status = "Cancelled - process not killed"
                        stdscr.nodelay(True)
                        stdscr.timeout(int(interval * 1000))
                        continue
                else:
                    # For normal processes, just press 'y'
                    ans = stdscr.getch()
                    if ans not in (ord('y'), ord('Y')):
                        status = "Cancelled - process not killed"
                        stdscr.nodelay(True)
                        stdscr.timeout(int(interval * 1000))
                        continue
                
                stdscr.nodelay(True)
                stdscr.timeout(int(interval * 1000))
                
                # Perform the kill/stop
                # Simple rule: if this is a container row, do exactly what [D] does (stop/remove container).
                # Otherwise, send OS signal to the PID.
                if s.container_name:
                    ok, msg = _docker_stop_or_remove(s.container_name, force=(sig_label == "KILL"))
                else:
                    if s.pid is not None:
                        ok, msg = kill_pid(s.pid, sig, dry_run=getattr(args, 'dry_run', False))
                    else:
                        ok, msg = False, "No PID (non-container)"
                
                if ok:
                    if s.container_name:
                        status = f"Container {action}ped: {s.container_name}"
                        action_history.append(f"STOP {s.container_name}")
                    else:
                        status = f"Killed PID {s.pid} ({s.process_name or 'unknown'})"
                        action_history.append(f"KILL {s.pid}")
                    
                    if len(action_history) > 50:
                        action_history.pop(0)
                    last_refresh = 0.0
                else:
                    status = f"Failed: {msg}"
            
            except Exception as e:
                status = f"Error: {e}"
                stdscr.nodelay(True)
                stdscr.timeout(int(interval * 1000))
            
            continue


def cmd_ui(args) -> int:
    """Run the interactive TUI."""
    try:
        return curses.wrapper(_ui_loop, args)
    except KeyboardInterrupt:
        return 0
    except Exception as e:
        print(f"TUI error: {e}")
        return 1