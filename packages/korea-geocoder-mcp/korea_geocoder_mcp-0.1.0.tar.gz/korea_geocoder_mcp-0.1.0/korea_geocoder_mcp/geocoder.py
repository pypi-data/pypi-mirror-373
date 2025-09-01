#!/usr/bin/env python3
"""
Geocoder with MCP Server
주소를 받아서 위도/경도를 반환하는 기능과 MCP 서버
"""

import googlemaps
import os
from fastmcp import FastMCP

API_KEY = os.environ.get('GOOGLE_CLOUD_API_KEY')

# MCP 서버 인스턴스 생성
mcp = FastMCP("Geocoder")


@mcp.tool()
def get_coordinates(address: str) -> dict:
    """
    주소를 받아서 위도와 경도를 반환합니다.
    
    Args:
        address: 지오코딩할 주소 (한국 주소)
    
    Returns:
        dict: 위도와 경도 정보 또는 오류 메시지
    """
    try:
        gmaps = googlemaps.Client(key=API_KEY)
        geocode_result = gmaps.geocode(address + ", 대한민국")
        
        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            lat, lng = location['lat'], location['lng']
            
            return {
                "success": True,
                "address": address,
                "latitude": lat,
                "longitude": lng
            }
        else:
            return {
                "success": False,
                "error": "주소를 찾을 수 없습니다.",
                "address": address
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"지오코딩 중 오류가 발생했습니다: {str(e)}",
            "address": address
        }


def main():
    """Entry point for the MCP server."""
    mcp.run(transport="stdio")


if __name__ == '__main__':
    main()
