from synapse_sdk.utils import debug


def test_debug_get_message():
    message = debug.get_message()
    assert message == 'hello world from sdk'
