"""
Test that /user endpoints use the correct format.
"""
import unittest
from unittest.mock import patch
from storedsafe import StoredSafe
# pylint: disable=unused-wildcard-import,wildcard-import
from mocks import *


class User(unittest.TestCase):
    """Test /user endpoint"""

    def setUp(self):
        self.api = StoredSafe(
            host=MOCK_HOST, token=MOCK_TOKEN, **MOCK_DEFAULT_OPTIONS)

    @patch('requests.get', list_users)
    def test_list_users(self):
        """Successfully list users"""
        res = self.api.list_users(requests_options=MOCK_OVERRIDE_OPTIONS)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(has_merged_options(res.options), True)

    @patch('requests.get', list_users_search_string)
    def test_list_users_search_string(self):
        """Successfully list users"""
        res = self.api.list_users(
            search_string=MOCK_SEARCH_STRING, requests_options=MOCK_OVERRIDE_OPTIONS)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(has_merged_options(res.options), True)

    @patch('requests.get', get_user)
    def test_get_user(self):
        """Successfully get user"""
        res = self.api.get_user(
            MOCK_USER_ID, requests_options=MOCK_OVERRIDE_OPTIONS)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(has_merged_options(res.options), True)

    @patch('requests.post', create_user)
    def test_create_user(self):
        """Successfully create user"""
        res = self.api.create_user(
            **MOCK_PARAMS, requests_options=MOCK_OVERRIDE_OPTIONS)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(has_merged_options(res.options), True)

    @patch('requests.put', edit_user)
    def test_edit_user(self):
        """Successfully edit user"""
        res = self.api.edit_user(
            MOCK_USER_ID, **MOCK_PARAMS, requests_options=MOCK_OVERRIDE_OPTIONS)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(has_merged_options(res.options), True)

    @patch('requests.delete', delete_user)
    def test_delete_user(self):
        """Successfully delete user"""
        res = self.api.delete_user(
            MOCK_USER_ID, requests_options=MOCK_OVERRIDE_OPTIONS)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(has_merged_options(res.options), True)
