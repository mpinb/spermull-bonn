import random
import math
from datetime import datetime, timedelta
import pandas as pd
from isf_pandas_msgpack import read_msgpack
import os

wd = os.path.dirname(__file__)
DATA_DIR = os.path.abspath(os.path.join(wd, "..", "data"))
DF_PATH = os.path.join(DATA_DIR, "geo_dates.msg")

def read_df():
    return read_msgpack(DF_PATH)

def get_lat_lon_from_date(
    start_date: str,
    end_date: str,
    ):
    """Get geolocation from a date range"""
    lat_lon = read_df().loc[
        (slice(start_date, end_date), slice(None)), :
        ].rename(
        columns={"LAT": "lat", "LON": "lng"}
        ).reset_index(
        level='date'
        )
    lat_lon['date'] = lat_lon['date'].astype(str)
    return lat_lon.to_dict('records')


def generate_points_around_location(lat, lng, start_date_str, end_date_str, radius_km=10, num_points=15):
    """
    Generate random points within a radius of the provided location.
    
    Args:
        lat (float): Latitude of center point
        lng (float): Longitude of center point
        start_date_str (str): Start date in YYYY-MM-DD format
        end_date_str (str): End date in YYYY-MM-DD format
        radius_km (float): Radius in kilometers
        num_points (int): Number of points to generate
        
    Returns:
        list: List of dictionaries with generated points
    """
    # Convert dates to datetime objects
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    
    # Calculate date range in days
    date_range = (end_date - start_date).days + 1
    
    # Earth's radius in km
    earth_radius = 6371.0
    
    points = []
    for _ in range(num_points):
        # Generate a random angle and distance within the radius
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, radius_km)
        
        # Convert distance to radians
        distance_in_radians = distance / earth_radius
        
        # Calculate new coordinates
        new_lat = math.asin(
            math.sin(math.radians(lat)) * math.cos(distance_in_radians) +
            math.cos(math.radians(lat)) * math.sin(distance_in_radians) * math.cos(angle)
        )
        new_lng = math.radians(lng) + math.atan2(
            math.sin(angle) * math.sin(distance_in_radians) * math.cos(math.radians(lat)),
            math.cos(distance_in_radians) - math.sin(math.radians(lat)) * math.sin(new_lat)
        )
        
        # Convert back to degrees
        new_lat = math.degrees(new_lat)
        new_lng = math.degrees(new_lng)
        
        # Generate a random date within the range
        random_days = random.randint(0, date_range - 1)
        point_date = start_date + timedelta(days=random_days)
        
        # Add the point to our list
        points.append({
            'lat': new_lat,
            'lng': new_lng,
            'date': point_date.strftime('%Y-%m-%d'),
            'title': f"Event on {point_date.strftime('%b %d, %Y')}"
        })
    
    return points