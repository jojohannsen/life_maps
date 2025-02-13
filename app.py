from fasthtml.common import *
from monsterui.all import *
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import json
import os
import pathlib
from users import init_user_module

# Database setup
pathlib.Path('data').mkdir(exist_ok=True)
DB_PATH = 'data/cities.db'
db = database(DB_PATH)

# UI Constants
CITY_NAV_WIDTH = 'w-48'

class CityLocation:
    id:int; username:str; name:str; lat:float; lon:float; zoomlevel:int; years:int

city_locs = db.create(CityLocation, pk='id')
initial_user = 'no user selected'  # default user
city_locs.xtra(username=initial_user)  # Set initial filter

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
auth_middleware = init_user_module(db)
app.before = [auth_middleware]
users = db.t.users

geolocator = Nominatim(user_agent="my_app")

def city_buttons(selected_city: CityLocation | None = None):
    user_city_data = city_locs()
    city_buttons = [make_city_button(city, selected_city) for city in user_city_data]

    return Div(
        *city_buttons,
        id='city-buttons-container',
        cls='space-y-2'
    )
    
def delete_city_record(city_id: int):
    city_locs.delete(city_id)

def make_city_button(city, selected_city: CityLocation | None = None):
    # Add 'active' class if this is the currently selected city
    button = Button(city.name, 
                   hx_trigger='click',
                   hx_get=f'/change-city/{city.id}',
                   hx_target='#city-buttons-container',  # Changed target to update all buttons
                   cls=f'text-left justify-start hover:bg-muted {CITY_NAV_WIDTH} ' + 
                       ('bg-blue-500 text-white' if city.id == selected_city.id else 'bg-blue-50'))
    citybutton = DivLAligned(
        button,
        id=f'citybutton-{city.id}',
    )
    return citybutton

def get_distinct_users(active_user: str):
    result = db.query("select distinct username from city_location")
    options = [Option("Select person", value="")]  # Placeholder option
    options.extend([Option(row['username'], value=row['username']) for row in result])
    
    # If no active_user specified, select first non-placeholder option if available
    if not active_user:
        options[0].selected = True
    else:
        # Otherwise select the matching user option
        for opt in options[1:]:  # Skip placeholder
            if opt.value == active_user:
                opt.selected = True
                break
    
    return Select(
        *options,
        name='username',
        hx_trigger='change',
        hx_post='/change-user',
        hx_target='#city-buttons-container',
        hx_swap='outerHTML',
        cls=f'{CITY_NAV_WIDTH} mb-2'
    )

@rt('/change-user')
def change_user(username: str, sess):
    sess['active_user'] = username
    # Reset users_with_markers when changing users
    sess['users_with_markers'] = []
    city_locs.xtra(username=username)
    
    # Get active city for the new user
    active_city = get_active_city(sess)
    print(f"Active city: {active_city}")
    
    if active_city:
        # Return both the map update and city buttons
        return Div(
            Script(f"""
                {add_person_markers(sess)}
                map.flyTo({{
                    center: [{active_city.lon}, {active_city.lat}],
                    zoom: {active_city.zoomlevel},
                    essential: true
                }});
            """),
            city_buttons(active_city)
        )
    
    return city_buttons(active_city)


@rt('/change-city/{city_id}')
def change_city(city_id: int, sess):
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

        sess['active_city_id'] = city_id
        
        # Return both the map update and the updated button list
        return Div(
            Script(f"""
                {add_person_markers(sess)}
                map.flyTo({{
                    center: [{city.lon}, {city.lat}],
                    zoom: {city.zoomlevel},
                    essential: true
                }});
            """, id="move-map"),
            city_buttons(city)
        )
    except GeocoderTimedOut:
        return "Geocoding timed out"

def get_active_city(sess) -> CityLocation | None:
    """Get the currently active city for the current user from session, or first city if none active"""
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

# get_lat_lon_key takes lat/lon and gives uniform format so we can use it as a key in a dictionary
def get_lat_lon_key(lat: float, lon: float) -> str:
    return f"{lat:.2f},{lon:.2f}"

def add_person_markers(sess) -> str:
    """Generate JavaScript code to add markers for all cities with coordinates"""
    active_user = sess['active_user']
    
    # Initialize users_with_markers if not present
    if 'users_with_markers' not in sess:
        sess['users_with_markers'] = []
    
    apm = ""
    # Only add markers if we haven't already added them for this user
    if active_user not in sess['users_with_markers']:
        for city in city_locs():
            if city.lat and city.lon:
                lat_lon_key = get_lat_lon_key(city.lat, city.lon)
                print(f"Adding marker for {city.name} at {city.lat}, {city.lon}")
                apm += f"console.log('Adding marker for {json.dumps(active_user)} at {json.dumps(city.name)}');\n"
                apm += f"add_person_location('{active_user}', '{lat_lon_key}', map, {city.lat}, {city.lon}, {city.years});\n"
        sess['users_with_markers'].append(active_user)
    return apm

@rt("/")
def index(auth, sess):
    # Create Mapbox container with initialization script
    map_container = Div(
        id="map",
        cls="w-full h-full rounded-lg",
        style="position: relative; height: calc(100vh - 2rem);"
    )
    print(f"Index: Session: {sess}")
    # Get active city for initial map position
    active_city = get_active_city(sess)
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
            {add_person_markers(sess)}
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
        Div(get_distinct_users(sess['active_user']), city_buttons(active_city), cls="p-2 h-screen overflow-y-auto"),
        right_content,
        cls="flex h-screen overflow-hidden"
    )
    
    return Title("Life Map"), layout

login_redir = RedirectResponse('/login', status_code=303)
@dataclass
class Login: name:str; pwd:str
# For instance, this function handles GET requests to the `/login` path.
@rt("/login")
def get():
    print("IN /login")
    # This creates a form with two input fields, and a submit button.
    # All of these components are `FT` objects. All HTML tags are provided in this form by FastHTML.
    # If you want other custom tags (e.g. `MyTag`), they can be auto-generated by e.g
    # `from fasthtml.components import MyTag`.
    # Alternatively, manually call e.g `ft(tag_name, *children, **attrs)`.
    frm = Form(
        Div("Any values are ignored, right now, just creates a session after login"),
        # Tags with a `name` attr will have `name` auto-set to the same as `id` if not provided
        Input(id='name', placeholder='Name'),
        Input(id='pwd', type='password', placeholder='Password'),
        Button('login'),
        action='/login', method='post', cls="w-96")
    # If a user visits the URL directly, FastHTML auto-generates a full HTML page.
    # However, if the URL is accessed by HTMX, then one HTML partial is created for each element of the tuple.
    # To avoid this auto-generation of a full page, return a `HTML` object, or a Starlette `Response`.
    # `Titled` returns a tuple of a `Title` with the first arg and a `Container` with the rest.
    # See the comments for `Title` later for details.
    return Titled("Login", frm, cls=TextPresetsT.label)

@rt("/login")
def post(login: Login, sess):
    print(f"Login: {login}")
    print(f"Session: {sess}")
    if not login.name or not login.pwd:
        return login_redir
    print(f"Attempt to get user {login.name}")
    try:
        user = users[login.name]
        print(f"User found: {user}")
    except NotFoundError:
        print(f"User not found, creating new user")
        user = users.insert(login)
        print(f"User: {user}")
        # if not compare_digest(user.pwd.encode("utf-8"), 
        #                     login.pwd.encode("utf-8")):
        #     return self.login_redirect
            
    sess['auth'] = user.name
    sess['active_user'] = user.name
    print(f"Session: {sess}")
    print(f"Redirecting to /")
    return RedirectResponse('/', status_code=303)

@rt("/logout")
def get(sess):
    if 'auth' in sess:
        del sess['auth']
    sess['active_user'] = None
    return login_redir
# Start the server
serve() 
