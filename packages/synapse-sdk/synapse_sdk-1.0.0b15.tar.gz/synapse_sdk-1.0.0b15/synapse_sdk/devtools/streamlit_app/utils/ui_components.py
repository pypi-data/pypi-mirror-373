"""Unified UI components for consistent styling across the application."""

from typing import Any, Callable, Optional

import streamlit as st


def render_action_button(
    label: str,
    key: str,
    type: str = 'secondary',
    icon: Optional[str] = None,
    on_click: Optional[Callable] = None,
    args: Optional[tuple] = None,
    disabled: bool = False,
    use_container_width: bool = False,
    help: Optional[str] = None,
) -> bool:
    """Render a styled action button with consistent appearance."""
    button_types = {
        'primary': 'primary',
        'secondary': 'secondary',
        'danger': 'secondary',  # Streamlit doesn't have danger, use CSS
        'success': 'secondary',
        'minimal': 'secondary',
    }

    # Add icon to label if provided
    if icon:
        display_label = f'{icon} {label}'
    else:
        display_label = label

    # Create button with appropriate styling
    clicked = st.button(
        display_label,
        key=key,
        type=button_types.get(type, 'secondary'),
        on_click=on_click,
        args=args,
        disabled=disabled,
        use_container_width=use_container_width,
        help=help,
    )

    # Apply custom CSS for special button types
    if type == 'danger':
        st.markdown(
            f"""
            <style>
            button[kind="secondary"][key="{key}"] {{
                background-color: #fff;
                color: #dc3545;
                border-color: #dc3545;
            }}
            button[kind="secondary"][key="{key}"]:hover {{
                background-color: #dc3545;
                color: white;
            }}
            </style>
        """,
            unsafe_allow_html=True,
        )
    elif type == 'success':
        st.markdown(
            f"""
            <style>
            button[kind="secondary"][key="{key}"] {{
                background-color: #fff;
                color: #28a745;
                border-color: #28a745;
            }}
            button[kind="secondary"][key="{key}"]:hover {{
                background-color: #28a745;
                color: white;
            }}
            </style>
        """,
            unsafe_allow_html=True,
        )
    elif type == 'minimal':
        st.markdown(
            f"""
            <style>
            button[kind="secondary"][key="{key}"] {{
                background-color: transparent;
                border: none;
                color: #007bff;
                padding: 4px 8px;
            }}
            button[kind="secondary"][key="{key}"]:hover {{
                background-color: #f8f9fa;
                text-decoration: underline;
            }}
            </style>
        """,
            unsafe_allow_html=True,
        )

    return clicked


def render_section_header(title: str, subtitle: Optional[str] = None):
    """Render a consistent section header."""
    subtitle_html = (
        f'<p style="margin-top: 0.25rem; color: #6c757d; font-size: 14px;">{subtitle}</p>' if subtitle else ''
    )
    st.markdown(
        f'<div style="margin-bottom: 1.5rem;">'
        f'<h3 style="margin: 0; font-weight: 600; color: #1a1a1a;">{title}</h3>'
        f'{subtitle_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_info_card(title: str, content: str, type: str = 'info', icon: Optional[str] = None):
    """Render an information card with consistent styling."""
    colors = {
        'info': {'bg': '#d1ecf1', 'border': '#bee5eb', 'text': '#0c5460'},
        'success': {'bg': '#d4edda', 'border': '#c3e6cb', 'text': '#155724'},
        'warning': {'bg': '#fff3cd', 'border': '#ffeaa7', 'text': '#856404'},
        'error': {'bg': '#f8d7da', 'border': '#f5c6cb', 'text': '#721c24'},
        'neutral': {'bg': '#f8f9fa', 'border': '#dee2e6', 'text': '#495057'},
    }

    color_scheme = colors.get(type, colors['info'])
    icon_html = f'<span style="margin-right: 8px;">{icon}</span>' if icon else ''

    st.markdown(
        f'<div style="'
        f'  background-color: {color_scheme["bg"]};'
        f'  border: 1px solid {color_scheme["border"]};'
        f'  border-radius: 6px;'
        f'  padding: 12px 16px;'
        f'  margin: 12px 0;'
        f'">'
        f'<div style="color: {color_scheme["text"]}; font-weight: 500; margin-bottom: 4px;">'
        f'{icon_html}{title}'
        f'</div>'
        f'<div style="color: {color_scheme["text"]}; font-size: 14px;">{content}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: Any, delta: Optional[str] = None, delta_color: str = 'normal'):
    """Render a metric card with consistent styling."""
    delta_html = ''
    if delta:
        color = {'normal': '#28a745', 'inverse': '#dc3545', 'off': '#6c757d'}.get(delta_color, '#28a745')
        delta_html = f'<div style="color: {color}; font-size: 12px; margin-top: 4px;">{delta}</div>'

    st.markdown(
        f'<div style="'
        f'  background-color: #fff;'
        f'  border: 1px solid #e0e0e0;'
        f'  border-radius: 8px;'
        f'  padding: 16px;'
        f'  margin: 8px 0;'
        f'">'
        f'<div style="color: #6c757d; font-size: 12px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">'  # noqa: E501
        f'{label}'
        f'</div>'
        f'<div style="color: #212529; font-size: 24px; font-weight: 600; margin-top: 4px;">'
        f'{value}'
        f'</div>'
        f'{delta_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_key_value_pair(key: str, value: Any, monospace_value: bool = False, inline: bool = True):
    """Render a key-value pair with consistent styling."""
    value_style = 'font-family: monospace;' if monospace_value else ''

    if inline:
        st.markdown(
            f'<div style="margin-bottom: 8px; font-size: 14px;">'
            f'<span style="color: #495057; font-weight: 500;">{key}:</span> '
            f'<span style="color: #212529; {value_style}">{value}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div style="margin-bottom: 12px;">'
            f'<div style="color: #495057; font-weight: 500; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">'  # noqa: E501
            f'{key}'
            f'</div>'
            f'<div style="color: #212529; font-size: 14px; {value_style}">{value}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


def render_divider(margin: str = '1.5rem'):
    """Render a consistent divider."""
    st.markdown(
        f'<hr style="margin: {margin} 0; border: none; border-top: 1px solid #e0e0e0;">', unsafe_allow_html=True
    )


def render_table_header(columns: list, column_widths: list = None):
    """Render a consistent table header."""
    if not column_widths:
        column_widths = [1] * len(columns)

    header_cols = st.columns(column_widths)
    for i, header in enumerate(columns):
        with header_cols[i]:
            st.markdown(
                f'<div style="'
                f'  color: #495057;'
                f'  font-size: 12px;'
                f'  font-weight: 600;'
                f'  text-transform: uppercase;'
                f'  letter-spacing: 0.5px;'
                f'  padding: 8px 0;'
                f'  border-bottom: 2px solid #dee2e6;'
                f'">{header}</div>',
                unsafe_allow_html=True,
            )
    return header_cols


def render_empty_state(
    message: str,
    icon: Optional[str] = None,
    action_label: Optional[str] = None,
    action_callback: Optional[Callable] = None,
):
    """Render an empty state message with optional action."""
    icon_html = f'<div style="font-size: 48px; margin-bottom: 16px;">{icon}</div>' if icon else ''

    st.markdown(
        f'<div style="'
        f'  text-align: center;'
        f'  padding: 48px 24px;'
        f'  background-color: #f8f9fa;'
        f'  border-radius: 8px;'
        f'  margin: 24px 0;'
        f'">'
        f'{icon_html}'
        f'<div style="color: #6c757d; font-size: 16px;">{message}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if action_label and action_callback:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(action_label, key='empty_state_action', type='primary'):
                action_callback()


def render_progress_bar(progress: float, label: Optional[str] = None, show_percentage: bool = True):
    """Render a custom progress bar with consistent styling."""
    percentage = int(progress * 100)

    label_html = f'<div style="font-size: 12px; color: #6c757d; margin-bottom: 4px;">{label}</div>' if label else ''
    percentage_html = (
        f'<span style="font-size: 12px; color: #495057; margin-left: 8px;">{percentage}%</span>'
        if show_percentage
        else ''
    )

    st.markdown(
        f'{label_html}'
        f'<div style="display: flex; align-items: center;">'
        f'<div style="'
        f'  flex: 1;'
        f'  height: 8px;'
        f'  background-color: #e9ecef;'
        f'  border-radius: 4px;'
        f'  overflow: hidden;'
        f'">'
        f'<div style="'
        f'  width: {percentage}%;'
        f'  height: 100%;'
        f'  background: linear-gradient(90deg, #007bff 0%, #0056b3 100%);'
        f'  transition: width 0.3s ease;'
        f'"></div>'
        f'</div>'
        f'{percentage_html}'
        f'</div>',
        unsafe_allow_html=True,
    )
