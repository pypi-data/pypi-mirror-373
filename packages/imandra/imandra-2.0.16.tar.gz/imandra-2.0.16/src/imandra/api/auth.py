import random
import uuid
import json
import os
import os.path

import urllib
import urllib.error
import urllib.parse
import urllib.request

import hashlib
import base64

import shutil
import webbrowser


_get_secrets_chars = b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def _get_secrets():
    rchar = lambda: random.SystemRandom().choice(_get_secrets_chars)
    verifier = bytes(rchar() for _ in range(32))
    challenge = hashlib.sha256(verifier).digest()
    challenge = base64.b64encode(challenge, altchars=b"-_")
    challenge = challenge.replace(b"=", b"")
    return verifier, challenge


class Auth:
    """
    Auth encapsulates authentication information for Imandra's Cloud APIs at
    https://www.imandra.ai/api/. An instance of this class should be passed to
    other ``imandra`` library methods to make calls to Imandra's cloud APIs.
    """

    def __init__(self):
        """
        Construct a new Auth object. This constructor configures the object
        with the locations of the Imandra authentication on your local machine
        (e.g. from ``~/.imandra`` or `%APPDATA%\\imandra`), and the Imandra cloud API
        details.
        """

        # NOTE: config env var handling mimics imandra_network_client

        envs = {
            "dev": {
                "auth0_base_host": "test-ai.eu.auth0.com",
                "auth0_client_id": "DQs4kqaeTPAENZ8dAj64qEm2SbJgncNK",
                "auth0_audience": "https://www.dev.imandracapital.com/api",
                "imandra_web_host": "https://www.dev.imandracapital.com",
                "config_dir_name": "imandra-dev",
                "imandra_repl": "imandra-repl-dev",
                "gcloud_project": "imandra-dev",
            },
            "prod": {
                "auth0_base_host": "auth.imandra.ai",
                "auth0_client_id": "q2yGHBTLmJSia35zCOdkUpEecj9mQl6o",
                "auth0_audience": "https://www.imandra.ai/api",
                "imandra_web_host": "https://www.imandra.ai",
                "config_dir_name": "imandra",
                "imandra_repl": "imandra-repl",
                "gcloud_project": "imandra-prod",
            },
        }

        env = os.getenv("IMANDRA_ENV", "prod")
        self.gcloud_project = envs[env]["gcloud_project"]

        self.auth0_base_host = os.getenv(
            "IMANDRA_AUTH0_BASE_HOST", envs[env]["auth0_base_host"]
        )
        self.auth0_client_id = os.getenv(
            "IMANDRA_AUTH0_CLIENT_ID", envs[env]["auth0_client_id"]
        )
        self.auth0_audience = os.getenv(
            "IMANDRA_AUTH0_AUDIENCE", envs[env]["auth0_audience"]
        )
        self.imandra_web_host = os.getenv(
            "IMANDRA_WEB_HOST", envs[env]["imandra_web_host"]
        )
        self.imandra_repl = envs[env]["imandra_repl"]
        self.http_port = None

        if os.name == "nt":
            user_config_root = os.environ["APPDATA"]
            self.folder_path = os.path.join(
                user_config_root, envs[env]["config_dir_name"]
            )
        else:
            user_config_root = os.environ["HOME"]
            self.folder_path = os.path.join(
                user_config_root, "." + envs[env]["config_dir_name"]
            )

        self.redirect_uri = self.imandra_web_host + "/pkce-callback"
        if self.http_port:
            self.redirect_uri += "?redirect_port=" + str(self.http_port)

    def login(self):
        """
        Ensures that all information is present in order to make calls to the
        API. This method is best run interactively from `imandra-cli`, via
        `imandra auth login`.
        """
        self.ensure_folder()
        self.ensure_token()
        self.ensure_confirm()
        self.ensure_zone()

    def logout(self):
        """
        Remove all Imandra user configuration information on the local machine.
        """
        self.ensure_folder()
        shutil.rmtree(self.folder_path)

    def ensure_folder(self):
        """
        Ensures the existence of the local imandra configuration directory (`~/.imandra` or `%APPDATA%\\imandra`).
        """
        if not os.path.exists(self.folder_path):
            os.mkdir(self.folder_path)

        device_id_path = os.path.join(self.folder_path, "device_id")
        if not os.path.exists(device_id_path):
            self.device_id = str(uuid.uuid4())
            with open(device_id_path, "w") as device_id_file:
                device_id_file.write(self.device_id)
        else:
            with open(device_id_path, "r") as device_id_file:
                self.device_id = device_id_file.read()

    def ensure_token(self):
        """
        Ensures the existence of the local imandra login token. Prompts the user to log in if there isn't one.
        """
        token_path = os.path.join(self.folder_path, "login_token")
        if os.path.exists(token_path):
            with open(token_path, "r") as token_file:
                self.token = token_file.read().strip()
            return

        self.verifier, self.challenge = _get_secrets()
        link = self._make_link()
        print("Trying to open a browser window to authenticate you...")
        show_open_msg = False
        try:
            if not webbrowser.open(link):
                show_open_msg = True
        except webbrowser.Error:
            show_open_msg = True

        if show_open_msg:
            print(
                "We couldn't open the browser automatically! Please visit: \n{}".format(
                    link
                )
            )

        code_str = str(
            input("Once you've authenticated, please enter the code provided: ")
        ).strip()
        self._exchange_tokens(code_str, token_path)

    def ensure_zone(self):
        """
        Ensures the existence of the default zone for creation of Imandra core
        instances. Pick the zone closest to you from those available to reduce
        latency when interacting with Imandra Core instances.
        """
        zone_path = os.path.join(self.folder_path, "zone")
        if os.path.exists(zone_path):
            with open(zone_path, "r") as zone_file:
                self.zone = zone_file.read().strip()
            return

        path = "pod/clusters"
        url = "{}/{}".format(self.imandra_web_host, path)
        headers = {"X-Auth": self.token}

        request = urllib.request.Request(url, headers=headers)

        try:
            response = urllib.request.urlopen(request)
        except urllib.error.HTTPError as e:
            raise ValueError(e.read())
        j = json.loads(response.read())

        options = []
        option_strs = []
        for i, cluster in enumerate(j["clusters"]):
            options.append((i, cluster))
            option_strs.append("[{}] {}".format(str(i + 1), cluster))

        def ask_for_selection():
            query = input("Select cloud zone {} : ".format(" ".join(option_strs)))
            try:
                return int(query) - 1
            except ValueError:
                print("Not a valid selection")
                return ask_for_selection()

        selected_opt_idx = ask_for_selection()
        _, selected_cluster = options[selected_opt_idx]

        with open(zone_path, "w") as zone_file:
            zone_file.write(selected_cluster)

        self.zone = selected_cluster

    def _make_link(self):
        params = urllib.parse.urlencode(
            {
                "audience": self.auth0_audience,
                "response_type": "code",
                "client_id": self.auth0_client_id,
                "code_challenge": self.challenge,
                "code_challenge_method": "S256",
                "redirect_uri": self.redirect_uri,
            }
        )
        return "https://{}/{}?{}".format(self.auth0_base_host, "authorize", params)

    def _prompt_verify_email(self):
        query = input("Enter the verification code we sent to your email: ")
        evrid, token, intention = (
            base64.b64decode(query.encode(), altchars=b"-_").decode("utf8").split(",")
        )
        params = urllib.parse.urlencode(
            {"evrid": evrid, "token": token, "intention": intention}
        )
        url = "{}/{}?{}".format(self.imandra_web_host, "verify-email", params)
        headers = {"X-Device-Id": self.device_id}
        request = urllib.request.Request(url, headers=headers)
        try:
            _ = urllib.request.urlopen(request)
        except urllib.error.HTTPError as e:
            raise ValueError(e.read())

    def _exchange_tokens(self, code_str, token_path):
        tkn = {
            "grant_type": "authorization_code",
            "client_id": self.auth0_client_id,
            "code_verifier": self.verifier.decode("utf-8"),
            "code": code_str,
            "redirect_uri": self.redirect_uri,
        }
        url = "https://{}/{}".format(self.auth0_base_host, "oauth/token")
        data = json.dumps(tkn)
        clen = len(data)
        data = data.encode("utf-8")
        request = urllib.request.Request(
            url, data, {"Content-Type": "application/json", "Content-Length": str(clen)}
        )
        try:
            response = urllib.request.urlopen(request)
        except urllib.error.HTTPError as e:
            raise ValueError(e.read())
        auth_token = json.loads(response.read())
        headers = {
            "Authorization": "Bearer {}".format(auth_token["access_token"]),
            "X-Device-Id": self.device_id,
        }
        url = "{}/{}".format(self.imandra_web_host, "api/login-token-for")
        request = urllib.request.Request(url, headers=headers)
        try:
            response = urllib.request.urlopen(request)
            self.token = response.read().decode("utf-8")

            with open(token_path, "w") as token_file:
                token_file.write(self.token)

        except urllib.error.HTTPError as e:
            content = e.read().decode("utf-8")
            if e.code == 400 and content == "email-not-verified":
                self._prompt_verify_email()
                self.ensure_token()
            else:
                raise ValueError(content)

    def ensure_confirm(self):
        path = "api/user-info"
        url = "{}/{}".format(self.imandra_web_host, path)
        headers = {"X-Auth": self.token}

        request = urllib.request.Request(url, headers=headers)

        try:
            response = urllib.request.urlopen(request)
        except urllib.error.HTTPError as e:
            raise ValueError(e.read())
        j = json.loads(response.read())
        if not j["trial_activated"]:
            query = input("Do you want to start your Imandra trial? [Y/n] ")
            if query == "" or query[0].lower() == "y":
                path = "welcome/activate-trial"
                url = "{}/{}".format(self.imandra_web_host, path)
                request = urllib.request.Request(url, headers=headers)
                try:
                    response = urllib.request.urlopen(request)
                except urllib.error.HTTPError as e:
                    raise ValueError(e.read())
            else:
                raise ValueError("Trial not activated")

    def export(self):
        """
        Export your login details for use via another Imandra Cloud API client.
        """
        token_path = os.path.join(self.folder_path, "login_token")
        zone_path = os.path.join(self.folder_path, "zone")
        on_behalf_of_path = os.path.join(self.folder_path, "on_behalf_of")

        if not os.path.exists(token_path) or not os.path.exists(zone_path):
            raise ValueError("Not logged in")

        details = {}
        with open(token_path, "r") as token_file:
            details["auth"] = token_file.read().strip()

        with open(zone_path, "r") as zone_file:
            details["zone"] = zone_file.read().strip()

        if os.path.exists(on_behalf_of_path):
            with open(on_behalf_of_path, "r") as on_behalf_of_file:
                details["on_behalf_of"] = on_behalf_of_file.read().strip()
        else:
            details["on_behalf_of"] = None

        return details

    def import_(self, details):
        """
        Import your login details from stdin.
        """
        token_path = os.path.join(self.folder_path, "login_token")
        zone_path = os.path.join(self.folder_path, "zone")
        on_behalf_of_path = os.path.join(self.folder_path, "on_behalf_of")

        if details.get("auth"):
            self.ensure_folder()
            with open(token_path, "w") as f:
                f.write(details["auth"])

        if details.get("zone"):
            self.ensure_folder()
            with open(zone_path, "w") as f:
                f.write(details["zone"])

        if details.get("on_behalf_of"):
            self.ensure_folder()
            with open(on_behalf_of_path, "w") as f:
                f.write(details["zone"])
