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
    id:int; username:str; name:str; lat:float; lon:float; zoomlevel:int; active:bool

city_locs = db.create(CityLocation, pk='id')
active_user = 'johannes'  # default user
city_locs.xtra(username=active_user)  # Set initial filter

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
                   id=f'city-name-{city.id}',
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

def select_user():
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


@rt("/move_map", methods=["POST"])
async def move_map(req):
    form = await req.form()
    lat = float(form.get("lat"))
    lng = float(form.get("lng"))
    return Script(f"""
        map.flyTo({{
            center: [{lng}, {lat}],
            zoom: 9,
            essential: true
        }});
    """)

@rt('/change-city/{city_id}')
def change_city(city_id: int):
    city = city_locs.get(city_id)
    try:
        # Only geocode if lat/lon not already set
        if not city.lat or not city.lon:
            location = geolocator.geocode(city.name)
            if location:
                city.lat = location.latitude
                city.lon = location.longitude
                city.zoomlevel = 10
                city_locs.update(city)
        
        # Set all cities as inactive and mark the selected one as active
        for c in city_locs():
            c.active = (c.id == city_id)
            city_locs.update(c)
        
        # Return both the map update and the updated button list
        return Div(
            Script(f"""
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
    initial_center = f"[{active_city.lon}, {active_city.lat}]" if active_city else "[-74.5, 40]"
    initial_zoom = active_city.zoomlevel if active_city else 9
    
    map_script = Div(
        Script(f"""
            const map = initMap('{mapbox_token}', {initial_center}, {initial_zoom});
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
        Div(select_user(), city_buttons(), cls="p-2 h-screen overflow-y-auto"),
        right_content,
        cls="flex h-screen overflow-hidden"
    )
    
    return Title("Map Dashboard"), layout

# Start the server
serve() 
