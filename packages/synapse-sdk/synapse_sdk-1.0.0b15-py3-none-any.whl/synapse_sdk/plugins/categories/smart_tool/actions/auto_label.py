from synapse_sdk.plugins.categories.base import Action
from synapse_sdk.plugins.categories.decorators import register_action
from synapse_sdk.plugins.enums import PluginCategory, RunMethod
from synapse_sdk.plugins.exceptions import ActionError
from synapse_sdk.plugins.utils import get_action


@register_action
class AutoLabelAction(Action):
    name = 'auto_label'
    category = PluginCategory.SMART_TOOL
    method = RunMethod.TASK

    def get_auto_label(self):
        return self.entrypoint(**self.params)

    def run_model(self, input_data):
        try:
            action = get_action(
                'inference',
                input_data,
                config={
                    'category': 'neural_net',
                    'code': self.params['plugin'],
                    'version': self.params['version'],
                    'actions': {'inference': {'method': input_data['method']}},
                },
            )
            return action.run_action()
        except ActionError as e:
            raise Exception(e.errors)

    def start(self):
        auto_label = self.get_auto_label()
        input_data = auto_label.handle_input(self.params)
        output_data = self.run_model(input_data)
        return auto_label.handle_output(output_data)
