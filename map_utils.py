import json
from geopy.geocoders import Nominatim


geolocator = Nominatim(user_agent="my_app")

def get_lat_lon_key(lat: float, lon: float) -> str:
    """Takes lat/lon and gives uniform format for dictionary keys"""
    return f"{lat:.2f},{lon:.2f}"

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
        for city in city_locs():
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