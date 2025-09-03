# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite - HTTP Server Module
=========================

This module provides a simple HTTP server implementation using Python's
built-in http.server library.

"""


# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

import logging
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

# Import | Standard Library
from typing import List

# Import | Libraries

# Import | Local Modules


# =============================================================================
# Classes
# =============================================================================


class BaseHTTPServer(BaseHTTPRequestHandler):
    """
    HTTP Server Class
    =================

    A simple HTTP server handler class that responds to GET and POST requests.

    Attributes
    ----------
        None

    Methods
    -------
        do_get(): Handle GET requests.
        do_post(): Handle POST requests.
        _send_response(status_code, content, content_type): Helper method to
        send HTTP responses.
        _handle_404(): Helper method to handle 404 Not Found responses.
        run(server_class, handler_class, port): Static method to run the
        server.
    """

    def do_get(self):
        """
        Handle GET requests. Parses the request path and query parameters.

        Returns
        -------
            None
        """
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query = urllib.parse.parse_qs(parsed_path.query)

        logging.info(
            "GET request,\nPath: %s\nQuery: %s\nHeaders:\n%s",
            path,
            query,
            self.headers,
        )

        if path == "/":
            self._send_response(
                200, "<h1>Welcome to the Python HTTP Server</h1>", "text/html"
            )
        elif path == "/info":
            self._send_response(200, str(query), "text/plain")
        else:
            self._handle_404()

    def do_post(self):
        """
        Handle POST requests. Parses the posted data.

        Returns
        -------
            None
        """
        content_length = int(self.headers["Content-Length"])
        post_data = urllib.parse.parse_qs(
            self.rfile.read(content_length).decode("utf-8")
        )

        logging.info(
            "POST request,\nPath: %s\nHeaders:\n%s\nBody:\n%s\n",
            self.path,
            self.headers,
            post_data,
        )

        self._send_response(
            200,
            "<h1>POST request received</h1>",
            "text/html",
        )

    def _send_response(self, status_code, content, content_type):
        """
        Helper method to send HTTP responses.

        Parameters:
            status_code (int): HTTP status code.
            content (str): Response content.
            content_type (str): MIME type of the response content.

        Returns
        -------
            None
        """
        self.send_response(status_code)
        self.send_header("Content-type", content_type)
        self.end_headers()
        if isinstance(content, str):
            content = content.encode("utf-8")
        self.wfile.write(content)

    def _handle_404(self):
        """
        Helper method to handle 404 Not Found responses.

        Returns
        -------
            None
        """
        self._send_response(404, "<h1>404 Not Found</h1>", "text/html")

    @staticmethod
    def run(
        server_class=HTTPServer,
        handler_class=BaseHTTPRequestHandler,
        port=8000,
    ):
        """
        Static method to run the HTTP server.

        Parameters:
            server_class (HTTPServer): The HTTP server class.
            handler_class (BaseHTTPRequestHandler): The HTTP request handler
            class.
            port (int): Port number to run the server on.

        Returns
        -------
            None
        """
        logging.basicConfig(level=logging.INFO)
        server_address = ("", port)
        httpd = server_class(server_address, handler_class)
        logging.info("Starting httpd server on port %d", port)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()
        logging.info("Stopping httpd server")


# =============================================================================
# Exports
# =============================================================================

__all__: List[str] = [
    "BaseHTTPServer",
]


# =============================================================================
# Functions
# =============================================================================


def test():
    """
    Test Function
    """

    # Running the server
    BaseHTTPServer.run(handler_class=HTTPServer, port=8000)


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    import doctest

    doctest.testmod()
    test()
