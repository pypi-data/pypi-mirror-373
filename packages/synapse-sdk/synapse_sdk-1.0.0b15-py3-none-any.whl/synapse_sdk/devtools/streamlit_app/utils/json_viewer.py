"""Professional JSON viewer component."""

import json
from typing import Any, Dict, List, Union

import streamlit as st
from streamlit_ace import st_ace


def format_json_value(value: Any, indent: int = 0) -> str:
    """Format a JSON value for display."""
    if isinstance(value, (dict, list)):
        return json.dumps(value, indent=2)
    elif isinstance(value, str):
        return f'"{value}"'
    elif value is None:
        return 'null'
    elif isinstance(value, bool):
        return 'true' if value else 'false'
    else:
        return str(value)


def render_json_compact(data: Union[Dict, List], title: str = None, expanded: bool = True):
    """Render JSON data in a compact, professional format."""
    if not data:
        return

    if title:
        st.markdown(f'### {title}')

    # Use code editor for better JSON display
    json_str = json.dumps(data, indent=2, ensure_ascii=False)

    # Calculate appropriate height based on content
    lines = json_str.count('\n') + 1
    height = min(max(100, lines * 20), 600)  # Min 100px, max 600px

    st_ace(
        value=json_str,
        language='json',
        theme='monokai',
        key=f'json_viewer_{title}_{hash(json_str)}',
        height=height,
        auto_update=False,
        font_size=13,
        show_gutter=True,
        show_print_margin=False,
        wrap=False,
        annotations=None,
        readonly=True,
    )


def render_json_as_table(data: Dict, title: str = None):
    """Render JSON data as a formatted table for key-value pairs."""
    if not data:
        return

    if title:
        st.markdown(f'### {title}')

    # Create HTML table - use compact string to avoid rendering issues
    html = (  # noqa: E501
        '<style>'
        '.json-table { width: 100%; border-collapse: collapse; font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", monospace; font-size: 13px; margin: 10px 0; }'  # noqa: E501
        '.json-table th { background-color: #2d2d2d; color: #f0f0f0; text-align: left; padding: 10px 15px; border-bottom: 2px solid #444; font-weight: 600; }'  # noqa: E501
        '.json-table td { padding: 8px 15px; border-bottom: 1px solid #e0e0e0; vertical-align: top; }'
        '.json-table tr:hover { background-color: #f8f9fa; }'
        '.json-key { color: #0066cc; font-weight: 500; white-space: nowrap; width: 30%; }'
        '.json-value { color: #333; word-break: break-word; }'
        '.json-value-null { color: #999; font-style: italic; }'
        '.json-value-bool { color: #d73a49; }'
        '.json-value-number { color: #005cc5; }'
        '.json-value-string { color: #032f62; }'
        '.json-value-object { color: #6f42c1; font-family: "SF Mono", Monaco, monospace; font-size: 12px; background-color: #f6f8fa; padding: 4px 8px; border-radius: 3px; display: inline-block; max-width: 500px; overflow-x: auto; }'  # noqa: E501
        '</style>'
        '<table class="json-table">'
        '<thead><tr><th>Key</th><th>Value</th></tr></thead>'
        '<tbody>'
    )

    for key, value in data.items():
        value_class = 'json-value'
        value_str = ''

        if value is None:
            value_class = 'json-value-null'
            value_str = 'null'
        elif isinstance(value, bool):
            value_class = 'json-value-bool'
            value_str = str(value).lower()
        elif isinstance(value, (int, float)):
            value_class = 'json-value-number'
            value_str = str(value)
        elif isinstance(value, str):
            value_class = 'json-value-string'
            value_str = value
        elif isinstance(value, (dict, list)):
            value_class = 'json-value-object'
            value_str = json.dumps(value, ensure_ascii=False)
            if len(value_str) > 100:
                value_str = json.dumps(value, indent=2, ensure_ascii=False)
        else:
            value_str = str(value)

        html += f'<tr><td class="json-key">{key}</td><td class="{value_class}">{value_str}</td></tr>'

    html += '</tbody></table>'

    st.markdown(html, unsafe_allow_html=True)


def render_json_tree(data: Union[Dict, List], title: str = None, max_depth: int = 3):
    """Render JSON data as an expandable tree view."""
    if not data:
        return

    if title:
        st.markdown(f'### {title}')

    def render_node(obj: Any, key: str = '', depth: int = 0):
        """Recursively render JSON nodes."""
        indent = '&nbsp;' * (depth * 20)

        if isinstance(obj, dict):
            if depth < max_depth:
                with st.expander(f'{key or "Object"} ({len(obj)} items)', expanded=depth == 0):
                    for k, v in obj.items():
                        if isinstance(v, (dict, list)):
                            render_node(v, k, depth + 1)
                        else:
                            st.markdown(
                                f"<div style='font-family: monospace; font-size: 13px; padding: 2px 0;'>"
                                f"<span style='color: #0066cc; font-weight: 500;'>{k}:</span> "
                                f"<span style='color: #333;'>{format_json_value(v)}</span></div>",
                                unsafe_allow_html=True,
                            )
            else:
                st.code(json.dumps(obj, indent=2), language='json')

        elif isinstance(obj, list):
            if depth < max_depth:
                with st.expander(f'{key or "Array"} [{len(obj)} items]', expanded=depth == 0):
                    for i, item in enumerate(obj):
                        render_node(item, f'[{i}]', depth + 1)
            else:
                st.code(json.dumps(obj, indent=2), language='json')

        else:
            st.markdown(
                f"<div style='font-family: monospace; font-size: 13px; padding: 2px 0;'>"
                f"{indent}<span style='color: #333;'>{format_json_value(obj)}</span></div>",
                unsafe_allow_html=True,
            )

    render_node(data)


def render_metrics_grid(metrics: Dict, title: str = 'Metrics'):
    """Render metrics in a professional grid layout."""
    if not metrics:
        return

    st.markdown(f'### {title}')

    # Create columns based on number of metrics
    num_metrics = len(metrics)
    if num_metrics <= 3:
        cols = st.columns(num_metrics)
    elif num_metrics <= 6:
        cols = st.columns(3)
    else:
        cols = st.columns(4)

    for i, (key, value) in enumerate(metrics.items()):
        col_idx = i % len(cols)
        with cols[col_idx]:
            # Format the value
            if isinstance(value, float):
                if value < 1:
                    formatted_value = f'{value:.4f}'
                else:
                    formatted_value = f'{value:.2f}'
            elif isinstance(value, dict):
                formatted_value = f'{len(value)} items'
            elif isinstance(value, list):
                formatted_value = f'{len(value)} items'
            else:
                formatted_value = str(value)

            # Display as metric
            st.metric(
                label=key.replace('_', ' ').title(),
                value=formatted_value,
                delta=None,
            )
