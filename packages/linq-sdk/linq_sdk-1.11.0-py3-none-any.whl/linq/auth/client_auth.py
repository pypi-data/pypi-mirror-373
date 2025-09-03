import base64
import datetime
import hashlib
import secrets
import time
import webbrowser
from dataclasses import dataclass
from urllib.parse import urlencode

import requests
from auth0.authentication.token_verifier import AsymmetricSignatureVerifier, TokenVerifier

from ..exceptions import AuthError
from .server import AuthErrorMessage, AuthServer


@dataclass(kw_only=True, slots=True)
class TokenInfo:
    name: str
    locale: str
    iss: str
    aud: str
    iat: datetime.datetime
    exp: datetime.datetime
    sub: str


def validate_token(*, id_token: str, auth0_domain: str, client_id: str) -> TokenInfo:
    jwks_url = "https://{}/.well-known/jwks.json".format(auth0_domain)
    issuer = "https://{}/".format(auth0_domain)
    sv = AsymmetricSignatureVerifier(jwks_url)
    tv = TokenVerifier(signature_verifier=sv, issuer=issuer, audience=client_id)
    decoded = tv.verify(id_token)
    return TokenInfo(
        # TODO: Check if this is okay. For example, can org_id be null?
        name=decoded.get("name", "NO NAME"),
        locale=decoded.get("locale", ""),
        iss=decoded["iss"],
        aud=decoded["aud"],
        iat=datetime.datetime.fromtimestamp(decoded["iat"]),
        exp=datetime.datetime.fromtimestamp(decoded["exp"]),
        sub=decoded["sub"],
    )


def _wait_for_confirmation():
    input("Press enter to open your browser to complete the login.")  # pragma: no cover


def _auth0_url_encode(byte_data: bytes) -> str:
    """Safe encoding handles + and /, and also replace = with nothing"""
    return base64.urlsafe_b64encode(byte_data).decode("utf-8").replace("=", "")


def _generate_auth0_challenge(verifier: str):
    return _auth0_url_encode(hashlib.sha256(verifier.encode()).digest())


def login(*, client_id: str, auth0_domain: str, customer_domain: str) -> tuple[str, TokenInfo]:
    """Get an API token via a login in the browser."""
    redirect_uri = "http://127.0.0.1:5699/callback"

    # Random string used to validate the response belongs to the appropriate request
    state = _auth0_url_encode(secrets.token_bytes(32))

    # Start the local server used to receive the callback
    server = AuthServer(expected_state=state, port=5699)
    server.start()

    verifier = _auth0_url_encode(secrets.token_bytes(32))

    audience = f"https://{customer_domain}"

    url_parameters = {
        "audience": audience,
        "scope": "profile openid email read:clients create:clients read:client_keys",
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "code_challenge": _generate_auth0_challenge(verifier).replace("=", ""),
        "code_challenge_method": "S256",
        "state": state,
    }
    url = f"https://{auth0_domain}/authorize?" + urlencode(url_parameters)

    _wait_for_confirmation()
    webbrowser.open(url, new=2, autoraise=True)

    # Wait for the user to go through the authentication flow
    while not server.callback_received():
        time.sleep(1)
    server.stop()

    if server.auth_error is not None:
        raise AuthError(message=server.auth_error)

    # Exchange the code for a token
    assert server.auth_code, "No auth code in spite of successful auth, this should never happen."
    token_response = requests.post(
        f"https://{auth0_domain}/oauth/token",
        headers={"Content-Type": "application/json"},
        json={
            "grant_type": "authorization_code",
            "client_id": client_id,
            "code_verifier": verifier,
            "code": server.auth_code,
            "audience": audience,
            "redirect_uri": redirect_uri,
        },
    )

    token_data = token_response.json()
    if token_response.status_code == 200:
        return token_data["access_token"], validate_token(
            id_token=token_data["id_token"],
            auth0_domain=auth0_domain,
            client_id=client_id,
        )

    raise AuthError(
        message=AuthErrorMessage(
            error=token_data["error"],
            description=token_data["error_description"],
        )
    )


def machine_login(
    *, client_id: str, client_secret: str, auth0_domain: str, customer_domain: str
) -> tuple[str, TokenInfo]:
    """Get an API token via machine credentials."""
    audience = f"https://{customer_domain}"

    token_response = requests.post(
        f"https://{auth0_domain}/oauth/token",
        headers={"Content-Type": "application/json"},
        json={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "audience": audience,
        },
    )

    token_data = token_response.json()
    if token_response.status_code == 200:
        return token_data["access_token"], validate_token(
            id_token=token_data["access_token"],
            auth0_domain=auth0_domain,
            client_id=audience,
        )

    raise AuthError(
        message=AuthErrorMessage(
            error=token_data["error"],
            description=token_data["error_description"],
        )
    )
