#!/usr/bin/env python3
import os
import requests

from config import GOOGLE_API_KEY
from urllib.parse import urlencode
from fastmcp import FastMCP

mcp = FastMCP("Sample MCP Server")

def get_address_details(address: str) -> dict:
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": GOOGLE_API_KEY}

    response = requests.get(base_url, params=params, timeout=10).json()
    
    longitude = response['results'][0]['geometry']['location']['lng']
    latitude = response['results'][0]['geometry']['location']['lat']
    formatted_address = response['results'][0]['formatted_address']

    return {
        "latitude": latitude,
        "longitude": longitude,
        "address": formatted_address
    }

def generate_uber_link(details: dict) -> str:
    address = details["address"]
    base_url = "uber://?"
    params = {
        "action": "setPickup",
        "pickup": "my_location",
        "dropoff[formatted_address]": address,
        "dropoff[latitude]": details["latitude"],
        "dropoff[longitude]": details["longitude"],
    }

    url = base_url + urlencode(params)
    return url

@mcp.tool(description="Get the URL link to book an Uber ride to a given address from current location")
def get_uber_booking_link(address: str) -> str:
    details = get_address_details(address)
    return generate_uber_link(details)

@mcp.tool(description="Estimate user's longitude/latitude")
def get_user_position() -> list:
    url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={GOOGLE_API_KEY}"
    
    payload = {
        "homeMobileCountryCode": 310,
        "homeMobileNetworkCode": 410,
        "radioType": "gsm",
        "carrier": "Vodafone",
        "considerIp": True
    }

    headers = {"Content-Type": "application/json"}

    resp = requests.post(url, json=payload, headers=headers, timeout=10)

    if resp.status_code != 200:
        raise RuntimeError(f"Geolocation API error: {resp.status_code}, {resp.text}")

    data = resp.json()
    print("Latitude:", data["location"]["lat"])
    print("Longitude:", data["location"]["lng"])
    print("Accuracy (meters):", data["accuracy"])
    return [data["location"]["lat"], data["location"]["lng"], data["accuracy"]]

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"Starting FastMCP server on {host}:{port}")
    
    mcp.run(
        transport="http",
        host=host,
        port=port,
        stateless_http=True
    )