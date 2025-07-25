from flask import Blueprint, request, jsonify
from .services.google_places import extract_place_data
from .db import get_connection

routes = Blueprint('routes', __name__)

@routes.route('/ping', methods=['GET'])
def ping():
    return 'pong'

@routes.route('/add', methods=['POST'])
def add():
    data = request.get_json()
    place_id = data.get("google_link")
    tags = data.get("tags", {})
    location = tags.get("location", "")
    food_type = ", ".join(tags.get("food_type", []))
    my_rating = data.get("my_rating")  # new

    # Fetch details from Google Places API
    place_data = extract_place_data(place_id)
    if not place_data:
        return jsonify({"error": "Failed to fetch place details"}), 400

    with get_connection() as conn:
        conn.execute('''
            INSERT INTO restaurants (name, rating, address, timings, place_id, location, food_type, my_rating)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            place_data["name"],
            place_data["rating"],
            place_data["address"],
            place_data["timings"],
            place_id,
            location,
            food_type,
            my_rating
        ))

    return jsonify({"message": "Saved", "name": place_data["name"]}), 200

@routes.route('/restaurant/<place_id>', methods=['DELETE'])
def delete_restaurant(place_id):
    with get_connection() as conn:
        conn.execute('DELETE FROM restaurants WHERE place_id = ?', (place_id,))
    return jsonify({"message": "Restaurant deleted"}), 200

@routes.route('/restaurant/<place_id>', methods=['PUT'])
def update_restaurant(place_id):
    data = request.get_json()
    location = data.get("location", "")
    food_type = ", ".join(data.get("food_type", []))
    my_rating = data.get("my_rating")  # new

    with get_connection() as conn:
        conn.execute('''
            UPDATE restaurants
            SET location = ?, food_type = ?, my_rating = ?
            WHERE place_id = ?
        ''', (location, food_type, my_rating, place_id))

    return jsonify({"message": "Updated"}), 200

@routes.route('/restaurants', methods=['GET'])
def get_restaurants():
    location_filter = request.args.get("location", "").lower()
    food_type_filter = request.args.get("food_type", "").lower()
    rating_filter = request.args.get("my_rating")

    with get_connection() as conn:
        rows = conn.execute('SELECT * FROM restaurants').fetchall()

    restaurants = []
    for row in rows:
        if location_filter and location_filter not in row["location"].lower():
            continue
        if food_type_filter and food_type_filter not in row["food_type"].lower():
            continue
        if rating_filter:
            try:
                if row["my_rating"] is None or int(row["my_rating"]) < int(rating_filter):
                    continue
            except ValueError:
                pass

        restaurants.append({
            "name": row["name"],
            "rating": row["rating"],
            "address": row["address"],
            "timings": row["timings"],
            "google_link": row["place_id"],
            "tags": {
                "location": row["location"],
                "food_type": row["food_type"].split(", ")
            },
            "my_rating": row["my_rating"]  # included in response
        })

    return jsonify(restaurants), 200
