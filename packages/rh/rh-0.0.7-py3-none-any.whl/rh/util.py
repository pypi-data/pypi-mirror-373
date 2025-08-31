"""
Utility functions for the RH framework.
"""

import http.server
import socketserver
import threading
import time
from pathlib import Path


def serve_directory(directory: str, port: int = 8080, host: str = "localhost"):
    """Serve a directory using Python's built-in HTTP server.

    Args:
        directory: Directory to serve
        port: Port to serve on
        host: Host to bind to
    """
    import os
    import webbrowser

    # Change to the directory to serve
    original_dir = os.getcwd()
    try:
        os.chdir(directory)

        class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
            """HTTP request handler that suppresses log messages."""

            def log_message(self, format, *args):
                pass  # Suppress default logging

        with socketserver.TCPServer((host, port), QuietHTTPRequestHandler) as httpd:
            url = f"http://{host}:{port}"
            print(f"Serving {directory} at {url}")
            print("Press Ctrl+C to stop the server")

            # Open browser automatically
            try:
                webbrowser.open(url)
            except Exception:
                pass  # Don't fail if browser can't be opened

            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nServer stopped.")

    finally:
        os.chdir(original_dir)


def _find_free_port(start_port: int = 8080) -> int:
    """Find a free port starting from the given port.

    Args:
        start_port: Port to start searching from

    Returns:
        First available port number
    """
    import socket

    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue

    raise RuntimeError(f"No free ports found starting from {start_port}")


class PluginRegistry:
    """Registry for managing optional tool plugins."""

    def __init__(self):
        """Initialize the plugin registry."""
        self._handlers = {}
        self._auto_register()

    def register(self, tool_type: str, handler_class, priority: int = 0):
        """Manual registration for custom handlers.

        Args:
            tool_type: Type of tool (e.g., 'template', 'bundler')
            handler_class: Handler class to register
            priority: Priority (higher number = higher priority)
        """
        if tool_type not in self._handlers:
            self._handlers[tool_type] = []

        self._handlers[tool_type].append((priority, handler_class))
        self._handlers[tool_type].sort(key=lambda x: x[0], reverse=True)

    def _auto_register(self):
        """Detect and register third-party tools automatically."""
        # Try to register enhanced tools if available
        if self._has_package('jinja2'):
            # Would register Jinja2Handler if implemented
            pass
        if self._has_package('esbuild'):
            # Would register ESBuildHandler if implemented
            pass

    def _has_package(self, package_name: str) -> bool:
        """Check if a package is available for import.

        Args:
            package_name: Name of the package to check

        Returns:
            True if package is available
        """
        try:
            __import__(package_name)
            return True
        except ImportError:
            return False

    def get_handler(self, tool_type: str):
        """Return highest-priority available handler.

        Args:
            tool_type: Type of tool to get handler for

        Returns:
            Handler class or None if no handler available
        """
        handlers = self._handlers.get(tool_type, [])
        return handlers[0][1] if handlers else None
