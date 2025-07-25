import requests
import os
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")


def extract_place_id(input_str):
    """
    Extracts place_id from:
    - a full Google Maps URL like 'https://www.google.com/maps/place/?q=place_id:ChIJxyz...'
    - or a raw place_id directly passed
    """
    if not input_str:
        return None

    if input_str.startswith("ChI"):  # Google place_ids always start with ChI
        return input_str

    parsed = urlparse(input_str)
    query = parse_qs(parsed.query)

    if 'q' in query and query['q'][0].startswith('place_id:'):
        return query['q'][0].split(':')[1]

    if 'placeid' in query:
        return query['placeid'][0]

    return None


def extract_place_data(place_id):
    """
    Uses Google Places API to fetch name, rating, address, timings, etc.
    """
    if not place_id:
        print("No place ID provided.")
        return None

    url = f"https://maps.googleapis.com/maps/api/place/details/json?placeid={place_id}&key={API_KEY}"
    res = requests.get(url)

    if res.status_code != 200:
        print("Google API request failed:", res.text)
        return None

    result = res.json().get("result", {})
    if not result:
        print("No result returned from Google API.")
        return None

    timings_list = result.get("opening_hours", {}).get("weekday_text", [])
    timings = ", ".join(timings_list) if timings_list else "Not Available"

    return {
        "name": result.get("name"),
        "rating": result.get("rating"),
        "address": result.get("formatted_address"),
        "timings": timings,
        "google_link": result.get("url"),
        "place_id": place_id
    }
