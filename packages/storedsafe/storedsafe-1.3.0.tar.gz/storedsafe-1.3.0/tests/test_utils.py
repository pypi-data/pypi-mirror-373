"""
Test that /utils endpoints use the correct format.
"""
import unittest
from unittest.mock import patch
from storedsafe import StoredSafe
# pylint: disable=unused-wildcard-import,wildcard-import
from mocks import *


class Utils(unittest.TestCase):
    """Test /utils endpoint"""

    def setUp(self):
        self.api = StoredSafe(host=MOCK_HOST, token=MOCK_TOKEN, **MOCK_DEFAULT_OPTIONS)

    @patch('requests.get', status_values)
    def test_status_values(self):
        """Successfully list status values"""
        res = self.api.status_values(requests_options=MOCK_OVERRIDE_OPTIONS)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(has_merged_options(res.options), True)

    @patch('requests.get', password_policies)
    def test_password_policies(self):
        """Successfully list password policies"""
        res = self.api.password_policies(requests_options=MOCK_OVERRIDE_OPTIONS)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(has_merged_options(res.options), True)

    @patch('requests.get', version)
    def test_version(self):
        """Successfully get StoredSafe version"""
        res = self.api.version(requests_options=MOCK_OVERRIDE_OPTIONS)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(has_merged_options(res.options), True)

    @patch('requests.get', generate_password)
    def test_generate_password(self):
        """Successfully generate password"""
        res = self.api.generate_password(requests_options=MOCK_OVERRIDE_OPTIONS)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(has_merged_options(res.options), True)

    @patch('requests.get', generate_password_params)
    def test_generate_password_params(self):
        """Successfully generate password with parameters"""
        res = self.api.generate_password(**MOCK_PARAMS, requests_options=MOCK_OVERRIDE_OPTIONS)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(has_merged_options(res.options), True)
