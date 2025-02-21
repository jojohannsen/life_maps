import json
from geopy.geocoders import Nominatim


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
    location_totals = {}
    
    for city in cities:
        if city.lat and city.lon:
            key = get_lat_lon_key(city.lat, city.lon)
            if key not in location_totals:
                # Create new city instance with same properties
                new_city = CityLocation(
                    id=city.id,
                    name=city.name,
                    lat=city.lat,
                    lon=city.lon,
                    years=city.years
                )
                location_totals[key] = new_city
            else:
                # Add years to existing location
                location_totals[key].years += city.years
    
    return list(location_totals.values())

def add_person_markers(sess) -> str:
    """Generate JavaScript code to add markers for all cities with coordinates"""
    from models import city_locs
    
    selected_person = sess['selected_person']
    
    # Initialize users_with_markers if not present
    if 'users_with_markers' not in sess:
        sess['users_with_markers'] = []
    
    apm = ""
    # Only add markers if we haven't already added them for this user
    if selected_person not in sess['users_with_markers']:
        # Modified to use total_year_city_locs
        for city in total_year_city_locs(city_locs()):
            if city.lat and city.lon:
                lat_lon_key = get_lat_lon_key(city.lat, city.lon)
                apm += f"console.log('Adding marker for {json.dumps(selected_person)} at {json.dumps(city.name)}');\n"
                apm += f"add_person_location('{selected_person}', '{lat_lon_key}', map, {city.lat}, {city.lon}, {city.years});\n"
        sess['users_with_markers'].append(selected_person)
    return apm

def get_active_city(sess):
    """Get the currently active city for the current user from session, or first city if none active"""
    from models import city_locs
    
    cities = city_locs()
    if not cities:
        return None
        
    active_city_id = sess.get('active_city_id')
    if active_city_id:
        try:
            return city_locs.get(active_city_id)
        except:
            pass
    
    # If no active city in session or not found, use the first city
    first_city = cities[0]
    sess['active_city_id'] = first_city.id
    return first_city 