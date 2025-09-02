"""
Define mocked responses mimicking the StoredSafe REST-like API.

Because the wrapper is transparent, the only required return data
is the token on login requests and the HTTP status to indicate whether
the request was correct or not.
"""
MOCK_HOST = "test.storedsafe.com"
MOCK_URL = f"https://{MOCK_HOST}"
MOCK_URL_MTLS = f"https://{MOCK_HOST}:8443"
MOCK_TOKEN = "mock-token"
MOCK_APIKEY = "mock-api-key"
MOCK_USERNAME = "mock-username"
MOCK_PASSPHRASE = "mock-passphrase"
MOCK_OTP = "mock-otp"

MOCK_VAULT_ID = 42
MOCK_OBJECT_ID = 93
MOCK_TEMPLATE_ID = 10
MOCK_USER_ID = 18
MOCK_STATUS = 2
MOCK_NEEDLE = 'Waldo'
MOCK_SEARCH_STRING = 'Nilsson'

MOCK_PUBKEY = '/mock/certs/cert.pem'
MOCK_PRIVKEY = '/mock/certs/cert.key'

MOCK_PARAMS = {'first': 1, 'second': 'two', 'third': True}

MOCK_DEFAULT_OPTIONS = {'option_always': 1,
                        'option_override': 1,
                        'headers': {'x-http-default': 1}}
MOCK_OVERRIDE_OPTIONS = {'option_override': 2,
                         'headers': {'x-http-override': 2}}

MOCK_FILE_SIZE = 128
MOCK_FILE_EXTENSION = ".txt"
MOCK_FILE_CONTENT = b"A"*MOCK_FILE_SIZE
MOCK_FILE_PARAMS = { **MOCK_PARAMS, 'templateid': 3 }


class MockResponse:
    """
    Mimicks a minimal StoredSafe response as presented by the
    requests library.
    """

    def __init__(self, json_data, status_code, **kwargs):
        self.json_data = json_data
        self.status_code = status_code
        self.options = kwargs

    def json(self):
        """Returns the JSON data of the response."""
        return self.json_data


class MockError(MockResponse):
    """MockResponse prepared with error data"""

    def __init__(self, **kwargs):
        super().__init__({}, 403, **kwargs)

class MockNotFound(MockResponse):
    """MockResponse prepared with not found (404) data"""

    def __init__(self, **kwargs):
        super().__init__({}, 404, **kwargs)


class MockLoginSuccess(MockResponse):
    """MockResponse prepared with login data"""

    def __init__(self, **kwargs):
        super().__init__({'CALLINFO': {'token': MOCK_TOKEN}}, 200, **kwargs)


class MockSuccess(MockResponse):
    """MockResponse prepared with success data"""

    def __init__(self, **kwargs):
        super().__init__({}, 200, **kwargs)


def is_endpoint(endpoint, url, mtls=False):
    """Check if the intended enpoint matches the URL"""
    if mtls:
        return url == MOCK_URL_MTLS + endpoint
    return url == MOCK_URL + endpoint


def has_valid_token(**kwargs):
    """Check if a valid token exists in the header"""
    headers = kwargs.get('headers', {})
    return headers.get('X-Http-Token') == MOCK_TOKEN


def has_merged_options(options):
    headers = options.get('headers', {})
    return\
        options.get('option_always') == 1 and\
        options.get('option_override') == 2 and\
        headers.get('x-http-default') == 1 and\
        headers.get('x-http-override') == 2
