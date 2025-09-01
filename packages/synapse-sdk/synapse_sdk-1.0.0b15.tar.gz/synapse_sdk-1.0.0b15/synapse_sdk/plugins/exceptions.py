class ActionError(Exception):
    errors = None

    def __init__(self, errors, *args):
        if isinstance(errors, (str, dict)):
            self.errors = errors
        elif isinstance(errors, Exception) and len(errors.args) == 1:
            self.errors = ActionError(errors.args[0]).errors
        else:
            self.errors = str(errors)
        super().__init__(errors, *args)

    def as_drf_error(self, data=None):
        if data is None:
            data = self.errors

        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return {key: self.as_drf_error(value) for key, value in data.items()}

        return [str(data)]
