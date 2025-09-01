"""Styling constants and CSS for the Streamlit app."""

CUSTOM_CSS = """
<style>
/* Global typography and spacing */
* {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
}

/* Consistent button styling */
.stButton > button {
    border-radius: 6px;
    font-weight: 500;
    transition: all 0.2s ease;
    padding: 0.5rem 1rem;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
    font-size: 14px;
    font-weight: 500;
    letter-spacing: 0.3px;
}
.success-box {
    padding: 1rem;
    border-radius: 0.5rem;
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
    margin: 1rem 0;
}
.error-box {
    padding: 1rem;
    border-radius: 0.5rem;
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    color: #721c24;
    margin: 1rem 0;
}
.info-box {
    padding: 1rem;
    border-radius: 0.5rem;
    background-color: #d1ecf1;
    border: 1px solid #bee5eb;
    color: #0c5460;
    margin: 1rem 0;
}
.status-bar {
    background-color: #f8f9fa;
    border-radius: 0.5rem;
    padding: 1rem;
    margin: 1rem 0;
    border: 1px solid #dee2e6;
}
.log-container {
    background-color: #1e1e1e;
    color: #d4d4d4;
    font-family: 'Fira Code', 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 14px;
    line-height: 1.4;
    padding: 0;
    border-radius: 0.5rem;
    overflow-x: auto;
    overflow-y: auto;
    max-height: 400px;
    white-space: pre-wrap;
    word-wrap: break-word;
    border: 1px solid #3c3c3c;
    display: flex;
    flex-direction: column;
}
.log-line {
    margin: 0;
    padding: 0.2rem 1rem;
    display: flex;
    align-items: flex-start;
    border-bottom: 1px solid #2a2a2a;
}
.log-line:hover {
    background-color: #2a2a2a;
}
.log-line-number {
    color: #858585;
    font-size: 12px;
    min-width: 40px;
    text-align: right;
    padding-right: 12px;
    user-select: none;
    flex-shrink: 0;
}
.log-line-content {
    flex: 1;
    word-break: break-word;
}
.log-error {
    color: #f48771;
    font-weight: bold;
}
.log-warning {
    color: #dcdcaa;
}
.log-info {
    color: #9cdcfe;
}
.log-debug {
    color: #608b4e;
}
.log-timestamp {
    color: #569cd6;
}
.stJson {
    max-width: 100%;
    overflow-x: auto;
}
/* Professional styling for code blocks */
.stCodeBlock {
    background-color: #1e1e1e !important;
    border: 1px solid #3c3c3c !important;
    border-radius: 6px !important;
}
/* Enhanced headers */
h1, h2, h3 {
    font-weight: 600 !important;
    color: #1a1a1a !important;
}
/* Professional section spacing */
.section-divider {
    margin: 2rem 0;
    border-bottom: 1px solid #e0e0e0;
}
/* Hide the Streamlit toolbar */
.stAppToolbar {
    visibility: hidden;
}
/* Alternative method to hide toolbar */
[data-testid="stToolbar"] {
    display: none !important;
}
/* Reduce top padding of main container */
.stMainBlockContainer,
.block-container {
    padding-top: 1rem !important;
    max-width: 100%;
}
/* Better tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background-color: transparent;
    border-bottom: 2px solid #e9ecef;
    padding: 0;
}
.stTabs [data-baseweb="tab"] {
    padding: 10px 20px;
    border-radius: 0;
    background-color: transparent;
    border-bottom: 3px solid transparent;
    margin-bottom: -2px;
}
.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
    background-color: transparent;
    border-bottom: 3px solid #007bff;
    color: #007bff;
}
.stTabs [data-baseweb="tab"]:hover {
    background-color: #f8f9fa;
}

/* Form styling */
.stSelectbox > div > div {
    border-radius: 6px;
}
.stTextInput > div > div > input {
    border-radius: 6px;
}
.stTextArea > div > div > textarea {
    border-radius: 6px;
}

/* Checkbox and radio styling */
.stCheckbox > label > span {
    font-size: 14px;
}
.stRadio > label {
    font-size: 14px;
}

/* Metrics styling */
.metric-container .metric-label {
    font-size: 12px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #6c757d;
}

/* Consistent spacing */
.row-widget.stButton {
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
}
/* Also adjust the header spacing */
.stAppHeader {
    height: 0rem !important;
}
</style>
"""


def get_status_badge_html(status: str) -> str:
    """Generate HTML for status badge with outline style."""
    status = status.upper() if status else 'UNKNOWN'

    color_map = {
        'SUCCEEDED': '#28a745',
        'RUNNING': '#007bff',
        'PENDING': '#6c757d',
        'FAILED': '#dc3545',
        'STOPPED': '#6c757d',
        'UNKNOWN': '#6c757d',
    }

    color = color_map.get(status, '#6c757d')

    return f"""
    <span style="
        border: 1px solid {color};
        color: {color};
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
        display: inline-block;
        text-align: center;
        min-width: 70px;
    ">{status}</span>
    """
