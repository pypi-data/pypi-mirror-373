"""Tests for plugin registry utilities."""

from unittest.mock import patch

from synapse_sdk.plugins.enums import PluginCategory
from synapse_sdk.plugins.utils.registry import (
    get_category_display_name,
    get_plugin_categories,
    is_valid_category,
)


class TestGetPluginCategories:
    """Test get_plugin_categories function."""

    def test_get_plugin_categories(self):
        """Test getting all plugin categories."""
        result = get_plugin_categories()

        expected_categories = [
            'neural_net',
            'export',
            'upload',
            'smart_tool',
            'post_annotation',
            'pre_annotation',
            'data_validation',
        ]

        assert isinstance(result, list)
        assert len(result) == len(PluginCategory)

        # Check that all expected categories are present
        for category in expected_categories:
            assert category in result

    def test_get_plugin_categories_returns_values(self):
        """Test that function returns enum values, not names."""
        result = get_plugin_categories()

        # Should contain values like 'neural_net', not names like 'NEURAL_NET'
        assert 'neural_net' in result
        assert 'NEURAL_NET' not in result
        assert 'export' in result
        assert 'EXPORT' not in result


class TestIsValidCategory:
    """Test is_valid_category function."""

    def test_is_valid_category_true(self):
        """Test validation of valid categories."""
        valid_categories = [
            'neural_net',
            'export',
            'upload',
            'smart_tool',
            'post_annotation',
            'pre_annotation',
            'data_validation',
        ]

        for category in valid_categories:
            assert is_valid_category(category) is True

    def test_is_valid_category_false(self):
        """Test validation of invalid categories."""
        invalid_categories = [
            'invalid_category',
            'NEURAL_NET',  # Should be lowercase with underscore
            'neural-net',  # Should use underscore, not hyphen
            'neuralnet',  # Should have underscore
            '',  # Empty string
            'ml',  # Not a defined category
            'ai',  # Not a defined category
        ]

        for category in invalid_categories:
            assert is_valid_category(category) is False

    def test_is_valid_category_case_sensitive(self):
        """Test that category validation is case sensitive."""
        # Valid: lowercase with underscore
        assert is_valid_category('neural_net') is True

        # Invalid: different cases
        assert is_valid_category('Neural_Net') is False
        assert is_valid_category('NEURAL_NET') is False
        assert is_valid_category('neural_NET') is False


class TestGetCategoryDisplayName:
    """Test get_category_display_name function."""

    def test_get_category_display_name_valid_categories(self):
        """Test getting display names for valid categories."""
        test_cases = [
            ('neural_net', 'Neural Net'),
            ('export', 'Export'),
            ('upload', 'Upload'),
            ('smart_tool', 'Smart Tool'),
            ('post_annotation', 'Post Annotation'),
            ('pre_annotation', 'Pre Annotation'),
            ('data_validation', 'Data Validation'),
        ]

        for category, expected_display_name in test_cases:
            result = get_category_display_name(category)
            assert result == expected_display_name

    def test_get_category_display_name_invalid_category(self):
        """Test getting display names for invalid categories."""
        # Should still format the string nicely even for invalid categories
        test_cases = [
            ('invalid_category', 'Invalid Category'),
            ('my_custom_plugin', 'My Custom Plugin'),
            ('test_plugin_type', 'Test Plugin Type'),
            ('single', 'Single'),
            ('', ''),  # Edge case: empty string
        ]

        for category, expected_display_name in test_cases:
            result = get_category_display_name(category)
            assert result == expected_display_name

    def test_get_category_display_name_special_cases(self):
        """Test display name generation for special cases."""
        # Test with hyphens (should still work)
        assert get_category_display_name('neural-net') == 'Neural-Net'

        # Test with mixed case
        assert get_category_display_name('Neural_Net') == 'Neural Net'

        # Test with numbers
        assert get_category_display_name('plugin_v2') == 'Plugin V2'

        # Test with single word
        assert get_category_display_name('test') == 'Test'

    @patch('synapse_sdk.plugins.utils.registry.PluginCategory')
    def test_get_category_display_name_enum_error(self, mock_plugin_category):
        """Test fallback when enum lookup fails."""
        # Simulate ValueError when creating enum from value
        mock_plugin_category.side_effect = ValueError('Invalid enum value')

        result = get_category_display_name('invalid_category')

        # Should fall back to string formatting
        assert result == 'Invalid Category'


# Integration tests
class TestRegistryIntegration:
    """Integration tests for registry utilities."""

    def test_all_categories_have_display_names(self):
        """Test that all valid categories have proper display names."""
        categories = get_plugin_categories()

        for category in categories:
            display_name = get_category_display_name(category)

            # Display name should not be empty
            assert display_name
            assert isinstance(display_name, str)

            # Should be title case
            assert display_name[0].isupper()

            # Should not contain underscores
            assert '_' not in display_name

    def test_category_validation_consistency(self):
        """Test consistency between category list and validation."""
        categories = get_plugin_categories()

        # All categories from get_plugin_categories should be valid
        for category in categories:
            assert is_valid_category(category) is True

        # Some obviously invalid categories should not be valid
        invalid_categories = ['invalid', 'not_a_category', 'fake_plugin_type']
        for category in invalid_categories:
            assert is_valid_category(category) is False

    def test_display_names_are_human_readable(self):
        """Test that display names are properly formatted for humans."""
        categories = get_plugin_categories()

        for category in categories:
            display_name = get_category_display_name(category)

            # Should be different from the raw category name (unless single word)
            if '_' in category:
                assert display_name != category

            # Should not start or end with spaces
            assert display_name == display_name.strip()

            # Should have proper capitalization
            words = display_name.split()
            for word in words:
                if word:  # Skip empty words
                    assert word[0].isupper(), f"Word '{word}' in '{display_name}' should be capitalized"
