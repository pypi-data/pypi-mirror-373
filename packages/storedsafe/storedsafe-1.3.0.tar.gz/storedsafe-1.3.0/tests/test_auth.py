"""
Test that /auth endpoints use the correct format.
"""
import unittest
from unittest.mock import patch
from storedsafe import StoredSafe
# pylint: disable=unused-wildcard-import,wildcard-import
from mocks import *


class Auth(unittest.TestCase):
    """Test /auth endpoint"""

    @patch('requests.post', login_totp)
    def test_login_totp(self):
        """Successful login using TOTP"""
        api = StoredSafe(host=MOCK_HOST, apikey=MOCK_APIKEY,
                         **MOCK_DEFAULT_OPTIONS)
        res = api.login_totp(MOCK_USERNAME, MOCK_PASSPHRASE,
                             MOCK_OTP, MOCK_OVERRIDE_OPTIONS)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(api.token, MOCK_TOKEN)
        self.assertTrue(has_merged_options(res.options), True)

    @patch('requests.post', login_yubikey)
    def test_login_yubikey(self):
        """Successful login using YubiKey"""
        api = StoredSafe(host=MOCK_HOST, apikey=MOCK_APIKEY,
                         **MOCK_DEFAULT_OPTIONS)
        res = api.login_yubikey(
            MOCK_USERNAME, MOCK_PASSPHRASE, MOCK_OTP, MOCK_OVERRIDE_OPTIONS)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(api.token, MOCK_TOKEN)
        self.assertTrue(has_merged_options(res.options), True)

    @patch('requests.post', login_smartcard)
    def test_login_smartcard(self):
        """Successful login using mTLS"""
        api = StoredSafe(host=MOCK_HOST, apikey=MOCK_APIKEY,
                         **MOCK_DEFAULT_OPTIONS)
        res = api.login_smartcard(
            MOCK_USERNAME, MOCK_PASSPHRASE, MOCK_PUBKEY, MOCK_PRIVKEY,
            MOCK_OVERRIDE_OPTIONS)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(api.token, MOCK_TOKEN)
        self.assertTrue(has_merged_options(res.options), True)

    @patch('requests.get', logout)
    def test_logout(self):
        """Successful logout"""
        api = StoredSafe(host=MOCK_HOST, token=MOCK_TOKEN,
                         **MOCK_DEFAULT_OPTIONS)
        res = api.logout(MOCK_OVERRIDE_OPTIONS)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(has_merged_options(res.options), True)

    @patch('requests.post', check)
    def test_check(self):
        """Successful check"""
        api = StoredSafe(host=MOCK_HOST, token=MOCK_TOKEN,
                         **MOCK_DEFAULT_OPTIONS)
        res = api.check(MOCK_OVERRIDE_OPTIONS)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(has_merged_options(res.options), True)
