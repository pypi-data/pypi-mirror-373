import base64
import hashlib
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

AUTH_STATE = {
    "received_callback": False,
    "code": None,
    "error_message": None,
    "received_state": None,
}


class SimpleServer(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _html(self, message):
        content = f"<html><body><h1>{message}</h1></body></html>"
        return content.encode("utf8")

    def do_GET(self):
        if "/callback?" not in self.path:
            return

        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)

        self._set_headers()
        self.wfile.write(self._html("Please return to your application now."))

        AUTH_STATE["error_message"] = params.get("error", [""])[0]
        AUTH_STATE["code"] = params.get("code", [""])[0]
        AUTH_STATE["received_state"] = params.get("state", [""])[0]
        AUTH_STATE["received_callback"] = True


class ServerThread(threading.Thread):
    """
    The simple server is done this way to allow shutting down after a single request has been received.
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self.srv = HTTPServer(("127.0.0.1", 64242), SimpleServer)

    def run(self):
        self.srv.serve_forever()

    def shutdown(self):
        self.srv.shutdown()


def auth0_url_encode(byte_data):
    """
    Safe encoding handles + and /, and also replace = with nothing
    :param byte_data:
    :return:
    """
    return base64.urlsafe_b64encode(byte_data).decode("utf-8").replace("=", "")


def generate_challenge(a_verifier):
    return auth0_url_encode(hashlib.sha256(a_verifier.encode()).digest())
