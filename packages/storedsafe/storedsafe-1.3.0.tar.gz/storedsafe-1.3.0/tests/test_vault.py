"""
Test that /vault endpoints use the correct format.
"""
import unittest
from unittest.mock import patch
from storedsafe import StoredSafe
# pylint: disable=unused-wildcard-import,wildcard-import
from mocks import *


class Vault(unittest.TestCase):
    """Test /vault endpoint"""

    def setUp(self):
        self.api = StoredSafe(
            host=MOCK_HOST, token=MOCK_TOKEN, **MOCK_DEFAULT_OPTIONS)

    @patch('requests.get', list_vaults)
    def test_list_vaults(self):
        """Successfully list vaults"""
        res = self.api.list_vaults(requests_options=MOCK_OVERRIDE_OPTIONS)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(has_merged_options(res.options), True)

    @patch('requests.get', vault_objects)
    def test_vault_objects(self):
        """Successfully list objects in vault"""
        res = self.api.vault_objects(
            MOCK_VAULT_ID, requests_options=MOCK_OVERRIDE_OPTIONS)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(has_merged_options(res.options), True)

    @patch('requests.get', vault_members)
    def test_vault_members(self):
        """Successfully list members in vault"""
        res = self.api.vault_members(
            MOCK_VAULT_ID, requests_options=MOCK_OVERRIDE_OPTIONS)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(has_merged_options(res.options), True)

    @patch('requests.post', add_vault_member)
    def test_add_vault_member(self):
        """Successful add member to vault"""
        res = self.api.add_vault_member(
            MOCK_VAULT_ID, MOCK_USER_ID, MOCK_STATUS, requests_options=MOCK_OVERRIDE_OPTIONS)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(has_merged_options(res.options), True)

    @patch('requests.put', edit_vault_member)
    def test_edit_vault_member(self):
        """Successful edit member in vault"""
        res = self.api.edit_vault_member(
            MOCK_VAULT_ID, MOCK_USER_ID, MOCK_STATUS, requests_options=MOCK_OVERRIDE_OPTIONS)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(has_merged_options(res.options), True)

    @patch('requests.delete', remove_vault_member)
    def test_remove_vault_member(self):
        """Successful remove member in vault"""
        res = self.api.remove_vault_member(
            MOCK_VAULT_ID, MOCK_USER_ID, requests_options=MOCK_OVERRIDE_OPTIONS)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(has_merged_options(res.options), True)

    @patch('requests.post', create_vault)
    def test_create_vault(self):
        """Successful create new vault"""
        res = self.api.create_vault(
            **MOCK_PARAMS, requests_options=MOCK_OVERRIDE_OPTIONS)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(has_merged_options(res.options), True)

    @patch('requests.put', edit_vault)
    def test_edit_vault(self):
        """Successful edit vault"""
        res = self.api.edit_vault(
            MOCK_VAULT_ID, **MOCK_PARAMS, requests_options=MOCK_OVERRIDE_OPTIONS)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(has_merged_options(res.options), True)

    @patch('requests.delete', delete_vault)
    def test_delete_vault(self):
        """Successful delete vault"""
        res = self.api.delete_vault(
            MOCK_VAULT_ID, requests_options=MOCK_OVERRIDE_OPTIONS)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(has_merged_options(res.options), True)
