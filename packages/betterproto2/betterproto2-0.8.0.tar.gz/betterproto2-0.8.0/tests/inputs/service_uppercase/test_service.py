import inspect

from tests.outputs.service_uppercase.service_uppercase import TestStub


def test_parameters():
    sig = inspect.signature(TestStub.do_thing)
    assert len(sig.parameters) == 5, "Expected 5 parameters"
