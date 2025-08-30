import base64
import hashlib
import os
import threading
from abc import ABC, abstractmethod
from typing import Optional, Tuple

import featureform as ff
import requests
from flask import Flask, request
from typeguard import typechecked
from werkzeug.serving import make_server
import yaml
import time
from okta_jwt_verifier import JWTUtils


@typechecked
class AuthConfig(ABC):
    @abstractmethod
    def get_authorization_endpoint(self, redirect_uri: str, code_challenge: str) -> str:
        pass

    @abstractmethod
    def get_token_exchange_endpoint(self) -> str:
        pass


@typechecked
class OktaAuthConfig(AuthConfig):
    def __init__(
        self, domain: str, authorization_server_id: str, client_id: str
    ) -> None:
        self.domain = domain
        self.authorization_server_id = authorization_server_id
        self.client_id = client_id

    def get_authorization_endpoint(self, redirect_uri: str, code_challenge: str) -> str:
        return (
            f"https://{self.domain}/oauth2/v1/authorize?client_id={self.client_id}"
            f"&response_type=code&scope=openid%20offline_access&redirect_uri={redirect_uri}&state=random_state"
            f"&code_challenge_method=S256&code_challenge={code_challenge}"
        )

    def get_token_exchange_endpoint(self) -> str:
        return f"https://{self.domain}/oauth2/v1/token"

    def get_native_exchange_endpoint(self) -> str:
        return f"https://{self.domain}/oauth2/v1/token?client_id={self.client_id}"
    
    # caveat: uses our custom auth server (enabled by developer account)
    # default org servers don't allow modifying any internal scopes, 
    # and the client credentials flow requires custom auth servers to do so
    def get_machine_exchange_endpoint(self) -> str:
        return f"https://{self.domain}/oauth2/default/v1/token"

    def get_token_refresh_endpoint(self) -> str:
        return f"https://{self.domain}/oauth2/v1/token?client_id={self.client_id}"

@typechecked
class CidrAuthConfig(AuthConfig):
    def __init__(self) -> None:
        pass

    def get_authorization_endpoint(self, redirect_uri: str, code_challenge: str) -> str:
        pass

    def get_token_exchange_endpoint(self) -> str:
        pass


@typechecked
class AuthService(ABC):
    def __init__(self, auth_config) -> None:
        self._auth_config = auth_config

    @abstractmethod
    def authenticate(self) -> None:
        pass

    @abstractmethod
    def refresh_token(self, refresh_token) -> None:
        pass

    @abstractmethod
    def get_access_dict(self) -> Optional[dict]:
        pass

    @abstractmethod
    def clear_access_token(self) -> None:
        pass


@typechecked
class PassThroughService(AuthService):
    def authenticate(self) -> None:
        pass

    def refresh_token(self, _) -> None:
        pass

    def get_access_dict(self) -> Optional[dict]:
        pass

    def clear_access_token(self) -> None:
        pass


@typechecked
class CidrService(AuthService):
    def authenticate(self) -> None:
        pass

    def refresh_token(self, _) -> None:
        pass

    def get_access_dict(self) -> Optional[dict]:
        pass

    def clear_access_token(self) -> None:
        pass


@typechecked
class OktaOAuth2PKCE(AuthService):
    def __init__(self, auth_config: OktaAuthConfig) -> None:
        super().__init__(auth_config)
        # up casts the instance in this class to OktaAuthConfig
        self._auth_config: OktaAuthConfig = auth_config
        self.redirect_uri = "http://localhost:9080/authorization-code/callback"
        self._access_token = None
        self._refresh_token = None
        self._access_token_expires = None
        self._code_verifier = None
        self._callback_server = None
        self._callback_server_thread = None
        self._callback_flask_app = Flask(__name__)
        self._auth_completed = threading.Event()

        @self._callback_flask_app.route("/authorization-code/callback")
        def callback():
            auth_code = request.args.get("code")
            threading.Thread(
                target=self._exchange_code_for_token, args=(auth_code,)
            ).start()
            return "Authentication successful! You can close this window."

    def authenticate(self) -> None:
        self._code_verifier = self._create_code_verifier()
        code_challenge = self._create_code_challenge(self._code_verifier)
        auth_url = self._auth_config.get_authorization_endpoint(
            self.redirect_uri, code_challenge
        )
        print(f"Please visit the following URL to authenticate: {auth_url}")
        self._callback_server_thread = threading.Thread(
            target=self._start_callback_server
        )
        self._callback_server_thread.start()
        self._auth_completed.wait()

    def refresh_token(self, refresh_token) -> None:
        new_token = self._request_refresh_token(refresh_token)

        if new_token:
            print("Token Refreshed!")
        else:
            raise Exception("Failed to refresh access_token")

    def get_access_dict(self) -> Optional[dict]:
        return {
            "access_token": self._access_token,
            "refresh_token": self._refresh_token,
            "access_token_expires": self._access_token_expires,
        }

    def _request_refresh_token(self, refresh_token) -> Optional[str]:
        print("Refreshing Token...")
        headers = {
            "Accept": "application/json",
        }
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "scope": "openid offline_access",
        }
        response = requests.post(
            self._auth_config.get_token_refresh_endpoint(),
            headers=headers,
            data=data,
        )

        if response.status_code == 200:
            json_resp = response.json()
            if json_resp:
                self._access_token = json_resp.get("access_token")
                self._refresh_token = json_resp.get("refresh_token")
                self._access_token_expires = int(time.time()) + int(
                    json_resp.get("expires_in")
                )
        else:
            print(f"PKCE failed to get refresh_token: {response.status_code}")
            self._access_token = None
            self._refresh_token = None
            self._access_token_expires = None

        return self._access_token

    def clear_access_token(self) -> None:
        self._auth_completed.clear()
        self._access_token = None
        self._refresh_token = None
        self._access_token_expires = None

    @staticmethod
    def _create_code_verifier():
        token = base64.urlsafe_b64encode(os.urandom(40)).decode("utf-8")
        return token.rstrip("=")

    @staticmethod
    def _create_code_challenge(verifier):
        m = hashlib.sha256()
        m.update(verifier.encode("utf-8"))
        challenge = base64.urlsafe_b64encode(m.digest()).decode("utf-8")
        return challenge.rstrip("=")

    def _exchange_code_for_token(self, auth_code):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        data = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": self.redirect_uri,
            "client_id": self._auth_config.client_id,
            "code_verifier": self._code_verifier,
            "scope": "openid offline_access",
        }
        try:
            response = requests.post(
                self._auth_config.get_token_exchange_endpoint(),
                headers=headers,
                data=data,
            )
            if response.status_code == 200:
                print("Authentication Succeeded!")
                json_resp = response.json()
                if json_resp:
                    self._access_token = json_resp.get("access_token")
                    self._refresh_token = json_resp.get("refresh_token")
                    self._access_token_expires = self._access_token_expires = int(
                        time.time()
                    ) + int(json_resp.get("expires_in"))
                self._auth_completed.set()
            else:
                raise Exception("Authentication Failed.")
        finally:
            self._stop_callback_server()

    def _start_callback_server(self):
        self._callback_server = make_server("127.0.0.1", 9080, self._callback_flask_app)
        self._callback_server.serve_forever()

    def _stop_callback_server(self):
        if self._callback_server:
            self._callback_server.shutdown()


@typechecked
class OktaOAuthNative(AuthService):
    def __init__(self, auth_config) -> None:
        super().__init__(auth_config)
        self._access_token = None
        self._access_token_expires = None
        self._refresh_token = None

    def authenticate(self) -> None:
        # attempt to use env vars, then cred file
        username = os.environ.get("FF_OKTA_USERNAME")
        password = os.environ.get("FF_OKTA_PASSWORD")

        if username and password:
            print("Using cred vars...")
            self._access_token = self._request_token(
                username=username, password=password
            )
        else:
            print("Using cred file...")
            cred_dict = self._pull_file_creds()
            if cred_dict is not None:
                self._access_token = self._request_token(
                    username=cred_dict.get("username"),
                    password=cred_dict.get("password"),
                )
            else:
                print("No user credentials for okta app found in Environment")
                return None

        if self._access_token:
            print("Authentication Succeeded!")
        else:
            raise Exception("Failed to authenticate with user credentials")

    def refresh_token(self, refresh_token) -> None:
        new_token = self._request_refresh_token(refresh_token)

        if new_token:
            print("Token Refreshed!")
        else:
            raise Exception("Failed to refresh access_token")

    def get_access_dict(self) -> Optional[dict]:
        return {
            "access_token": self._access_token,
            "refresh_token": self._refresh_token,
            "access_token_expires": self._access_token_expires,
        }

    def clear_access_token(self) -> None:
        self._access_token = None
        self._refresh_token = None
        self._access_token_expires = None

    def _request_token(self, username: str, password: str) -> Optional[str]:
        headers = {
            "Accept": "application/json",
        }
        data = {
            "grant_type": "password",
            "username": username,
            "password": password,
            "scope": "openid offline_access",
        }
        response = requests.post(
            self._auth_config.get_native_exchange_endpoint(),
            headers=headers,
            data=data,
        )

        if response.status_code == 200:
            json_resp = response.json()
            if json_resp:
                self._access_token = json_resp.get("access_token")
                self._refresh_token = json_resp.get("refresh_token")
                self._access_token_expires = int(time.time()) + int(
                    json_resp.get("expires_in")
                )
        else:
            print(f"Native failed to get access_token: {response.status_code}")
            try:
                json_resp = response.json()
                print(json_resp)
            except ValueError as e:
                print(f"Failed to parse JSON response: {e}")
            self._access_token = None
            self._refresh_token = None
            self._access_token_expires = None

        return self._access_token

    def _request_refresh_token(self, refresh_token) -> Optional[str]:
        print("Refreshing Token...")
        headers = {
            "Accept": "application/json",
        }
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "scope": "openid offline_access",
        }
        response = requests.post(
            self._auth_config.get_token_refresh_endpoint(),
            headers=headers,
            data=data,
        )

        if response.status_code == 200:
            json_resp = response.json()
            if json_resp:
                self._access_token = json_resp.get("access_token")
                self._refresh_token = json_resp.get("refresh_token")
                self._access_token_expires = int(time.time()) + int(
                    json_resp.get("expires_in")
                )
        else:
            print(f"Native failed to get refresh_token: {response.status_code}")
            try:
                json_resp = response.json()
                print(json_resp)
            except ValueError as e:
                print(f"Failed to parse JSON response: {e}")
            self._refresh_token = None
            self._access_token_expires = None

        return self._access_token

    def _pull_file_creds(self) -> Optional[dict]:
        featureform_path = os.environ.get("FEATUREFORM_DIR", ".featureform")
        auth_path = os.path.join(featureform_path, "auth")
        credential_file_path = os.path.join(auth_path, "credentials.yaml")

        if os.path.exists(credential_file_path):
            with open(credential_file_path, "r") as file:
                file_dict = yaml.safe_load(file)
                cred_dict = file_dict.get("okta")
                return cred_dict
        else:
            print("File path does not exist")
            return None

@typechecked
class OktaOAuth2ClientCredentials(AuthService):
    def __init__(self, auth_config) -> None:
        super().__init__(auth_config)
        self._access_token = None
        self._access_token_expires = None

    def authenticate(self) -> None:
        api_client_id = os.environ.get("FF_API_CLIENT_ID")
        api_client_secret = os.environ.get("FF_API_CLIENT_SECRET")

        if not api_client_id or not api_client_secret:
            print("No api client credentials found in Environment, falling back to user and password...")
            return None
        
        auth_header = base64.b64encode(f"{api_client_id}:{api_client_secret}".encode()).decode()

        print("API client and secret set, using client credentials flow...")
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Cache-Control": "no-cache",
        }
        data = {
            "grant_type": "client_credentials",
            "scope": "api.access"
        }
        response = requests.post(
            self._auth_config.get_machine_exchange_endpoint(), headers=headers, data=data
        )


        if response.status_code == 200:
            json_resp = response.json()
            if json_resp:
                self._access_token = json_resp.get("access_token")
                self._access_token_expires = int(time.time()) + int(json_resp.get("expires_in"))
        else:
            print(f"API Credentials failed to get access_token: {response.status_code}")
            try: 
                json_resp = response.json()
                print(json_resp)
            except ValueError as e:
                print(f"Failed to parse JSON response: {e}")
            self._access_token = None
            self._access_token_expires = None
        
        if self._access_token:
            print("Authentication Succeeded!")
        else:
            print("Failed to authenticate with api client credentials")

    def get_access_dict(self) -> Optional[dict]:
        return {
            "access_token": self._access_token,
            "refresh_token": None, # none for api credentials
            "access_token_expires": self._access_token_expires,
        }
    def refresh_token(self, _) -> None:
        print("api client credentials...reauthenticating...")
        self.authenticate()

    def clear_access_token(self) -> None:
        self._access_token = None
        self._access_token_expires = None

@typechecked
class AuthenticationManagerImpl:
    TOKEN_FILENAME = "token.yaml"

    def __init__(self) -> None:
        self._access_token = None
        self._refresh_token = None
        self._access_token_expires = None

        self._auth_config = None
        self._services = []
        feature_form_dir = os.environ.get("FEATUREFORM_DIR", ".featureform")
        self.auth_dir = os.path.join(feature_form_dir, "auth")
        os.makedirs(self.auth_dir, exist_ok=True)
        self.token_filepath = os.path.join(self.auth_dir, self.TOKEN_FILENAME)

    def _write_token_dict_to_file(
        self,
        token_dict: dict,
    ):
        with open(self.token_filepath, "w") as file:
            yaml.dump(token_dict, file)
        os.chmod(self.token_filepath, 0o600)

    def _read_token_dict_from_file(self) -> Optional[dict]:
        if os.path.exists(self.token_filepath):
            with open(self.token_filepath, "r") as file:
                file_dict = yaml.safe_load(file)
                return file_dict
        return {}

    def delete_expired_token(self):
        self._access_token = None
        self._refresh_token = None
        self._access_token_expires = None

        for service in self._services:
            service.clear_access_token()
        feature_form_dir = os.environ.get("FEATUREFORM_DIR", ".featureform")
        auth_dir = os.path.join(feature_form_dir, "auth")

        token_filepath = os.path.join(
            auth_dir, AuthenticationManagerImpl.TOKEN_FILENAME
        )
        if os.path.exists(token_filepath):
            os.remove(token_filepath)

    def get_access_token_or_authenticate(self, insecure, host) -> Optional[dict]:
        token_dict = self._read_token_dict_from_file()
        if token_dict:
            self._access_token = token_dict.get("access_token")
            self._refresh_token = token_dict.get("refresh_token")
            self._access_token_expires = token_dict.get("access_token_expires")

        if self._access_token:
            if (
                isinstance(self._access_token_expires, int)
                and int(time.time()) > self._access_token_expires
            ):
                if not self._services:
                    self._auth_config = self._load_auth_config(insecure, host)
                    if self._auth_config is not None:
                        self._services = [
                            OktaOAuth2ClientCredentials(self._auth_config),
                            OktaOAuthNative(self._auth_config),
                            OktaOAuth2PKCE(self._auth_config)
                        ]
                    else:
                        self._services = [PassThroughService(self._auth_config)]
                for service in self._services:
                    service.refresh_token(self._refresh_token)
                    token_dict = service.get_access_dict()
                    if token_dict and token_dict.get("access_token"):
                        self._access_token = token_dict.get("access_token")
                        self._refresh_token = token_dict.get("refresh_token")
                        self._access_token_expires = token_dict.get(
                            "access_token_expires"
                        )
                        self._write_token_dict_to_file(token_dict)
                        break
        elif not self._access_token:
            if not self._services:
                self._auth_config = self._load_auth_config(insecure, host)
                self._add_services()

            for service in self._services:
                service.authenticate()
                token_dict = service.get_access_dict()
                if token_dict and token_dict.get("access_token"):
                    self._access_token = token_dict.get("access_token")
                    self._refresh_token = token_dict.get("refresh_token")
                    self._access_token_expires = token_dict.get("access_token_expires")
                    self._write_token_dict_to_file(token_dict)
                    break

        resultDict = {
            "token": None,
            "refreshToken": None,
            "subject": None,
        }
        if self._access_token:
            parsed_token = JWTUtils.parse_token(self._access_token)
            if len(parsed_token) != 4:
                raise Exception("Invalid access token, cannot parse the sub property!")
            payload = parsed_token[1]
            resultDict["token"] = self._access_token
            resultDict["refreshToken"] = self._refresh_token
            resultDict["subject"] = payload.get("sub")

        return resultDict

    def get_subject(self, config, insecure, host) -> Optional[str]:
        self._auth_config = self._init_auth_config(config)
        self._add_services()

        if len(self._services) == 1 and isinstance(
            self._services[0], PassThroughService
        ):
            return "default_user"
        elif len(self._services) == 1 and isinstance(self._services[0], CidrService):
            return "allowed_cidr_user"
        else:
            sub = None
            resultDict = self.get_access_token_or_authenticate(insecure, host)
            if resultDict["token"] is not None:
                parsed_token = JWTUtils.parse_token(resultDict["token"])
                if len(parsed_token) != 4:
                    raise Exception("Invalid access token")
                payload = parsed_token[1]
                sub = payload.get("sub")

                # set the appropriate subject from the token
                api_client_id = os.environ.get("FF_API_CLIENT_ID")
                if api_client_id and sub == api_client_id:
                    sub = f"machine-{sub}"
                    print(f"Identified machine user: {sub}")
            return sub

    def _load_auth_config(self, insecure, host) -> Optional[OktaAuthConfig]:
        config = ff.Client(insecure=insecure, host=host).get_auth_config()
        return self._init_auth_config(config)

    def _init_auth_config(self, config) -> Optional[AuthConfig]:
        if config.WhichOneof("config") == "okta":
            okta_config = config.okta
            return OktaAuthConfig(
                domain=okta_config.domain,
                authorization_server_id=okta_config.authorization_server_id,
                client_id=okta_config.client_id,
            )
        elif config.WhichOneof("config") == "cidr":
            return CidrAuthConfig()
        elif config.WhichOneof("config") == "pass_through":
            return None
        else:
            raise Exception("Unsupported auth config")

    def _add_services(self):
        if isinstance(self._auth_config, OktaAuthConfig):
            self._services = [
                OktaOAuth2ClientCredentials(self._auth_config),
                OktaOAuthNative(self._auth_config),
                OktaOAuth2PKCE(self._auth_config)
            ]
        elif isinstance(self._auth_config, CidrAuthConfig):
            self._services = [CidrService(self._auth_config)]
        else:
            self._services = [PassThroughService(self._auth_config)]


singleton = AuthenticationManagerImpl()
