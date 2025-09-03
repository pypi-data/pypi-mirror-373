import threading
from typing import TypedDict

from flask import Flask, request
from werkzeug.serving import make_server


class AuthErrorMessage(TypedDict):
    error: str
    description: str


class SecurityError(Exception):
    pass


class ServerThread(threading.Thread):
    app: Flask
    port: int

    def __init__(self, app: Flask, port: int):
        threading.Thread.__init__(self)
        self.app = app
        self.port = port

    def run(self):
        self.srv = make_server("127.0.0.1", self.port, self.app)
        self.srv.serve_forever()

    def shutdown(self):
        self.srv.shutdown()


class AuthServer:
    app: Flask
    port: int
    server: ServerThread

    # Random string used to validate that the response corresponds to the user's request
    expected_state: str

    # Values returned by auth0
    auth_code: str | None = None
    auth_error: AuthErrorMessage | None = None

    def __init__(self, expected_state: str, port: int):
        self.app = Flask(__name__)
        self.port = port

        self.server = ServerThread(self.app, port)

        self.expected_state = expected_state

        @self.app.route("/callback")
        def callback():
            """React to the auth redirect and extract the auth code or any errors."""

            if "error" in request.args:
                self.auth_error = AuthErrorMessage(
                    error=request.args["error"],
                    description=request.args["error_description"],
                )
                return f"Authentication failed - {self.auth_error['error']}:{self.auth_error['description']}"

            if request.args["state"] != self.expected_state:
                raise SecurityError("State returned by auth0 did not match expected state")

            self.auth_code = request.args["code"]

            return "Please return to your application now."

    def start(self) -> None:
        self.server.start()

    def stop(self) -> None:
        self.server.shutdown()

    def callback_received(self) -> bool:
        """Starts returning True as soon as the auth callback is received (successfully or not)."""
        return any((self.auth_code is not None, self.auth_error is not None))
