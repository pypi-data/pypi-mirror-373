"""
/object endpoint mocks
"""
# pylint: disable=unused-wildcard-import,wildcard-import
from .mock_response import *


def list_templates(*args, **kwargs):
    """Send mocked response listing all templates."""
    if is_endpoint(f'/api/1.0/template', args[0]):
        if has_valid_token(**kwargs):
            return MockSuccess(**kwargs)
        return MockError(**kwargs)
    return MockNotFound(**kwargs)


def get_template(*args, **kwargs):
    """Send mocked response getting template."""
    if is_endpoint(f'/api/1.0/template/{MOCK_TEMPLATE_ID}', args[0]):
        if has_valid_token(**kwargs):
            return MockSuccess(**kwargs)
        return MockError(**kwargs)
    return MockNotFound(**kwargs)
