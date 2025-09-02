"""StoredSafe API wrapper module."""
from pathlib import Path
from base64 import b64encode
import requests


class RCException(Exception):
    """Failed to read rc file."""


class ApikeyUndefinedException(Exception):
    """Cannot authenticate with StoredSafe API calls because apikey is not defined."""


class TokenUndefinedException(Exception):
    """Cannot use privileged StoredSafe API calls because token is not defined."""


# pylint: disable=too-many-public-methods
class StoredSafe:
    """StoredSafe API wrapper class."""

    @staticmethod
    def from_rc(path=Path.home() / '.storedsafe-client.rc', **requests_options):
        """Create StoredSafe instance from rc-file"""
        config = {}
        try:
            with Path(path).open('r') as rc_file:
                for line in rc_file:
                    [key, value] = line.strip().split(':')
                    if key == 'mysite':
                        config['host'] = value
                    elif key == 'apikey':
                        config['apikey'] = value
                    elif key == 'token':
                        config['token'] = value
        except Exception:
            raise RCException()
        return StoredSafe(**config, **requests_options)

    def __init__(self, host, apikey=None, token=None, version='1.0', **requests_options):
        self.host = host
        self.apikey = apikey
        self.token = token
        self.api_version = version
        self.requests_options = requests_options

    ###
    # Helper methods.
    ##
    def __assert_apikey_exists(self):
        """Throws ApikeyUndefinedException if token is None."""
        if self.apikey is None:
            raise ApikeyUndefinedException()

    def __headers(self, requests_options, token=True):
        """Create the required headers for requests to the StoredSafe API and merge with options."""
        headers = {
            **self.requests_options.get('headers', {}),
            **requests_options.get('headers', {})}
        if token:
            self.__assert_token_exists()
            headers['X-Http-Token'] = self.token
        return headers

    def __auth(self, data, mtls=False, **requests_options):
        """Authenticate with StoredSafe and save token if the request was successful."""
        self.__assert_apikey_exists()
        res = requests.post(
            self.__get_url('/auth', mtls), **{
            **self.requests_options,
            **requests_options,
            'headers': self.__headers(requests_options, False)
            }, json=data)
        if res.status_code == 200:
            data = res.json()
            self.token = data['CALLINFO']['token']
        return res


    def __assert_token_exists(self):
        """Throws TokenUndefinedException if token is None."""
        if self.token is None:
            raise TokenUndefinedException()

    def __get_url(self, path, mtls=False):
        """Get the full url of the relative API path."""
        port = mtls and ':8443' or ''
        return f'https://{self.host}{port}/api/{self.api_version}/{path.strip("/")}'

    def __get(self, path, params=None, mtls=False, **requests_options):
        """Send a GET request to the provided relative API path."""
        self.__assert_token_exists()
        args = {
            **self.requests_options,
            **requests_options,
            'headers': self.__headers(requests_options)
        }
        if params is not None:
            args['params'] = params
        return requests.get(
            self.__get_url(path, mtls), **args)

    def __post(self, path, data={}, mtls=False, **requests_options):
        """Send a POST request to the provided relative API path."""
        self.__assert_token_exists()
        return requests.post(
            self.__get_url(path, mtls), **{
                **self.requests_options,
                **requests_options,
                'headers': self.__headers(requests_options)
            }, json=data)

    def __put(self, path, data={}, mtls=False, **requests_options):
        """Send a PUT request to the provided relative API path."""
        self.__assert_token_exists()
        return requests.put(
            self.__get_url(path, mtls), **{
                **self.requests_options,
                **requests_options,
                'headers': self.__headers(requests_options)
            }, json=data)

    def __delete(self, path, mtls=False, **requests_options):
        """Send a DELETE request to the provided relative API path."""
        self.__assert_token_exists()
        return requests.delete(
            self.__get_url(path, mtls), **{
                **self.requests_options,
                **requests_options,
                'headers': self.__headers(requests_options)
            })

    def __post_file(self, path, file, data={}, mtls=False, **requests_options):
        """Send a POST request to the provided relative API path."""
        self.__assert_token_exists()
        return requests.post(
            self.__get_url(path, mtls), **{
                **self.requests_options,
                **requests_options,
                'headers': self.__headers(requests_options)
            }, files={'upload': file}, data=data)

    ###
    # API Auth methods.
    ##
    def login_totp(self, username, passphrase, otp, requests_options={}):
        """Request login using TOTP."""
        data = {
            'username': username,
            'passphrase': passphrase,
            'otp': otp,
            'apikey': self.apikey,
            'logintype': 'totp',
        }
        return self.__auth(data, **requests_options)

    def login_yubikey(self, username, passphrase, otp, requests_options={}):
        """Request login using Yubico OTP."""
        data = {
            'username': username,
            'keys': f'{passphrase}{self.apikey}{otp}',
            'apikey': self.apikey,
        }
        return self.__auth(data, **requests_options)

    def login_smartcard(self, username, passphrase, cert, key, requests_options={}):
        """Request login using mTLS"""
        data = {
            'username': username,
            'passphrase': passphrase,
            'apikey': self.apikey,
            'logintype': 'smartcard',
        }
        return self.__auth(data, mtls=True, cert=(cert, key), **requests_options)

    def logout(self, requests_options={}):
        """Request logout."""
        return self.__get('/auth/logout', **requests_options)

    def check(self, requests_options={}):
        """Request check status of session."""
        return self.__post('/auth/check', **requests_options)

    ###
    # API Vault methods.
    ##
    def list_vaults(self, requests_options={}):
        """Request a list of all vaults."""
        return self.__get('/vault', **requests_options)

    def vault_objects(self, vault_id, requests_options={}):
        """Request a list of the objects in a vault."""
        return self.__get(f'/vault/{vault_id}', **requests_options)

    def vault_members(self, vault_id, requests_options={}):
        """Request a list of the members in a vault."""
        return self.__get(f'/vault/{vault_id}/members', **requests_options)

    def add_vault_member(self, vault_id, user_id, status, requests_options={}):
        """Request to add a member to a vault."""
        return self.__post(f'/vault/{vault_id}/member/{user_id}', {'status': status}, **requests_options)

    def edit_vault_member(self, vault_id, user_id, status, requests_options={}):
        """Request to edit a member in a vault."""
        return self.__put(f'/vault/{vault_id}/member/{user_id}', {'status': status}, **requests_options)

    def remove_vault_member(self, vault_id, user_id, requests_options={}):
        """Request to remove a member from a vault."""
        return self.__delete(f'/vault/{vault_id}/member/{user_id}', **requests_options)

    def create_vault(self, requests_options={}, **params):
        """Request the creation of a new vault."""
        return self.__post('/vault', params, **requests_options)

    def edit_vault(self, vault_id, requests_options={}, **params):
        """Request an edit of an existing vault."""
        return self.__put(f'/vault/{vault_id}', params, **requests_options)

    def delete_vault(self, vault_id, requests_options={}):
        """Request the deletion of a vault."""
        return self.__delete(f'/vault/{vault_id}', **requests_options)

    ###
    # API Object methods.
    ##
    def get_object(self, object_id, children=False, requests_options={}):
        """Request a StoredSafe object and optionally its children."""
        return self.__get(f'/object/{object_id}', {'children': 'true' if children else 'false'}, **requests_options)

    def decrypt_object(self, object_id, requests_options={}):
        """Request the decryption of a StoredSafe object."""
        return self.__get(f'/object/{object_id}', {'decrypt': 'true'}, **requests_options)

    def create_object(self, requests_options={}, **params):
        """Request the creation of an object."""
        return self.__post('/object', params, **requests_options)

    def edit_object(self, object_id, requests_options={}, **params):
        """Request the edit of an existing object."""
        return self.__put(f'/object/{object_id}', params, **requests_options)

    def delete_object(self, object_id, requests_options={}):
        """Request the deletion of an object."""
        return self.__delete(f'/object/{object_id}', **requests_options)

    def find(self, needle, requests_options={}):
        """Request all objects with searchable fields matching the needle."""
        return self.__get('/find', {'needle': needle}, **requests_options)

    ###
    # API File (Object) methods.
    ##
    def get_mime_type(self, file, requests_options={}, **params):
        """Check the mime type of the file and get the max upload size."""
        data = {}
        path = Path(file)
        data['extension'] = path.suffix
        data['size'] = path.stat().st_size
        with open(file, 'rb') as f:
            data['data'] = b64encode(f.read(64)).decode("utf-8")
        return self.__post('/utils/get_mime_type', { **data, **params }, **requests_options)

    def filecollect(self, file, requests_options={}, **params):
        """Request the appropriate template for the file."""
        path = Path(file)
        with path.open('rb') as f:
            data = f.read(64)
        return self.__post_file('/filecollect', (path.name, data), params, **requests_options)

    def upload_file(self, file, requests_options={}, **params):
        """Request the creation of a file object."""
        if not params.get('templateid'):
            params['templateid'] = 3
        return self.__post_file('/object', open(file, 'rb'), params, **requests_options)

    def get_file(self, object_id, requests_options={}):
        """Request a base64 string of a file object."""
        return self.__get(f'/object/{object_id}', {'decrypt': 'true', 'filedata': 'true'}, **requests_options)


    ###
    # API Templates methods.
    ##
    def list_templates(self, requests_options={}):
        """Request a list of all available templates."""
        return self.__get('/template', **requests_options)

    def get_template(self, template_id, requests_options={}):
        """Request a StoredSafe template."""
        return self.__get(f'/template/{template_id}', **requests_options)

    ###
    # API User methods
    ##
    def list_users(self, search_string=None, requests_options={}):
        """Request list of all users or any users matching search string."""
        if search_string is None:
            return self.__get('/user', **requests_options)
        return self.__get(f'/user/{search_string}', **requests_options)

    def get_user(self, user_id, requests_options={}):
        """Request user matching the user_id."""
        return self.__get(f'/user/{user_id}', **requests_options)

    def create_user(self, requests_options={}, **params):
        """Request the creation of a new user."""
        return self.__post('/user', params, **requests_options)

    def edit_user(self, user_id, requests_options={}, **params):
        """Request the creation of a new user."""
        return self.__put(f'/user/{user_id}', params, **requests_options)

    def delete_user(self, user_id, requests_options={}):
        """Request the creation of a new user."""
        return self.__delete(f'/user/{user_id}', **requests_options)

    def get_user_certificate(self, user_id, requests_options={}):
        """Request the user certificate used for mTLS"""
        return self.__get(f'/usercert/{user_id}', **requests_options)

    def set_user_certificate(self, user_id, cert_path, requests_options={}):
        """Request a new user certificate for mTLS to be added to the user"""
        files = {'user_cert': open(cert_path, 'rb')}
        return self.__post(f'/usercert/{user_id}', files=files, **requests_options)

    def remove_user_certificate(self, user_id, requests_options={}):
        """Request the user certificate for mTLS to be removed from user"""
        return self.__delete(f'/usercert/{user_id}', **requests_options)

    ###
    # API Utils methods.
    ##
    def status_values(self, requests_options={}):
        """Request a list of all available capabilities and permission bits."""
        return self.__get('/utils/statusvalues', **requests_options)

    def password_policies(self, requests_options={}):
        """Request a list of all available password policies."""
        return self.__get('/utils/policies', **requests_options)

    def version(self, requests_options={}):
        """Request the version of the StoredSafe server."""
        return self.__get('/utils/version', **requests_options)

    def generate_password(self, requests_options={}, **params):
        """Request a password generated with the passed settings (or vault policy)."""
        return self.__get('/utils/pwgen', params, **requests_options)
