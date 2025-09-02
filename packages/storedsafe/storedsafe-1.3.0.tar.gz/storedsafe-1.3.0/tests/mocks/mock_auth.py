"""
/auth endpoint mocks
"""
# pylint: disable=unused-wildcard-import,wildcard-import
from .mock_response import *


def login_totp(*args, **kwargs):
    """Send mocked response for totp login."""
    data = kwargs.get('json', {})
    if is_endpoint('/api/1.0/auth', args[0]):
        login_type = data.get('logintype', 'yubikey')
        if login_type == 'totp':
            if (
                    data.get('username') == MOCK_USERNAME and
                    data.get('passphrase') == MOCK_PASSPHRASE and
                    data.get('otp') == MOCK_OTP and
                    data.get('apikey') == MOCK_APIKEY
            ):
                return MockLoginSuccess(**kwargs)
        return MockError(**kwargs)
    return MockNotFound(**kwargs)


def login_yubikey(*args, **kwargs):
    """Send mocked response for yubikey login."""
    data = kwargs.get('json', {})
    if is_endpoint('/api/1.0/auth', args[0]):
        login_type = data.get('logintype', 'yubikey')
        if login_type == 'yubikey':
            if (
                    data.get('username') == MOCK_USERNAME and
                    data.get('keys') == MOCK_PASSPHRASE +
                MOCK_APIKEY + MOCK_OTP and
                    data.get('apikey') == MOCK_APIKEY
            ):
                return MockLoginSuccess(**kwargs)
        return MockError(**kwargs)
    return MockNotFound(**kwargs)


def login_smartcard(*args, **kwargs):
    """Send mocked response for smartcard login."""
    data = kwargs.get('json', {})
    if is_endpoint('/api/1.0/auth', args[0], mtls=True):
        login_type = data.get('logintype', 'yubikey')
        if login_type == 'smartcard':
            if (
                    data.get('username') == MOCK_USERNAME and
                    data.get('passphrase') == MOCK_PASSPHRASE and
                    kwargs.get('cert') == (MOCK_PUBKEY, MOCK_PRIVKEY) and
                    data.get('apikey') == MOCK_APIKEY
            ):
                return MockLoginSuccess(**kwargs)
        return MockError(**kwargs)
    return MockNotFound(**kwargs)


def logout(*args, **kwargs):
    """Send mocked response for logout."""
    if is_endpoint('/api/1.0/auth/logout', args[0]):
        if has_valid_token(**kwargs):
            return MockSuccess(**kwargs)
        return MockError(**kwargs)
    return MockNotFound(**kwargs)


def check(*args, **kwargs):
    """Send mocked response for check."""
    if is_endpoint('/api/1.0/auth/check', args[0]):
        if has_valid_token(**kwargs):
            return MockSuccess(**kwargs)
        return MockError(**kwargs)
    return MockNotFound(**kwargs)
