"""
Test that /template endpoints use the correct format.
"""
import unittest
from unittest.mock import patch
from storedsafe import StoredSafe
# pylint: disable=unused-wildcard-import,wildcard-import
from mocks import *


class Template(unittest.TestCase):
    """Test /template endpoint"""

    def setUp(self):
        self.api = StoredSafe(
            host=MOCK_HOST, token=MOCK_TOKEN, **MOCK_DEFAULT_OPTIONS)

    @patch('requests.get', list_templates)
    def test_list_templates(self):
        """Successfully list templates"""
        res = self.api.list_templates(requests_options=MOCK_OVERRIDE_OPTIONS)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(has_merged_options(res.options), True)

    @patch('requests.get', get_template)
    def test_get_template(self):
        """Successfully get template"""
        res = self.api.get_template(
            MOCK_TEMPLATE_ID, requests_options=MOCK_OVERRIDE_OPTIONS)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(has_merged_options(res.options), True)
