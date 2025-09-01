class ClientError(Exception):
    status = None
    reason = None

    def __init__(self, status, reason, *args):
        self.status = status
        self.reason = reason
        super().__init__(status, reason, *args)
