from fasthtml.common import *
from monsterui.all import *
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import json
import os
import pathlib

# Database setup
pathlib.Path('data').mkdir(exist_ok=True)
DB_PATH = 'data/cities.db'
db = database(DB_PATH)

# UI Constants
CITY_NAV_WIDTH = 'w-48'

class CityLocation:
    id:int; username:str; name:str; lat:float; lon:float; zoomlevel:int; active:bool; years:int

city_locs = db.create(CityLocation, pk='id')
active_user = 'johannes'  # default user
city_locs.xtra(username=active_user)  # Set initial filter
print(f"Active user: {active_user}")
# Create FastHTML app with blue theme and add Mapbox CSS/JS
mapbox_token = os.environ['MAPBOX_TOKEN']
mapbox_css = Link(rel="stylesheet", href="https://api.mapbox.com/mapbox-gl-js/v3.1.2/mapbox-gl.css")
mapbox_js = Script(src="https://api.mapbox.com/mapbox-gl-js/v3.1.2/mapbox-gl.js")
map_init_js = Script(src="/static/js/map-init.js")

app, rt = fast_app(
    db_file=DB_PATH,
    hdrs=[
        Theme.blue.headers(),
        mapbox_css,
        mapbox_js,
        map_init_js
    ]
)

geolocator = Nominatim(user_agent="my_app")

def city_buttons():
    user_city_data = city_locs()
    city_buttons = [make_city_button(city) for city in user_city_data]

    return Div(
        *city_buttons,
        id='city-buttons-container',
        cls='space-y-2'
    )
    
def delete_city_record(city_id: int):
    city_locs.delete(city_id)

def make_city_button(city):
    # Add 'active' class if this is the currently selected city
    button = Button(city.name, 
                   hx_trigger='click',
                   hx_get=f'/change-city/{city.id}',
                   hx_target='#city-buttons-container',  # Changed target to update all buttons
                   cls=f'text-left justify-start hover:bg-muted {CITY_NAV_WIDTH} ' + 
                       ('bg-blue-500 text-white' if getattr(city, 'active', False) else 'bg-blue-50'))
    citybutton = DivLAligned(
        button,
        id=f'citybutton-{city.id}',
    )
    return citybutton

def get_distinct_users():
    result = db.query("select distinct username from city_location")
    return Select(
        *[Option(row['username'], value=row['username']) for row in result],
        name='username',
        hx_trigger='change',
        hx_post='/change-user',
        hx_target='#city-buttons-container',
        hx_swap='outerHTML',
        cls=f'{CITY_NAV_WIDTH} mb-2'
    )

@rt('/change-user')
def change_user(username: str):
    global active_user
    active_user = username
    city_locs.xtra(username=active_user)
    
    # Get active city for the new user
    active_city = get_active_city()
    print(f"Active city: {active_city}")
    
    if active_city:
        # Return both the map update and city buttons
        return Div(
            Script(f"""
                map.flyTo({{
                    center: [{active_city.lon}, {active_city.lat}],
                    zoom: {active_city.zoomlevel},
                    essential: true
                }});
            """),
            city_buttons()
        )
    
    return city_buttons()


@rt('/change-city/{city_id}')
def change_city(city_id: int):
    city = city_locs.get(city_id)
    print(f"Changing city to {city.name}")
    print(f"City: {city}")
    try:
        # Only geocode if lat/lon not already set
        if not city.lat or not city.lon:
            print(f"Geocoding city {city.name}")
            location = geolocator.geocode(city.name)
            if location:
                print(f"Location: {location}")
                city.lat = location.latitude
                city.lon = location.longitude
                city.zoomlevel = 10
                city_locs.update(city)
            else:
                print(f"No location found for {city.name}")
        # Set all cities as inactive and mark the selected one as active
        for c in city_locs():
            c.active = (c.id == city_id)
            print(f"Setting city {c.name} to active: {c.active}")
            city_locs.update(c)
        
        # Return both the map update and the updated button list
        return Div(
            Script(f"""
                {add_person_markers()}
                map.flyTo({{
                    center: [{city.lon}, {city.lat}],
                    zoom: {city.zoomlevel},
                    essential: true
                }});
            """, id="move-map"),
            city_buttons()
        )
    except GeocoderTimedOut:
        return "Geocoding timed out"

def get_active_city() -> CityLocation | None:
    """Get the currently active city for the current user, or first city if none active"""
    cities = city_locs()
    # First try to find a city marked as active
    active = next((city for city in cities if getattr(city, 'active', False)), None)
    # If no active city found, use the first city
    if not active and cities:
        active = cities[0]
        active.active = True
        city_locs.update(active)
    return active

# get_lat_lon_key takes lat/lon and gives uniform format so we can use it as a key in a dictionary
def get_lat_lon_key(lat: float, lon: float) -> str:
    return f"{lat:.2f},{lon:.2f}"

def add_person_markers() -> str:
    """Generate JavaScript code to add markers for all cities with coordinates"""
    apm = ""
    for city in city_locs():
        if city.lat and city.lon:
            lat_lon_key = get_lat_lon_key(city.lat, city.lon)
            print(f"Adding marker for {city.name} at {city.lat}, {city.lon}")
            apm += f"add_person_location('{active_user}', '{lat_lon_key}', map, {city.lat}, {city.lon}, {city.years});\n"
    return apm

@rt
def index():
    # Create Mapbox container with initialization script
    map_container = Div(
        id="map",
        cls="w-full h-full rounded-lg",
        style="position: relative; height: calc(100vh - 2rem);"
    )
    
    # Get active city for initial map position
    active_city = get_active_city()
    lat = 40.0
    lon = -75.0
    initial_zoom = 9
    print(f"Active city: {active_city}")
    if active_city and active_city.lat and active_city.lon:
        lat = active_city.lat
        lon = active_city.lon
        initial_zoom = active_city.zoomlevel
    initial_center = f"[{lon}, {lat}]"
    
    map_script = Div(
        Script(f"""
            const map = initMap('{mapbox_token}', {initial_center}, {initial_zoom});
            {add_person_markers()}
        """)
    )
    
    # Create right content area with map and slider
    right_content = Div(
        map_container,
        map_script,
        cls="flex-1 p-2 h-screen overflow-hidden"
    )
    
    # Create layout with sidebar and right content
    layout = Div(
        Div(get_distinct_users(), city_buttons(), cls="p-2 h-screen overflow-y-auto"),
        right_content,
        cls="flex h-screen overflow-hidden"
    )
    
    return Title("Life Map"), layout

# Start the server
serve() 
