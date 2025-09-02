"""
/object endpoint mocks
"""
# pylint: disable=unused-wildcard-import,wildcard-import
from .mock_response import *


def list_users(*args, **kwargs):
    """Send mocked response listing all users."""
    if is_endpoint('/api/1.0/user', args[0]):
        if has_valid_token(**kwargs):
            return MockSuccess(**kwargs)
        return MockError(**kwargs)
    return MockNotFound(**kwargs)


def list_users_search_string(*args, **kwargs):
    """Send mocked response listing all users matching search string."""
    if is_endpoint(f'/api/1.0/user/{MOCK_SEARCH_STRING}', args[0]):
        if has_valid_token(**kwargs):
            return MockSuccess(**kwargs)
        return MockError(**kwargs)
    return MockNotFound(**kwargs)


def get_user(*args, **kwargs):
    """Send mocked response getting user."""
    if is_endpoint(f'/api/1.0/user/{MOCK_USER_ID}', args[0]):
        if has_valid_token(**kwargs):
            return MockSuccess(**kwargs)
        return MockError(**kwargs)
    return MockNotFound(**kwargs)


def create_user(*args, **kwargs):
    """Send mocked response creating user."""
    data = kwargs.get('json', {})
    if is_endpoint('/api/1.0/user', args[0]):
        if has_valid_token(**kwargs) and data == MOCK_PARAMS:
            return MockSuccess(**kwargs)
        return MockError(**kwargs)
    return MockNotFound(**kwargs)


def edit_user(*args, **kwargs):
    """Send mocked response editing user."""
    data = kwargs.get('json', {})
    if is_endpoint(f'/api/1.0/user/{MOCK_USER_ID}', args[0]):
        if has_valid_token(**kwargs) and data == MOCK_PARAMS:
            return MockSuccess(**kwargs)
        return MockError(**kwargs)
    return MockNotFound(**kwargs)


def delete_user(*args, **kwargs):
    """Send mocked response editing user."""
    if is_endpoint(f'/api/1.0/user/{MOCK_USER_ID}', args[0]):
        if has_valid_token(**kwargs):
            return MockSuccess(**kwargs)
        return MockError(**kwargs)
    return MockNotFound(**kwargs)
