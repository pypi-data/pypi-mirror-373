"""Korea Geocoder MCP Server

A Model Context Protocol (MCP) server for geocoding Korean addresses
using Google Maps Geocoding API.
"""

from .geocoder import main

__version__ = "0.1.0"
__all__ = ["main"]