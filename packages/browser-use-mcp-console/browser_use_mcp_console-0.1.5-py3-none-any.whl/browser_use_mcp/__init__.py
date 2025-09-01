"""
Browser-Use MCP Server Package

A Model Context Protocol (MCP) server for browser automation using browser-use.
Provides console debugging capabilities for web applications.
"""

__version__ = "0.1.5"
__author__ = "archie"

from .server import main

__all__ = ["main"]