"""
Test that /object endpoints use the correct format.
"""

import unittest
import tempfile
from unittest.mock import patch
from storedsafe import StoredSafe

# pylint: disable=unused-wildcard-import,wildcard-import
import mocks


class Object(unittest.TestCase):
    """Test /object endpoint"""

    def setUp(self):
        self.api = StoredSafe(
            host=mocks.MOCK_HOST, token=mocks.MOCK_TOKEN, **mocks.MOCK_DEFAULT_OPTIONS
        )

    @patch("requests.get", mocks.get_object)
    def test_get_object(self):
        """Successfully get object"""
        res = self.api.get_object(
            mocks.MOCK_OBJECT_ID, requests_options=mocks.MOCK_OVERRIDE_OPTIONS
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(mocks.has_merged_options(res.options), True)

    @patch("requests.get", mocks.get_object_children)
    def test_get_object_children(self):
        """Successfully get object with children"""
        res = self.api.get_object(
            mocks.MOCK_OBJECT_ID, True, requests_options=mocks.MOCK_OVERRIDE_OPTIONS
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(mocks.has_merged_options(res.options), True)

    @patch("requests.get", mocks.decrypt_object)
    def test_decrypt_object(self):
        """Successfully decrypt object"""
        res = self.api.decrypt_object(
            mocks.MOCK_OBJECT_ID, requests_options=mocks.MOCK_OVERRIDE_OPTIONS
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(mocks.has_merged_options(res.options), True)

    @patch("requests.post", mocks.create_object)
    def test_create_object(self):
        """Successful create object"""
        res = self.api.create_object(
            **mocks.MOCK_PARAMS, requests_options=mocks.MOCK_OVERRIDE_OPTIONS
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(mocks.has_merged_options(res.options), True)

    @patch("requests.put", mocks.edit_object)
    def test_edit_object(self):
        """Successful edit object"""
        res = self.api.edit_object(
            mocks.MOCK_OBJECT_ID,
            **mocks.MOCK_PARAMS,
            requests_options=mocks.MOCK_OVERRIDE_OPTIONS,
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(mocks.has_merged_options(res.options), True)

    @patch("requests.delete", mocks.delete_object)
    def test_delete_object(self):
        """Successful delete object"""
        res = self.api.delete_object(
            mocks.MOCK_OBJECT_ID, requests_options=mocks.MOCK_OVERRIDE_OPTIONS
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(mocks.has_merged_options(res.options), True)

    @patch("requests.get", mocks.find)
    def test_find(self):
        """Successfully request find"""
        res = self.api.find(
            mocks.MOCK_NEEDLE, requests_options=mocks.MOCK_OVERRIDE_OPTIONS
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(mocks.has_merged_options(res.options), True)

    @patch("requests.get", mocks.get_file)
    def test_get_file(self):
        """Successfully request file"""
        res = self.api.get_file(
            mocks.MOCK_OBJECT_ID, requests_options=mocks.MOCK_OVERRIDE_OPTIONS
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(mocks.has_merged_options(res.options), True)

    @patch("requests.post", mocks.get_mime_type)
    def test_get_mime_type(self):
        """Successfully request mime type"""
        with tempfile.NamedTemporaryFile(suffix=".txt") as fp:
            fp.write(mocks.MOCK_FILE_CONTENT)
            fp.flush()
            res = self.api.get_mime_type(fp.name, requests_options=mocks.MOCK_OVERRIDE_OPTIONS)
            self.assertEqual(res.status_code, 200)
            self.assertTrue(mocks.has_merged_options(res.options), True)

    @patch("requests.post", mocks.filecollect)
    def test_filecollect(self):
        """Successfully request filecollect"""
        with tempfile.NamedTemporaryFile(suffix=".txt") as fp:
            fp.write(mocks.MOCK_FILE_CONTENT)
            fp.flush()
            res = self.api.filecollect(fp.name, requests_options=mocks.MOCK_OVERRIDE_OPTIONS)
            self.assertEqual(res.status_code, 200)
            self.assertTrue(mocks.has_merged_options(res.options), True)

    @patch("requests.post", mocks.file_upload)
    def test_file_upload(self):
        """Successfully request file upload"""
        with tempfile.NamedTemporaryFile(suffix=".txt") as fp:
            fp.write(mocks.MOCK_FILE_CONTENT)
            fp.flush()
            res = self.api.upload_file(fp.name, **mocks.MOCK_PARAMS, requests_options=mocks.MOCK_OVERRIDE_OPTIONS)
            self.assertEqual(res.status_code, 200)
            self.assertTrue(mocks.has_merged_options(res.options), True)
