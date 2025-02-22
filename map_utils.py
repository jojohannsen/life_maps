import json
from geopy.geocoders import Nominatim
from constants import ACTIVE_CITY_ID_KEY
from models import city_locs,cities_occupied_by_person

geolocator = Nominatim(user_agent="my_app")

def get_lat_lon_key(lat: float, lon: float) -> str:
    """Takes lat/lon and gives uniform format for dictionary keys"""
    return f"{lat:.2f},{lon:.2f}"

def total_year_city_locs(cities):
    """
    Aggregates cities by location and sums their years.
    Returns list of city instances with combined years for duplicate locations.
    
    Args:
        cities: List of city instances
    Returns:
        List of city instances with aggregated years for same locations
    """
    from models import CityLocation
    
    # Dictionary to store unique locations and their total years
    location_to_total_years = {}
    
    for city in cities:
        if city.lat and city.lon:
            key = get_lat_lon_key(city.lat, city.lon)
            if key not in location_to_total_years:
                # Create new city instance with same properties
                new_city = CityLocation(
                    id=city.id,
                    name=city.name,
                    lat=city.lat,
                    lon=city.lon,
                    years=city.years
                )
                location_to_total_years[key] = new_city
            else:
                # Add years to existing location
                location_to_total_years[key].years += city.years
    
    return list(location_to_total_years.values())

def add_person_markers(sess) -> str:
    """Generate JavaScript code to add markers for all cities with coordinates"""
    selected_person = sess['selected_person']
    
    # Initialize users_with_markers if not present
    if 'users_with_markers' not in sess:
        sess['users_with_markers'] = []
    
    apm = ""
    # Only add markers if we haven't already added them for this user
    if selected_person not in sess['users_with_markers']:
        # Modified to use total_year_city_locs
        for city in total_year_city_locs(cities_occupied_by_person(selected_person)):
            if city.lat and city.lon:
                lat_lon_key = get_lat_lon_key(city.lat, city.lon)
                apm += f"add_person_location('{selected_person}', '{lat_lon_key}', map, {city.lat}, {city.lon}, {city.years});\n"
        sess['users_with_markers'].append(selected_person)
    return apm

def get_active_city(sess):
    """Get the currently active city for the current user from session, or first city if none active"""
    cities = city_locs()
    if not cities:
        return None
        
    active_city_id = sess.get(ACTIVE_CITY_ID_KEY)
    if active_city_id:
        try:
            return city_locs.get(active_city_id)
        except:
            pass
    
    # If no active city in session or not found, use the first city
    first_city = cities[0]
    sess[ACTIVE_CITY_ID_KEY] = first_city.id
    return first_city 