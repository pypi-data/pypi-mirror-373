from unittest.mock import patch, Mock

import pytest

from featureform.lib import (
    auth,
    OktaAuthConfig,
    OktaOAuthNative,
    OktaOAuth2PKCE,
    OktaOAuth2ClientCredentials
)


def test_okta_auth_config():
    config = OktaAuthConfig("domain.com", "server", "client123")
    expected_endpoint = (
        "https://domain.com/oauth2/v1/authorize?"
        + "client_id=client123&response_type=code&scope=openid%20offline_access&"
        + "redirect_uri=some_uri&state=random_state&code_challenge_method=S256&code_challenge=some_challenge"
    )
    assert (
        config.get_authorization_endpoint("some_uri", "some_challenge")
        == expected_endpoint
    )
    assert config.get_token_exchange_endpoint() == "https://domain.com/oauth2/v1/token"


def test_okta_auth_native_endpoint():
    config = OktaAuthConfig("featureform.test.com", "default", "client123")
    expected_endpoint = (
        "https://featureform.test.com/oauth2/v1/token?client_id=client123"
    )

    assert config.get_native_exchange_endpoint() == expected_endpoint


def test_code_verifier_creation():
    config = OktaAuthConfig("domain.com", "server", "client123")
    service = OktaOAuth2PKCE(config)
    verifier = service._create_code_verifier()
    assert len(verifier) == 54  # This assumes a 40-byte token as input


def test_code_challenge_creation():
    config = OktaAuthConfig("domain.com", "server", "client123")
    service = OktaOAuth2PKCE(config)
    verifier = "some_verifier"
    challenge = service._create_code_challenge(verifier)
    assert len(challenge) <= 44  # Base64 url-safe encoded SHA256


@patch("requests.post")
def test_exchange_code_for_token_success(mock_post):
    config = OktaAuthConfig("domain.com", "server", "client123")
    service = OktaOAuth2PKCE(config)

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "access_token": "some_access_token",
        "refresh_token": "some_refresh_token",
        "expires_in": 3600,
    }
    mock_post.return_value = mock_response

    service._exchange_code_for_token("some_auth_code")
    token_dict = service.get_access_dict()
    assert token_dict.get("access_token") == "some_access_token"
    assert token_dict.get("refresh_token") == "some_refresh_token"
    assert token_dict.get("access_token_expires") is not None

@patch("requests.post")
def test_refresh_token_pkce_success(mock_post):
    config = OktaAuthConfig("domain.com", "server", "client123")
    service = OktaOAuth2PKCE(config)

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "access_token": "new_access_token",
        "refresh_token": "new_refresh_token",
        "expires_in": 3600,
    }
    mock_post.return_value = mock_response

    service.refresh_token("some_refresh_token")
    token_dict = service.get_access_dict()

    assert token_dict.get("access_token") == "new_access_token"
    assert token_dict.get("refresh_token") == "new_refresh_token"
    assert token_dict.get("access_token_expires") is not None


@patch("requests.post")
def test_exchange_code_for_token_fail(mock_post):
    config = OktaAuthConfig("domain.com", "server", "client123")
    service = OktaOAuth2PKCE(config)

    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = {}
    mock_post.return_value = mock_response

    with pytest.raises(Exception) as e:
        service._exchange_code_for_token("some_auth_code")
    assert str(e.value) == "Authentication Failed."

    token_dict = service.get_access_dict()
    assert token_dict.get("access_token") is None
    assert token_dict.get("refresh_token") is None
    assert token_dict.get("access_token_expires") is None


@patch("requests.post")
@patch("os.environ")
def test_native_authenticate_failure(mock_environ, mock_post):
    mock_environ.get.side_effect = ["FF_OKTA_USERNAME", "FF_OKTA_PASSWORD"]
    config = OktaAuthConfig("featureform", "server", "client123")
    service = OktaOAuthNative(config)

    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = {}
    mock_post.return_value = mock_response
    with pytest.raises(Exception) as e:
        service.authenticate()
    assert str(e.value) == "Failed to authenticate with user credentials"

    token_dict = service.get_access_dict()
    assert token_dict.get("access_token") is None
    assert token_dict.get("refresh_token") is None
    assert token_dict.get("access_token_expires") is None


@patch("requests.post")
@patch("os.environ")
def test_native_authenticate_returns_token(mock_environ, mock_post):
    mock_environ.get.side_effect = ["FF_OKTA_USERNAME", "FF_OKTA_PASSWORD"]
    config = OktaAuthConfig("featureform", "server", "client123")
    service = OktaOAuthNative(config)

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "access_token": "some_access_token",
        "refresh_token": "some_refresh_token",
        "expires_in": 3600,
    }
    mock_post.return_value = mock_response

    service.authenticate()

    token_dict = service.get_access_dict()
    assert token_dict.get("access_token") == "some_access_token"
    assert token_dict.get("refresh_token") == "some_refresh_token"
    assert token_dict.get("access_token_expires") is not None


@patch.object(OktaOAuth2PKCE, "authenticate")
@patch.object(OktaOAuth2PKCE, "get_access_token", return_value="token")
@patch.object(
    auth.singleton,
    "_load_auth_config",
    return_value=OktaAuthConfig(
        domain="",
        authorization_server_id="",
        client_id="",
    ),
)
@pytest.mark.skip
def test_authentication_manager_success(
    mock_get_access_token, mock_authenticate, mocked_load
):
    assert auth.singleton._access_token is None
    token = auth.singleton.get_access_token_or_authenticate(insecure=True)

    assert token == "token"
    auth.singleton._access_token = "override_with_cache_token"
    token_cached = auth.singleton.get_access_token_or_authenticate(insecure=True)
    assert token_cached == "override_with_cache_token"


@patch("requests.post")
@patch("os.environ")
def test_client_credentials_success(mock_environ, mock_post):
    mock_environ.get.side_effect = ["client_id", "client_secret"]
    config = OktaAuthConfig("domain.com", "server", "client123")
    service = OktaOAuth2ClientCredentials(config)

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"access_token": "some_access_token", "expires_in": 3600}
    mock_post.return_value = mock_response

    service.authenticate()
    token_dict = service.get_access_dict()
    assert token_dict.get("access_token") == "some_access_token"
    assert token_dict.get("refresh_token") is None
    assert token_dict.get("access_token_expires") is not None


@patch("requests.post")
@patch("os.environ")
def test_client_credentials_fail(mock_environ, mock_post):
    mock_environ.get.side_effect = [None, None]
    config = OktaAuthConfig("domain.com", "server", "client123")
    service = OktaOAuth2ClientCredentials(config)

    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = {}
    mock_post.return_value = mock_response

    service.authenticate()
    token_dict = service.get_access_dict()
    assert token_dict.get("access_token") is None
    assert token_dict.get("refresh_token") is None
    assert token_dict.get("access_token_expires") is None

@patch("os.environ")
def test_client_credentials_missing_env(mock_environ):
    mock_environ.get.side_effect = [None, None]
    config = OktaAuthConfig("domain.com", "server", "client123")
    service = OktaOAuth2ClientCredentials(config)

    service.authenticate()
    token_dict = service.get_access_dict()

    assert token_dict.get("access_token") is None
    assert token_dict.get("refresh_token") is None
    assert token_dict.get("access_token_expires") is None


def execute_dummy_method():
    print("Executing dummy method...")


if __name__ == "__main__":
    access_token = None

    while True:
        print("\nChoose an action:")
        print("1. Execute dummy method")
        print("2. Exit")
        choice = input("> ")

        if choice == "1":
            if not access_token:
                access_token = auth.singleton.get_access_token_or_authenticate(
                    insecure=True
                )
                if not access_token:
                    print("Failed to authenticate.")
                    continue
            execute_dummy_method()

        elif choice == "2":
            break
