"""Configuration tab UI component."""

import streamlit as st

from ..services.plugin_service import PluginService
from ..utils.ui_components import render_info_card


class ConfigTab:
    """UI component for the Configuration tab."""

    def __init__(self, plugin_service: PluginService):
        self.plugin_service = plugin_service

    def render(self):
        """Render the Configuration tab."""
        config = st.session_state.get('config', self.plugin_service.load_config())

        if not config:
            render_info_card(
                'No Configuration',
                'No plugin configuration file found. Please create a config.yaml file.',
                type='error',
            )
            return

        # Display file path
        render_info_card('Configuration File', str(self.plugin_service.config_path), type='neutral', icon='📁')

        # Configuration form
        with st.form('config_form'):
            col1, col2 = st.columns(2)

            with col1:
                config['name'] = st.text_input('Plugin Name', value=config.get('name', ''))
                config['code'] = st.text_input('Code', value=config.get('code', ''))
                config['version'] = st.text_input('Version', value=config.get('version', ''))

                categories = [
                    'neural_net',
                    'export',
                    'upload',
                    'smart_tool',
                    'post_annotation',
                    'pre_annotation',
                    'data_validation',
                ]
                current_category = config.get('category', '')
                category_index = categories.index(current_category) if current_category in categories else 0
                config['category'] = st.selectbox('Category', categories, index=category_index)

            with col2:
                data_types = ['image', 'text', 'video', 'pcd', 'audio']
                current_data_type = config.get('data_type', '')
                data_type_index = data_types.index(current_data_type) if current_data_type in data_types else 0
                config['data_type'] = st.selectbox('Data Type', data_types, index=data_type_index)

                package_managers = ['pip', 'uv']
                current_pm = config.get('package_manager', '')
                pm_index = package_managers.index(current_pm) if current_pm in package_managers else 0
                config['package_manager'] = st.selectbox('Package Manager', package_managers, index=pm_index)

            config['description'] = st.text_area('Description', value=config.get('description', ''), height=100)

            config_tasks = config.get('tasks', [])
            tasks_str = ', '.join(config_tasks) if isinstance(config_tasks, list) else config.get('tasks', '')
            tasks_input = st.text_input('Task Types (comma-separated)', value=tasks_str)
            config['tasks'] = [t.strip() for t in tasks_input.split(',') if t.strip()]

            if st.form_submit_button('Save Configuration', type='primary'):
                st.session_state['config'] = config
                if self.plugin_service.save_config(config):
                    st.success('✅ Configuration saved successfully!')
                    st.rerun()
                else:
                    st.error('Failed to save configuration')
