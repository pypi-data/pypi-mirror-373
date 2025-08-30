"""
Formatting utilities for Spark Analyzer.

This module contains utility functions for formatting output,
error messages, and user interface elements.
"""
import sys
import textwrap
import os


def print_error_box(title: str, message: str, help_text: str = None):
    """Print an error message with rich formatting when available."""
    try:
        # Try to use rich if available
        from rich.console import Console
        from rich.panel import Panel
        
        console = Console()
        
        # Build the rich content
        content_parts = [f"[bold red]{title}[/bold red]", "", message]
        if help_text:
            content_parts.extend(["", "[bold]Help:[/bold]", help_text])
        
        content = "\n".join(content_parts)
        
        console.print(Panel(
            content,
            title="❌ Error",
            border_style="red"
        ))
    except ImportError:
        # Fallback to plain text if rich not available
        _print_plain_error_box(title, message, help_text)


def _print_plain_error_box(title: str, message: str, help_text: str = None):
    """Plain text fallback for error formatting."""
    # Replace special characters for compatibility
    message = str(message).replace("│", "|").replace("➤", "->")
    if help_text:
        help_text = str(help_text).replace("│", "|").replace("➤", "->")
    
    # Calculate box width based on terminal width, with a minimum of 65 (original fixed width)
    try:
        terminal_width = min(100, max(65, os.get_terminal_size().columns))
    except:
        terminal_width = 80

    # Format the title
    title = f" {title} ".center(terminal_width, "=")
    
    # Format the message with word wrap
    wrapped_message = textwrap.fill(message, width=terminal_width - 4)
    message_lines = wrapped_message.split('\n')
    message_box = []
    for line in message_lines:
        message_box.append(f"│ {line.ljust(terminal_width - 4)} │")
    
    # Format the help text if provided
    help_box = []
    if help_text:
        help_box.append("│" + "─" * (terminal_width - 2) + "│")
        help_box.append("│ Help:".ljust(terminal_width - 2) + "│")
        
        help_lines = help_text.split('\n')
        for line in help_lines:
            line = line.strip()
            if line:
                if line[0].isdigit() and '.' in line[:3]:
                    # For numbered lines, check if they need wrapping
                    if len(line) > terminal_width - 6:
                        # Wrap long numbered lines
                        wrapped_line = textwrap.fill(line, width=terminal_width - 6)
                        for wrapped_part in wrapped_line.split('\n'):
                            help_box.append(f"│   {wrapped_part.ljust(terminal_width - 6)} │")
                    else:
                        # Short numbered lines don't need wrapping
                        help_box.append(f"│   {line.ljust(terminal_width - 6)} │")
                else:
                    # For non-numbered lines, wrap them normally
                    wrapped_line = textwrap.fill(line, width=terminal_width - 6)
                    for wrapped_part in wrapped_line.split('\n'):
                        help_box.append(f"│   {wrapped_part.ljust(terminal_width - 6)} │")
    
    # Print the box
    print("\n" + "=" * terminal_width)
    print(title)
    print("=" * terminal_width)
    print("│" + " " * (terminal_width - 2) + "│")
    for line in message_box:
        print(line)
    print("│" + " " * (terminal_width - 2) + "│")
    for line in help_box:
        print(line)
    print("│" + " " * (terminal_width - 2) + "│")
    print("=" * terminal_width + "\n")
