from abc import ABC, abstractmethod

from synapse_sdk.shared.enums import SupportedTools


class BaseDMConverter(ABC):
    """Base class for DM format converters."""

    SUPPORTED_TOOLS = SupportedTools.get_all_values()

    def __init__(self, file_type=None):
        """Initialize the base converter.

        Args:
            file_type (str, optional): Type of file being converted (image, video, pcd, text, audio)
        """
        self.file_type = file_type
        self.tool_processors = self._setup_tool_processors()

    def _setup_tool_processors(self):
        """Setup tool processor mapping dynamically based on file_type."""
        if not self.file_type:
            return {}

        processors = {}
        tools = SupportedTools.get_tools_for_file_type(self.file_type)

        for tool in tools:
            # For other tools, use generic method names
            method_name = f'_convert_{tool.method_name}'

            if hasattr(self, method_name):
                processors[tool.annotation_tool] = getattr(self, method_name)

        return processors

    @abstractmethod
    def convert(self):
        """Convert data from one format to another."""

    def _handle_unknown_tool(self, tool_type, item_id=None):
        """Handle unknown tool types with consistent warning message."""
        warning_msg = f"Warning: Unknown tool type '{tool_type}'"
        if item_id:
            warning_msg += f' for item {item_id}'
        print(warning_msg)

    def _extract_media_type_info(self, media_id):
        """Extract media type information from media ID."""
        media_type = media_id.split('_')[0] if '_' in media_id else media_id
        media_type_plural = media_type + 's' if not media_type.endswith('s') else media_type
        return media_type, media_type_plural

    def _singularize_media_type(self, media_type_plural):
        """Convert plural media type to singular."""
        return media_type_plural.rstrip('s')
