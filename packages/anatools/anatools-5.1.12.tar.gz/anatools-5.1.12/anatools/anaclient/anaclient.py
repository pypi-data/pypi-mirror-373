"""The client module is used for connecting to Rendered.ai's Platform API."""
import webbrowser
import http.server
import socketserver
import threading
import urllib
from urllib.parse import urlparse, parse_qs
import hashlib
import base64

envs = {
    'prod': {
        'name': 'Rendered.ai Platform',
        'url':  'https://deckard.rendered.ai',
        'statusAPI': 'https://api.rendered.ai/system',
        'api':  'https://api.rendered.ai/graphql',
        'auth': 'https://keycloak.rendered.ai' },
    'test': {
        'name': 'Rendered.ai Test Platform',
        'url':  'https://deckard.test.rendered.ai',
        'statusAPI': 'https://api.test.rendered.ai/system',
        'api':  'https://api.test.rendered.ai/graphql',
        'auth': 'https://keycloak.test.rendered.ai' },
    'dev': {
        'name': 'Rendered.ai Development Platform',
        'url':  'https://deckard.dev.rendered.ai/',
        'statusAPI': 'https://api.dev.rendered.ai/system',
        'api':  'https://api.dev.rendered.ai/graphql',
        'auth': 'https://keycloak.dev.rendered.ai' }
}

class AuthFailedError(Exception):
    """Custom exception for authentication failures."""
    pass

class client:

    def __init__(self, email=None, password=None, APIKey=None, bearer_token=None, environment=None, endpoint=None, local=False, interactive=True, verbose=None):
        from anatools.anaclient.api import api
        from anatools.lib.print import print_color
        from datetime import datetime
        import getpass
        import yaml
        import os
        import requests
        import anatools
        import time
        self.verbose = verbose
        self.interactive = interactive
        self.__bearer_token = bearer_token or os.environ.get('RENDEREDAI_BEARER_TOKEN')

        # check home directory for api key
        # Priority: Bearer Token -> API Key -> Email/Password
        if self.__bearer_token:
            pass # Handled after endpoint setup
        elif email is None and APIKey is None and os.environ.get('RENDEREDAI_API_KEY') is None:
            if os.path.exists(os.path.expanduser('~/.renderedai/config.yaml')):
                with open(os.path.expanduser('~/.renderedai/config.yaml'), 'r') as f:
                    config = yaml.safe_load(f)
                    if environment == None or environment == config['environment']:
                        APIKey = config['apikey']
                        environment = config['environment']
                        if self.interactive: print_color("Loaded API Key from ~/.renderedai/config.yaml", '91e600')

        # check environment
        if environment: self.environment = environment.lower()
        elif os.environ.get('RENDEREDAI_ENVIRONMENT'): self.environment = os.environ.get('RENDEREDAI_ENVIRONMENT').lower()
        else: self.environment = 'prod'
        if self.environment not in envs.keys():  raise Exception("Invalid environment argument.")

        # set client endpoints
        if local:
            os.environ['NO_PROXY'] = '127.0.0.1'
            self.__url = 'http://127.0.0.1:3000/graphql'
            self.__status_url = None
            self.__environment = 'Local'
            if self.interactive: print_color(f"Local is set to: {self.__url}", 'ffff00')
        elif endpoint:
            self.__url = endpoint
            self.__status_url = None
            self.__environment = 'Rendered.ai'
        elif os.environ.get('RENDEREDAI_ENDPOINT'):
            self.__url = os.environ.get('RENDEREDAI_ENDPOINT')
            self.__status_url = None
            self.__environment = 'Rendered.ai'
        else:
            self.__url = envs[self.environment]['api']
            self.__status_url = envs[self.environment]['statusAPI']
            self.__environment = envs[self.environment]['name']

        # Determine headers for API client
        initial_headers = None
        if self.__bearer_token:
            initial_headers = {'Authorization': f'Bearer {self.__bearer_token}'}

        self.ana_api = api(self.__url, self.__status_url, initial_headers, self.verbose)

        # initialize client variables
        self.__logout = False
        self.user = None
        self.organizations = None
        self.organization = None
        self.workspaces = None
        self.workspace = None
        self.channels = {}
        self.volumes = {}
        self.auth_method = None

        # configure client context
        if self.__bearer_token:
            try:
                # Fetch user context using the bearer token
                # This relies on getCurrentUserContext being available in self.ana_api (via api_keys.py)
                # and that it handles token errors via the errorhandler.
                user_context = self.ana_api.getCurrentUserContext()
                if not user_context or 'userId' not in user_context:
                    # errorhandler should have already printed a message if it's a token error
                    raise AuthFailedError("Failed to retrieve user context with Bearer Token.")

                self.user = user_context
                if 'userId' in self.user and 'uid' not in self.user:
                    self.user['uid'] = self.user.pop('userId')
                self.user['idtoken'] = self.__bearer_token # Store the token as idtoken for consistency
                # Ensure 'expiresAt' is handled if available from getCurrentUserContext, otherwise it might be None
                if 'expires' in self.user and 'expiresAt' not in self.user : # If 'expires' (duration) is returned
                    self.user['expiresAt'] = time.time() + self.user['expires']

                self.auth_method = 'bearer'
                self.__logout = False
                if self.interactive: print_color(f"Signed into {self.__environment} with Bearer Token.", '91e600')

                # Populate organizations and workspaces (similar to user-scope API key)
                self.organizations = self.get_organizations()
                organization = None
                if not self.organizations:
                    msg = "No organizations found for your account. Please contact support@rendered.ai."
                    if self.interactive: print_color(msg, 'ff0000')
                    raise AuthFailedError(msg)
                self.workspaces = self.get_workspaces()
                workspace = None
                if not self.workspaces:
                    response = input("No workspaces available. Would you like to create a new one? (y/n)")
                    if response.lower() == 'y':
                        self.create_workspace(name="Workspace")
                        self.workspaces = self.get_workspaces(fields=["workspaceId", "name", "organizationId"])
                        workspace = self.workspaces[0]
                        self.workspace = workspace['workspaceId']
                    else: raise Exception("No workspaces available. Please contact support@rendered.ai for support.")

                if os.getenv("RENDEREDAI_WORKSPACE_ID") and os.getenv("RENDEREDAI_WORKSPACE_ID") in [w['workspaceId'] for w in self.workspaces]: self.workspace = os.getenv("RENDEREDAI_WORKSPACE_ID")
                else: self.workspace = self.workspaces[0]['workspaceId']
                workspace = [w for w in self.workspaces if w['workspaceId'] == self.workspace][0] # Default to first workspace
                self.organization = workspace['organizationId']
                organization = [o for o in self.organizations if o['organizationId'] == workspace['organizationId']][0]

                if self.interactive and workspace:
                     print_color(f"The current organization is: {organization['name']}\nThe current workspace is: {workspace['name']}.", '91e600')
                elif self.interactive:
                     print_color(f"Set organization to {organization['name']}\nNo workspace set", 'ffff00')

            except AuthFailedError as e: # Catch specific auth errors from context fetching or setup
                if self.interactive: print_color(str(e), 'ff0000')
                raise
            except Exception as e: # Catch other unexpected errors during bearer token setup
                err_msg = f"An unexpected error occurred during Bearer Token authentication: {e}"
                if self.interactive: print_color(err_msg, 'ff0000')
                # The errorhandler in api.py should catch API call errors (like connection errors)
                # This handles errors in the client-side logic after a potentially successful API call
                raise AuthFailedError(err_msg)

        # If an email is provided, attempt email/password authentication.
        # Otherwise, the flow will fall through and trigger OAuth as the default.
        elif email:
            # The `email` argument is now required to enter this block, so we can remove the interactive prompt.
            self.__email = email
            # If a password is not provided and the session is interactive, prompt for it.
            if password is None and self.interactive:
                self.__password = getpass.getpass('Password: ')
            else:
                self.__password = password
            try:
                self.user = self.ana_api.login(email=self.__email, password=self.__password)
                if self.user: self.auth_method = 'password'
                if not self.user: raise AuthFailedError()
            except AuthFailedError as e:
                # If email/password login fails, print a message but don't raise an error.
                # This allows the client to fall back to the OAuth flow.
                if self.interactive: print_color(f'Failed to login to {self.__environment} with email {self.__email}.', 'ff0000')
                self.user = None
            except requests.exceptions.ConnectionError as e:
                print_color(f'Could not connect to API to login. Try again or contact support@rendered.ai for assistance.', 'ff0000')
                raise AuthFailedError()
            except requests.exceptions.JSONDecodeError as e:
                print_color(f'Failed to login with email {self.__email} and endpoint {self.__url}. Please confirm this is the correct email and endpoint, contact support@rendered.ai for assistance.', 'ff0000')
                raise AuthFailedError()
            self.ana_api = api(self.__url, self.__status_url, {'uid':self.user['uid'], 'Authorization': f'Bearer {self.user["idtoken"]}'}, self.verbose)
            try:
                response = self.ana_api.getSDKCompatibility()
                if response['version'] != anatools.__version__: print_color(response['message'], 'ff0000')
            except:
                if self.verbose: print_color("Failed to check SDK compatibility.", 'ff0000')
            # ask to create an api key if using email/password
            if self.interactive:
                resp = input('Would you like to create an API key to avoid logging in next time? (y/n): ')
                while resp.lower() not in ['y', 'n']:
                    resp = input('Invalid input, please respond with y or n: ')
                if resp.lower() == 'y':
                    print("What kind of scope would you like this API key to have?")
                    print("  [0] User - Full access to all organizations and workspaces you have access to.")
                    print("  [1] Organization - Access to a particular organization and any of it's workspaces.")
                    print("  [2] Workspace - Access to a particular workspace.")
                    resp = input('Please enter the number for the scope: ')
                    while resp.lower() not in ['0', '1', '2']:
                        resp = input('Invalid input, please respond with 0, 1, or 2: ')
                    datestr = datetime.now().isoformat()
                    if resp.lower() == '0':
                        apikey = self.create_api_key(name=f"anatools-{datestr}", scope='user')
                    elif resp.lower() == '1':
                        self.organizations = self.get_organizations()
                        organizations = [org for org in self.organizations if not org['expired']]
                        if len(organizations) == 0: raise Exception("No valid organizations found. Please contact sales@rendered.ai for support.")
                        print("Which organization would you like this API key to be associated with?")
                        for i, org in enumerate(organizations):
                            print(f"  [{i}] {org['name']}")
                        resp = input('Please enter a number for the organization: ')
                        while resp.lower() not in [str(i) for i in range(len(organizations))]:
                            resp = input(f"Invalid input, please respond with a number between 0 and {len(organizations)}: ")
                        self.organization = organizations[int(resp)]['organizationId']
                        apikey = self.create_api_key(name=f"anatools-{datestr}", scope='organization', organizationId=self.organization)
                    else:
                        self.organizations = self.get_organizations()
                        organizations = [org for org in self.organizations if not org['expired']]
                        if len(organizations) == 0: raise Exception("No valid organizations found. Please contact sales@rendered.ai for support.")
                        print("Which organization is the workspace is in?")
                        for i, org in enumerate(organizations):
                            print(f"  [{i}] {org['name']}")
                        resp = input('Please enter a number for the organization: ')
                        while resp.lower() not in [str(i) for i in range(len(organizations))]:
                            resp = input(f"Invalid input, please respond with a number between 0 and {len(organizations)}: ")
                        self.organization = organizations[int(resp)]['organizationId']
                        workspaces = self.get_workspaces(organizationId=self.organization, fields=["workspaceId", "name", "organizationId"])
                        if len(workspaces) == 0: raise Exception("No valid workspaces found in this organization. Please contact sales@rendered.ai for support.")
                        print("Which workspace would you like this API key to be associated with?")
                        for i, workspace in enumerate(workspaces):
                            print(f"  [{i}] {workspace['name']}")
                        resp = input('Please enter a number for the workspace: ')
                        while resp.lower() not in [str(i) for i in range(len(workspaces))]:
                            resp = input(f"Invalid input, please respond with a number between 0 and {len(workspaces)-1}: ")
                        self.workspace = workspaces[int(resp)]['workspaceId']
                        apikey = self.create_api_key(name=f"anatools-{datestr}", scope='workspace', workspaceId=self.workspace)
                    os.makedirs(os.path.expanduser('~/.renderedai'), exist_ok=True)
                    with open(os.path.expanduser('~/.renderedai/config.yaml'), 'w') as f:
                        yaml.dump({'apikey': apikey, 'environment': self.environment}, f)
                    print_color("API Key saved to ~/.renderedai/config.yaml", '91e600')

            if self.organization is None:
                self.organizations = self.get_organizations()
                if len(self.organizations) == 0: raise Exception("No organizations found. Please contact sales@rendered.ai for support.")
                organizations = [org for org in self.organizations if not org['expired']]
                if len(organizations) == 0: raise Exception("No valid organizations found. Please contact sales@rendered.ai for support.")
                self.organization = organizations[0]['organizationId']

            # get workspaces
            self.workspaces = self.get_workspaces(fields=["workspaceId", "name", "organizationId"])
            if self.workspace is None:
                if len(self.workspaces):
                    if os.getenv("RENDEREDAI_WORKSPACE_ID") and os.getenv("RENDEREDAI_WORKSPACE_ID") in [w['workspaceId'] for w in self.workspaces]: self.workspace = os.getenv("RENDEREDAI_WORKSPACE_ID")
                    else: self.workspace = self.workspaces[0]['workspaceId']
                    self.organization = [w for w in self.workspaces if w['workspaceId'] == self.workspace][0]['organizationId']
                else: raise Exception("No workspaces available. Please contact support@rendered.ai for support.")

            if self.interactive and self.workspace:
                workspace = [w for w in self.workspaces if w['workspaceId'] == self.workspace][0]['name']
                organization = [o for o in self.organizations if o['organizationId'] == self.organization][0]['name']
                print_color(f'Signed into {self.__environment} with {self.__email}.\nThe current organization is: {organization}\nThe current workspace is: {workspace}', '91e600')
        else:
            if APIKey or os.environ.get('RENDEREDAI_API_KEY'):
                if APIKey: self.__APIKey = APIKey
                else: self.__APIKey = os.environ.get('RENDEREDAI_API_KEY')
                if self.__APIKey:
                    self.sign_in_apikey()
                    self.auth_method = 'apikey'
                    if self.interactive:
                        print_color(f"Signed into {self.__environment} with API Key.", '91e600')
                        if self.organizations:
                            organization = [o for o in self.organizations if o['organizationId'] == self.organization][0]['name']
                            print_color(f'The current organization is: {organization}', '91e600')
                        if self.workspaces:
                            workspace = [w for w in self.workspaces if w['workspaceId'] == self.workspace][0]['name']
                            print_color(f'The current workspace is: {workspace}', '91e600')
            if not self.user:
                self._authenticate_oauth()


    def sign_in_apikey(self):
        from anatools.anaclient.api import api
        from anatools.lib.print import print_color
        from datetime import datetime
        import anatools
        import os
        import requests

        try:
            self.ana_api = api(self.__url, self.__status_url, {'apikey': self.__APIKey}, self.verbose)
            apikeydata = self.ana_api.getAPIKeyContext(apiKey=self.__APIKey)
            if not apikeydata:
                print_color("Invalid API Key", 'ff0000')
                raise AuthFailedError()
            if apikeydata.get('expiresAt'):
                apikey_date = datetime.strptime(apikeydata['expiresAt'], "%Y-%m-%dT%H:%M:%S.%fZ")
                current_date = datetime.now()
                if apikey_date < current_date:
                    print_color(f"API Key expired at {apikey_date}", 'ff0000')
                    raise AuthFailedError()
            try:
                response = self.ana_api.getSDKCompatibility()
                if response['version'] != anatools.__version__: print_color(response['message'], 'ff0000')
            except:
                if self.verbose: print_color("Failed to check SDK compatibility.", 'ff0000')
        except requests.exceptions.ConnectionError as e:
            raise Exception("Failed to reach Rendered.ai endpoint for login.")

        # workspace scope
        if apikeydata.get('workspaceId'):
            self.workspace = apikeydata['workspaceId']
            self.workspaces = self.get_workspaces(workspaceId=apikeydata['workspaceId'], fields=["workspaceId", "name", "organizationId"])
            self.organization = self.workspaces[0]['organizationId']
            self.user = {'status': 'authenticated_by_apikey'}
            return

        # organization scope
        elif apikeydata.get('organizationId'):
            self.organization = apikeydata['organizationId']
            self.organizations = self.get_organizations(organizationId=self.organization)
            self.workspaces = self.get_workspaces(organizationId=self.organization, fields=["workspaceId", "name", "organizationId"])
            if len(self.workspaces): 
                if os.getenv("RENDEREDAI_WORKSPACE_ID") and os.getenv("RENDEREDAI_WORKSPACE_ID") in [w['workspaceId'] for w in self.workspaces]: self.workspace = os.getenv("RENDEREDAI_WORKSPACE_ID")
                else: self.workspace = self.workspaces[0]['workspaceId']
            else:
                response = input("No workspaces available. Would you like to create a new one? (y/n)")
                if response.lower() == 'y':
                    self.create_workspace(name="Workspace", organizationId=self.organization)
                    self.workspaces = self.get_workspaces(organizationId=self.organization, fields=["workspaceId", "name", "organizationId"])
                    self.workspace = self.workspaces[0]['workspaceId']
                else: raise Exception("No workspaces available. Please contact support@rendered.ai for support.")
            self.user = {'status': 'authenticated_by_apikey'}

        # user scope
        else:
            self.organizations = self.get_organizations()
            if len(self.organizations): self.organization = self.organizations[0]['organizationId']
            else: raise Exception("No organizations found. Please contact sales@rendered.ai for support.")
            self.workspaces = self.get_workspaces(fields=["workspaceId", "name", "organizationId"])
            if len(self.workspaces):
                if os.getenv("RENDEREDAI_WORKSPACE_ID") and os.getenv("RENDEREDAI_WORKSPACE_ID") in [w['workspaceId'] for w in self.workspaces]: self.workspace = os.getenv("RENDEREDAI_WORKSPACE_ID")
                else: self.workspace = self.workspaces[0]['workspaceId']
            else:
                response = input("No workspaces available. Would you like to create a new one? (y/n)")
                if response.lower() == 'y':
                    self.create_workspace(name="Workspace")
                    self.workspaces = self.get_workspaces(fields=["workspaceId", "name", "organizationId"])
                    self.workspace = self.workspaces[0]['workspaceId']
                else: raise Exception("No workspaces available. Please contact support@rendered.ai for support.")
            self.organization = self.workspaces[0]['organizationId']
            self.user = {'status': 'authenticated_by_apikey'}

        validorgs = False
        for org in self.organizations:
            if not org['expired']: validorgs = True
        if not validorgs: raise Exception("No valid organizations found. Please contact sales@rendered.ai for support.")


    def refresh_token(self):
        import time
        from anatools.anaclient.api import api
        from anatools.lib.print import print_color

        # If auth_method is bearer or apikey, or if user is not set, do nothing
        if not hasattr(self, 'auth_method') or self.auth_method in ['bearer', 'apikey'] or not self.user:
            return

        # Existing refresh logic (which implies auth_method == 'password')
        if self.user:
            if int(time.time()) > int(self.user['expiresAt']):
                self.user = self.ana_api.login(self.__email, self.__password)
                self.ana_api = api(self.__url, self.__status_url, {'uid': self.user['uid'], 'Authorization': f'Bearer {self.user["idtoken"]}'}, self.verbose)
                try:
                    notification = self.ana_api.getSystemNotifications()
                    self.__notificationId = notification['notificationId']
                    if notification and notification['notificationId'] != self.__notificationId:
                        self.__notificationId = notification['notificationId']
                        print_color(notification['message'], 'ffff00')
                except requests.exceptions.ConnectionError as e:
                        print_color(f"Could not get notifications: {e}", 'ffff00')


    def check_logout(self):
        if self.__logout: raise Exception('You are currently logged out, login to access the Rendered.ai Platform.')
        self.refresh_token()


    def logout(self):
        """Logs out of the ana sdk and removes credentials from ana."""
        if self.check_logout(): return
        self.__logout = True
        del self.__password, self.__url, self.user


    def login(self, email=None, password=None, environment=None, endpoint=None, local=False, interactive=True, verbose=None):
        """Log in to the SDK.

        Parameters
        ----------
        email: str
            Email for the login. Will prompt if not provided.
        password: str
            Password to login. Will prompt if not provided.
        environment: str
            Environment to log into. Defaults to production.
        endpoint: str
            Custom endpoint to log into.
        local: bool
            Used for development to indicate pointing to local API.
        interactive: bool
            Set to False for muting the login messages.
        verbose: str
            Flag to turn on verbose logging. Use 'debug' to view log output.

        """
        self.__init__( email, password, environment, endpoint, local, interactive, verbose)


    def _authenticate_oauth(self):
        """
        Handles the OAuth2 authentication flow with PKCE.
        """
        from anatools.lib.print import print_color
        import os
        import requests
        import time

        client_id = 'anatools'
        realm = 'renderedai'
        keycloak_url = envs[self.environment]['auth']

        if not all([client_id, realm, keycloak_url]):
            if self.interactive:
                print_color("OAuth configuration is missing. Skipping OAuth flow.", 'ff0000')
            return

        # PKCE code verifier and challenge
        code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode('utf-8').rstrip('=')
        code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode('utf-8')).digest()).decode('utf-8').rstrip('=')

        redirect_uri = "http://localhost:9090"
        redirect_uri_enc = urllib.parse.quote(redirect_uri, safe='')
        auth_url = (f"{keycloak_url}/realms/{realm}/protocol/openid-connect/auth?"
                    f"client_id={client_id}&"
                    f"response_type=code&"
                    f"redirect_uri={redirect_uri_enc}&"
                    f"scope=openid%20email%20profile&"
                    f"code_challenge={code_challenge}&"
                    f"code_challenge_method=S256")

        print_color("No other authentication methods found, attempting to login via your browser.", 'ffff00')
        print_color(f"If your browser does not open automatically, please open this URL in your browser: \n{auth_url}", "91e600")
        webbrowser.open(auth_url)

        auth_code = [None]

        class OAuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
            def log_message(self, format, *args):
                # Suppress default HTTP server logging
                return

            def do_GET(self):
                parsed_path = urlparse(self.path)
                query_params = parse_qs(parsed_path.query)
                if 'code' in query_params:
                    auth_code[0] = query_params['code'][0]
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b"<html><body><h1>Login successful!</h1><p>You can close this window.</p></body></html>")
                else:
                    self.send_response(400)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b"<html><body><h1>Login failed.</h1><p>No authorization code found.</p></body></html>")

                threading.Thread(target=self.server.shutdown).start()

        # Allow address reuse to prevent "Address already in use" errors
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer(("", 9090), OAuthCallbackHandler) as httpd:
            httpd.serve_forever()

        if auth_code[0]:
            token_url = f"{keycloak_url}/realms/{realm}/protocol/openid-connect/token"
            token_data = {
                'grant_type': 'authorization_code',
                'client_id': client_id,
                'code': auth_code[0],
                'redirect_uri': redirect_uri,
                'code_verifier': code_verifier  # Add verifier for PKCE
            }

            try:
                if self.verbose == 'debug':
                    print_color(f"DEBUG: Token Request URL: {token_url}", '91e600')
                    print_color(f"DEBUG: Token Request Payload: {token_data}", '91e600')

                token_r = requests.post(token_url, data=token_data)

                if self.verbose == 'debug' and token_r.status_code != 200:
                    print_color(f"DEBUG: Token Error Response: {token_r.text}", 'ff0000')

                token_r.raise_for_status()
                token_json = token_r.json()
                self.__bearer_token = token_json['access_token']
                self.ana_api.headers['Authorization'] = f'Bearer {self.__bearer_token}'

                self.ana_api.session.headers.update(self.ana_api.headers)

                user_context = self.ana_api.getCurrentUserContext()
                if not user_context or 'userId' not in user_context:
                    raise AuthFailedError("Failed to retrieve user context with OAuth Token.")

                self.user = user_context
                if 'userId' in self.user and 'uid' not in self.user:
                    self.user['uid'] = self.user.pop('userId')
                self.user['idtoken'] = self.__bearer_token
                if 'expires_in' in token_json:
                    self.user['expiresAt'] = time.time() + token_json['expires_in']

                self.auth_method = 'oauth'
                self.__logout = False
                if self.interactive: print_color(f"Signed into {self.__environment} with OAuth.", '91e600')

                self.organizations = self.get_organizations()
                if not self.organizations:
                    msg = "No organizations found for your account. Please contact support@rendered.ai."
                    if self.interactive: print_color(msg, 'ff0000')
                    raise AuthFailedError(msg)
                self.workspaces = self.get_workspaces()

            except requests.exceptions.RequestException as e:
                if self.interactive:
                    print_color(f"Failed to exchange authorization code for a token: {e}", "ff0000")
                raise AuthFailedError("OAuth token exchange failed.")

    def get_system_status(self, serviceId=None, display=True):
        """Fetches the system status, if no serviceId is provided it will fetch all services.

        Parameters
        ----------
        serviceId: str
            The identifier of the service to fetch the status of.
        display: bool
            Boolean for either displaying the status or returning as a dict.
        """
        from anatools.lib.print import print_color
        services = self.ana_api.getSystemStatus(serviceId)
        if services and display:
            spacing = max([len(service['serviceName']) for service in services])+4
            print('Service Name'.ljust(spacing, ' ')+'Status')
            for service in services:
                print(service['serviceName'].ljust(spacing, ' '), end='')
                if service['status'] == 'Operational': print_color('Operational', '91e600')
                elif service['status'] == 'Degraded': print_color('Degraded', 'ffff00')
                elif service['status'] == 'Down': print_color('Down', 'ff0000')
                else: print('?')
            return
        return services




    from .organizations import set_organization, get_organizations, edit_organization, get_organization_members, get_organization_invites, add_organization_member, edit_organization_member, remove_organization_member, remove_organization_invitation
    from .workspaces    import set_workspace, get_workspaces, create_workspace, edit_workspace, delete_workspace, mount_workspaces
    from .graphs        import get_graphs, upload_graph, edit_graph, delete_graph, download_graph, get_default_graph, set_default_graph
    from .datasets      import get_datasets, get_dataset_jobs, create_dataset, edit_dataset, delete_dataset, download_dataset, cancel_dataset, upload_dataset, get_dataset_runs, get_dataset_log, get_dataset_files, create_mixed_dataset
    from .channels      import get_channels, get_channel_nodes, create_channel, edit_channel, delete_channel, build_channel, deploy_channel, get_deployment_status, get_channel_documentation, upload_channel_documentation, get_node_documentation
    from .volumes       import get_volumes, get_volumes, create_volume, edit_volume, delete_volume, get_volume_data, edit_volume_data, download_volume_data, upload_volume_data, delete_volume_data, mount_volumes, add_workspace_volumes, remove_workspace_volumes, search_volume
    from .analytics     import get_analytics, download_analytics, get_analytics_types, create_analytics, delete_analytics
    from .annotations   import get_annotations, get_annotation_formats, get_annotation_maps, create_annotation, download_annotation, delete_annotation , get_annotation_maps, create_annotation_map, edit_annotation_map, delete_annotation_map, download_annotation_map
    from .gan           import get_gan_datasets, create_gan_dataset, delete_gan_dataset, get_gan_models, upload_gan_model, delete_gan_model, edit_gan_model, delete_gan_model, download_gan_model
    from .umap          import get_umaps, create_umap, delete_umap
    from .api_keys      import get_api_keys, create_api_key, delete_api_key
    from .llm           import get_llm_response, create_llm_prompt, delete_llm_prompt, get_llm_base_channels, get_llm_channel_node_types
    from .editor        import create_remote_development, delete_remote_development, list_remote_development, stop_remote_development, start_remote_development, prepare_ssh_remote_development, remove_ssh_remote_development, invite_remote_development, get_ssh_keys, register_ssh_key, deregister_ssh_key, get_servers, create_server, delete_server, edit_server, start_server, stop_server
    from .ml            import get_ml_architectures, get_ml_models, create_ml_model, delete_ml_model, edit_ml_model, download_ml_model, upload_ml_model, get_ml_inferences, get_ml_inference_metrics, create_ml_inference, delete_ml_inference, download_ml_inference
    from .inpaint       import get_inpaints, get_inpaint_log, create_inpaint, delete_inpaint
    from .preview       import get_preview, create_preview
    from .image         import get_image_annotation, get_image_mask, get_image_metadata
    from .agents        import get_data_types, get_data_fields
    from .services      import get_service_types, get_services, create_service, edit_service, delete_service, build_service, deploy_service, get_service_deployment, add_workspace_services, remove_workspace_services, get_service_jobs, create_service_job, delete_service_job, delete_service_job, get_workspace_service_credentials, get_instance_types
    from .rules         import get_platform_rules, get_organization_rules, get_workspace_rules, get_service_rules, get_user_rules, edit_organization_rules, edit_workspace_rules, edit_service_rules, edit_user_rules