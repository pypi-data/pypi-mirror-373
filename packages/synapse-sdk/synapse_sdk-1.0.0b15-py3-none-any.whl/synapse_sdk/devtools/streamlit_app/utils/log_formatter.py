"""Log formatting utilities."""

import html
import re


def format_log_line(line: str, line_number: int) -> str:
    """Format a log line with syntax highlighting and line numbers."""
    # Clean the line
    line = line.strip()
    if not line:
        return (
            f'<div class="log-line"><span class="log-line-number">{line_number}</span>'
            f'<div class="log-line-content"></div></div>'
        )

    # Escape HTML first
    line = html.escape(line)

    # Check for different log levels and patterns
    if re.search(r'\b(error|exception|fail|fatal)\b', line, re.IGNORECASE):
        css_class = 'log-error'
    elif re.search(r'\b(warn|warning)\b', line, re.IGNORECASE):
        css_class = 'log-warning'
    elif re.search(r'\b(info|information)\b', line, re.IGNORECASE):
        css_class = 'log-info'
    elif re.search(r'\b(debug|trace)\b', line, re.IGNORECASE):
        css_class = 'log-debug'
    else:
        css_class = ''

    # Highlight timestamps (common patterns)
    line = re.sub(r'(\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2})', r'<span class="log-timestamp">\1</span>', line)

    return (
        f'<div class="log-line"><span class="log-line-number">{line_number}</span>'
        f'<div class="log-line-content {css_class}">{line}</div></div>'
    )
