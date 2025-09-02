"""
/object endpoint mocks
"""
import mocks.mock_response as mockr
from base64 import b64encode


def get_object(*args, **kwargs):
    """Send mocked response getting object."""
    if mockr.is_endpoint(f"/api/1.0/object/{mockr.MOCK_OBJECT_ID}", args[0]):
        if mockr.has_valid_token(**kwargs):
            return mockr.MockSuccess(**kwargs)
        return mockr.MockError(**kwargs)
    return mockr.MockNotFound(**kwargs)


def get_object_children(*args, **kwargs):
    """Send mocked response getting object."""
    data = kwargs.get("params", {})
    if mockr.is_endpoint(f"/api/1.0/object/{mockr.MOCK_OBJECT_ID}", args[0]):
        if mockr.has_valid_token(**kwargs) and data.get("children") == "true":
            return mockr.MockSuccess(**kwargs)
        return mockr.MockError(**kwargs)
    return mockr.MockNotFound(**kwargs)


def decrypt_object(*args, **kwargs):
    """Send mocked response for decrypting object."""
    data = kwargs.get("params", {})
    if mockr.is_endpoint(f"/api/1.0/object/{mockr.MOCK_OBJECT_ID}", args[0]):
        if mockr.has_valid_token(**kwargs) and data.get("decrypt") == "true":
            return mockr.MockSuccess(**kwargs)
        return mockr.MockError(**kwargs)
    return mockr.MockNotFound(**kwargs)


def get_file(*args, **kwargs):
    """Send mocked response for getting file."""
    data = kwargs.get("params", {})
    if mockr.is_endpoint(f"/api/1.0/object/{mockr.MOCK_OBJECT_ID}", args[0]):
        if (
            mockr.has_valid_token(**kwargs)
            and data.get("decrypt") == "true"
            and data.get("filedata") == "true"
        ):
            return mockr.MockSuccess(**kwargs)
        return mockr.MockError(**kwargs)
    return mockr.MockNotFound(**kwargs)


def get_mime_type(*args, **kwargs):
    """Send mocked response for getting file mime type."""
    data = kwargs.get("json", {})
    if mockr.is_endpoint("/api/1.0/utils/get_mime_type", args[0]):
        if (
            mockr.has_valid_token(**kwargs)
            and data.get("size") == 128
            and data.get("extension") == mockr.MOCK_FILE_EXTENSION
            and data.get("data") == b64encode(mockr.MOCK_FILE_CONTENT[:64]).decode("utf-8")
        ):
            return mockr.MockSuccess(**kwargs)
        return mockr.MockError(**kwargs)
    return mockr.MockNotFound(**kwargs)

def filecollect(*args, **kwargs):
    """Send mocked response for filecollect."""
    files = kwargs.get("files", {})
    if mockr.is_endpoint("/api/1.0/filecollect", args[0]):
        if (
            mockr.has_valid_token(**kwargs)
            and files.get("upload")[0].endswith(mockr.MOCK_FILE_EXTENSION)
            and files.get("upload")[1] == mockr.MOCK_FILE_CONTENT[:64]
        ):
            return mockr.MockSuccess(**kwargs)
        return mockr.MockError(**kwargs)
    return mockr.MockNotFound(**kwargs)

def file_upload(*args, **kwargs):
    """Send mocked response for filecollect."""
    data = kwargs.get("data", {})
    files = kwargs.get("files", {})
    # Close file pointer since requests isn't doing it due to mock
    content = files.get('upload').read()
    files.get('upload').close()
    if mockr.is_endpoint("/api/1.0/object", args[0]):
        if (
            mockr.has_valid_token(**kwargs)
            and data == mockr.MOCK_FILE_PARAMS
            and files.get("upload").name.endswith(mockr.MOCK_FILE_EXTENSION)
            and files.get("upload").mode == "rb"
            and content == mockr.MOCK_FILE_CONTENT
        ):
            return mockr.MockSuccess(**kwargs)
        return mockr.MockError(**kwargs)
    return mockr.MockNotFound(**kwargs)


def create_object(*args, **kwargs):
    """Send mocked response for creating an object."""
    data = kwargs.get("json", {})
    if mockr.is_endpoint("/api/1.0/object", args[0]):
        if mockr.has_valid_token(**kwargs) and data == mockr.MOCK_PARAMS:
            return mockr.MockSuccess(**kwargs)
        return mockr.MockError(**kwargs)
    return mockr.MockNotFound(**kwargs)


def edit_object(*args, **kwargs):
    """Send mocked response for editing an object."""
    data = kwargs.get("json", {})
    if mockr.is_endpoint(f"/api/1.0/object/{mockr.MOCK_OBJECT_ID}", args[0]):
        if mockr.has_valid_token(**kwargs) and data == mockr.MOCK_PARAMS:
            return mockr.MockSuccess(**kwargs)
        return mockr.MockError(**kwargs)
    return mockr.MockNotFound(**kwargs)


def delete_object(*args, **kwargs):
    """Send mocked response for deleting an object."""
    if mockr.is_endpoint(f"/api/1.0/object/{mockr.MOCK_OBJECT_ID}", args[0]):
        if mockr.has_valid_token(**kwargs):
            return mockr.MockSuccess(**kwargs)
        return mockr.MockError(**kwargs)
    return mockr.MockNotFound(**kwargs)


def find(*args, **kwargs):
    """Send mocked response for finding objects."""
    data = kwargs.get("params", {})
    if mockr.is_endpoint("/api/1.0/find", args[0]):
        if mockr.has_valid_token(**kwargs) and data.get("needle") == mockr.MOCK_NEEDLE:
            return mockr.MockSuccess(**kwargs)
        return mockr.MockError(**kwargs)
    return mockr.MockNotFound(**kwargs)
