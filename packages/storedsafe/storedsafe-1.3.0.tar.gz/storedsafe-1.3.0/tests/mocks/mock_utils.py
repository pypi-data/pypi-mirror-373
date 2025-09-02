"""
/object endpoint mocks
"""
# pylint: disable=unused-wildcard-import,wildcard-import
from .mock_response import *


def status_values(*args, **kwargs):
    """Send mocked response listing status values."""
    if is_endpoint('/api/1.0/utils/statusvalues', args[0]):
        if has_valid_token(**kwargs):
            return MockSuccess(**kwargs)
        return MockError(**kwargs)
    return MockNotFound(**kwargs)


def password_policies(*args, **kwargs):
    """Send mocked response listing password policies."""
    if is_endpoint('/api/1.0/utils/policies', args[0]):
        if has_valid_token(**kwargs):
            return MockSuccess(**kwargs)
        return MockError(**kwargs)
    return MockNotFound(**kwargs)


def version(*args, **kwargs):
    """Send mocked response getting StoredSafe version."""
    if is_endpoint('/api/1.0/utils/version', args[0]):
        if has_valid_token(**kwargs):
            return MockSuccess(**kwargs)
        return MockError(**kwargs)
    return MockNotFound(**kwargs)

def generate_password(*args, **kwargs):
    """Send mocked response generating password."""
    if is_endpoint('/api/1.0/utils/pwgen', args[0]):
        if has_valid_token(**kwargs):
            return MockSuccess(**kwargs)
        return MockError(**kwargs)
    return MockNotFound(**kwargs)

def generate_password_params(*args, **kwargs):
    """Send mocked response generating password with parameters."""
    data = kwargs.get('params', {})
    if is_endpoint('/api/1.0/utils/pwgen', args[0]):
        if has_valid_token(**kwargs) and data == MOCK_PARAMS:
            return MockSuccess(**kwargs)
        return MockError(**kwargs)
    return MockNotFound(**kwargs)
