import base64
import hashlib
import http.server
import os
import sys
from typing import Optional
import webbrowser
import requests
import six
from getpass import getpass
from six.moves.urllib import parse
from geodesic.utils import DeferredImport

IPython = DeferredImport("IPython")


class OAuth2Client:
    def __init__(
        self,
        authorization_url: str,
        token_url: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str = "https://seerai.space/authPage",
        scope: list = [],
        audience: str = None,
        insecure_skip_verify: bool = False,
    ):
        """OAuth2Client handles authorization code grant flow for 3rd party oauth2 apps."""
        self.authorization_url = authorization_url
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        if "offline_access" not in self.scope:
            self.scope.append("offline_access")
        self.redirect_uri = redirect_uri
        self.audience = audience
        self.server = None
        self.insecure_skip_verify = insecure_skip_verify

    def print_auth_message(self):
        return self.authenticate()

    def _get_authorization_url(
        self,
        code_challenge: str,
        redirect_uri: Optional[str] = None,
    ):
        """Returns a URL to generate an auth code.

        Args:
            code_challenge: The OAuth2 code challenge
            redirect_uri: The URL to redirect to after authorization.
        """
        params = {
            "client_id": self.client_id,
            "scope": " ".join(self.scope),
            "redirect_uri": redirect_uri or self.redirect_uri,
            "response_type": "code",
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }

        if self.client_secret:
            params["client_secret"] = self.client_secret

        if self.audience:
            params["audience"] = self.audience

        return self.authorization_url + "?" + parse.urlencode(params)

    def _request_token(
        self, auth_code: str, code_verifier: str, redirect_uri: Optional[str] = None
    ) -> str:
        """Uses authorization code to request tokens."""
        request_args = {
            "code": auth_code,
            "client_id": self.client_id,
            "redirect_uri": redirect_uri or self.redirect_uri,
            "grant_type": "authorization_code",
            "code_verifier": code_verifier,
        }
        if self.client_secret:
            request_args["client_secret"] = self.client_secret

        headers = {"content-type": "application/x-www-form-urlencoded"}

        try:
            response = requests.post(
                self.token_url,
                request_args,
                headers=headers,
                verify=(not self.insecure_skip_verify),
            )
            response.raise_for_status()
            return response.json()["refresh_token"]
        except requests.exceptions.HTTPError as e:
            raise Exception("Problem requesting token. Please try again {0}".format(e))
        except ValueError as e:
            raise Exception("Problem decoding token response {0}".format(e))
        except KeyError as e:
            raise Exception("Refresh token not in response {0}".format(e))

    def _in_jupyter_shell(self):
        """Tests if the code is being executed within Jupyter."""
        try:
            import ipykernel.zmqshell

            return isinstance(IPython.get_ipython(), ipykernel.zmqshell.ZMQInteractiveShell)
        except ImportError:
            return False
        except NameError:
            return False

    def _obtain_token(
        self, auth_code=None, code_verifier=None, redirect_uri: Optional[str] = None
    ) -> str:
        """Obtains and writes credentials token based on a authorization code."""
        if not auth_code:
            auth_code = getpass("Enter verification code: ")
        assert isinstance(auth_code, six.string_types)
        return self._request_token(auth_code.strip(), code_verifier, redirect_uri)

    def _display_auth_instructions_with_html(self, auth_url):
        """Displays instructions for authenticating using HTML code."""
        try:
            IPython.display.display(
                IPython.display.HTML(
                    """<p>To authorize access needed by Geodesic, open the following
                URL in a web browser and follow the instructions:</p>
                <p><a href={0}>Click Here To Generate Code</a></p>
                <p>The authorization workflow will generate a code, which you
                should paste in the box below</p>
                """.format(auth_url)
                )
            )
        except NameError:
            print("The IPython module must be installed to use HTML.")
            raise

    def _display_auth_instructions_for_noninteractive(self, auth_url, code_verifier):
        """Displays instructions for authenticating without blocking for user input."""
        print(
            "Paste the following address into a web browser:\n"
            "\n"
            "    {0}\n"
            "\n"
            "On the web page, please authorize access to your "
            "Geodesic using your account and copy the authentication code. "
            "Next authenticate with the following command:\n"
            "\n"
            "    geodesic authenticate --code-verifier={1} "
            "--authorization-code=PLACE_AUTH_CODE_HERE\n".format(
                auth_url, six.ensure_str(code_verifier)
            )
        )

    def _display_auth_instructions_with_print(self, auth_url):
        """Displays instructions for authenticating using a print statement."""
        print(
            "To authorize access needed by Geodesic, open the following "
            "URL in a web browser and follow the instructions. If the web "
            "browser does not start automatically, please manually browse the "
            "URL below.\n"
            "\n"
            "    {0}\n"
            "\n"
            "The authorization workflow will generate a code, which you "
            "should paste in the box below. ".format(auth_url)
        )

    def _start_server(self, port: int):
        """Initializes a web server that handles the OAuth callback."""

        class Handler(http.server.BaseHTTPRequestHandler):
            """Handles the OAuth callback and reports a success page."""

            code: Optional[str] = None

            def do_GET(self) -> None:
                Handler.code = six.moves.urllib.parse.parse_qs(
                    six.moves.urllib.parse.urlparse(self.path).query
                )["code"][0]
                self.send_response(200)
                self.send_header("Content-type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(
                    b"\n\nAuthentication successful!\n\n\n"
                    b"Credentials have been retrieved. Please close this window.\n\n"
                )

            def log_message(self, *_) -> None:
                pass  # Suppresses the logging of request info to stderr.

        class Server:
            server: http.server.HTTPServer
            url: str

            def __init__(self) -> None:
                self.server = http.server.HTTPServer(("localhost", port), Handler)
                self.url = "http://localhost:%s" % self.server.server_address[1]

            def fetch_code(self) -> Optional[str]:
                self.server.handle_request()  # Blocks until a single request arrives.
                self.server.server_close()
                return Handler.code

        self.server = Server()

    def _token_flow(self, code_verifier, code: Optional[str] = None) -> str:
        redirect_uri = None
        if self.server and not code:
            redirect_uri = self.server.url
            code = self.server.fetch_code()  # Waits for OAuth callback.
            # If code is nil, restart auth process without port, restarting old flow
            if code is None:
                print("Automatic authentication failed, falling back to manual auth...")
                return self.authenticate()
        return self._obtain_token(code, code_verifier, redirect_uri)

    def authenticate(
        self,
        cli_authorization_code=None,
        quiet=False,
        cli_code_verifier=None,
        port: int = None,
    ) -> str:
        """Prompts the user to authorize access to Geodesic via OAuth2.

        Args:
            cli_authorization_code: An optional authorization code.  Supports CLI mode,
                where the code is passed as an argument to `geodesic authenticate`.
            quiet: If true, do not require interactive prompts.
            cli_code_verifier: PKCE verifier to prevent auth code stealing.  Must be
                provided if cli_authorization_code is given.
            port: An optional open port. If provided, authentication will attempt to
                use an http server to automatically get the authorization code,
                removing the need to copy-paste. Please note that not all ports may
                be enabled in your OAuth provider's list of allowed callback URLs.
        """
        if cli_authorization_code:
            return self._obtain_token(cli_authorization_code, cli_code_verifier)

        # PKCE.  Generates a challenge that the server will use to ensure that the
        # auth_code only works with Auth0 verifier.  https://tools.ietf.org/html/rfc7636
        code_verifier = _base64param(os.urandom(32))
        code_challenge = _base64param(hashlib.sha256(code_verifier).digest())

        if port:
            # If a port was provided, begin the automatic token fetching flow
            print("Attempting to authenticate and save code automatically...")
            self._start_server(port)
            auth_url = self._get_authorization_url(code_challenge, self.server.url)
            # We can validate if the callback URL is valid by opening the
            # URL: 403 = invalid, 400 = valid
            try:
                six.moves.urllib.request.urlopen(auth_url)
            except Exception:
                _, ex_value, _ = sys.exc_info()
                if "403" in str(ex_value):
                    print("Automatic authentication failed, falling back to manual auth...")
                    self.authenticate()
                    return
            webbrowser.open_new(auth_url)
            return self._token_flow(code_verifier)

        auth_url = self._get_authorization_url(code_challenge)

        if quiet:
            self._display_auth_instructions_for_noninteractive(auth_url, code_verifier)
            webbrowser.open_new(auth_url)
            return

        if self._in_jupyter_shell():
            self._display_auth_instructions_with_html(auth_url)
        else:
            self._display_auth_instructions_with_print(auth_url)

        webbrowser.open_new(auth_url)

        return self._obtain_token(None, code_verifier)  # Will prompt for auth_code.


def _base64param(byte_string):
    """Encodes bytes for use as a URL parameter."""
    return base64.urlsafe_b64encode(byte_string).rstrip(b"=")
