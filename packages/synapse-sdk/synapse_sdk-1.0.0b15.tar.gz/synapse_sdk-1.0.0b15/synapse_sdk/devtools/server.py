"""
Legacy server module - DEPRECATED

This module is kept for backwards compatibility only.
The devtools now use Streamlit exclusively.

All functionality has been moved to streamlit_app.py
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class DevtoolsServer:
    """Legacy DevtoolsServer class - DEPRECATED

    This class is kept only for backwards compatibility.
    Use streamlit_app.py instead.
    """

    def __init__(self, host: str = '0.0.0.0', port: int = 8080, plugin_directory: str = None):
        logger.warning("DevtoolsServer is deprecated. Use 'synapse devtools' command which runs Streamlit instead.")
        self.host = host
        self.port = port
        self.plugin_directory = Path(plugin_directory) if plugin_directory else Path.cwd()

    def start_server(self):
        """Legacy method - DEPRECATED"""
        logger.error("FastAPI server is no longer supported. Use 'synapse devtools' command to run Streamlit app.")
        raise RuntimeError("FastAPI server is deprecated. Use 'synapse devtools' command to run the Streamlit app.")


def create_devtools_server(host: str = '0.0.0.0', port: int = 8080, plugin_directory: str = None) -> DevtoolsServer:
    """Legacy function - DEPRECATED

    This function is kept only for backwards compatibility.
    Use 'synapse devtools' command instead.
    """
    return DevtoolsServer(host=host, port=port, plugin_directory=plugin_directory)
