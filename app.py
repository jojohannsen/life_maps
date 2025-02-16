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

def get_distinct_users(selected_person: str):
    result = db.query("select distinct username from city_location")
    options = [Option("Select person", value="")]  # Placeholder option
    options.extend([Option(row['username'], value=row['username']) for row in result])
    
    # If no selected_person specified, select first non-placeholder option if available
    if not selected_person:
        options[0].selected = True
    else:
        # Otherwise select the matching user option
        for opt in options[1:]:  # Skip placeholder
            if opt.value == selected_person:
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
    sess['selected_person'] = username
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
                print(f"Adding marker for {city.name} at {city.lat}, {city.lon}")
                apm += f"console.log('Adding marker for {json.dumps(selected_person)} at {json.dumps(city.name)}');\n"
                apm += f"add_person_location('{selected_person}', '{lat_lon_key}', map, {city.lat}, {city.lon}, {city.years});\n"
        sess['users_with_markers'].append(selected_person)
    return apm


def create_year_buttons(years, years_selected, base_css, selected_css, unselected_css):
    print(type(years), years_selected)
    buttons = []
    for year in years:
        if year in years_selected:
            buttons.append(Button(str(year), 
                                hx_get=f'/unselect/{year}', 
                                hx_target='#years-container', 
                                cls=f'year_button {base_css} {selected_css}'))
        else:
            buttons.append(Button(str(year), 
                                hx_get=f'/select/{year}', 
                                hx_target='#years-container', 
                                cls=f'year_button {base_css} {unselected_css}'))
    return buttons

@rt('/select/{year}')
def get(sess, year: int):
    print(f'selecting {year}')
    sess['years_selected'].append(year)
    print(sess['years_selected'])
    return Years(sess['years'], sess['years_selected'])

@rt('/unselect/{year}')
def get(sess, year: int):
    print(f'unselecting {year}')
    sess['years_selected'].remove(year)
    print(sess['years_selected'])
    return Years(sess['years'], sess['years_selected'])

def YearsButtons(years, years_selected):
    selected_css = 'text-gray-700 bg-green-200 hover:bg-green-400'
    unselected_css = 'text-gray-500 bg-yellow-200 hover:bg-yellow-400'
    base_css = 'italic text-xs h-full rounded-none pl-1 pr-1 py-0 border'
    buttons = create_year_buttons(years, years_selected, base_css, selected_css, unselected_css)
    
    # Add initial scroll position if provided
    script = """
    document.getElementById('buttons-container').addEventListener('scroll', function() {
        saveScrollPosition();
    });
    """
    
    return Div(
        *buttons,
        Script(script),
        id='buttons-container',
        cls='ml-8 mr-8 flex overflow-x-auto scroll-smooth no-scrollbar',
        style="""
            -ms-overflow-style: none; 
            scrollbar-width: none; 
            overflow-x: scroll;
        """,
        _after="""
            ::-webkit-scrollbar {
                display: none;
                width: 0;
                height: 0;
            }
        """
    )

def scroll_position():
    return Script("""
    // To save the scroll position
const saveScrollPosition = () => {
    const scrollPosition = document.getElementById('buttons-container').scrollLeft;
    // Save to localStorage
    localStorage.setItem('buttonsScrollPosition', scrollPosition);
};

// To restore the scroll position
const restoreScrollPosition = () => {
    const savedPosition = localStorage.getItem('buttonsScrollPosition');
    if (savedPosition !== null) {
        document.getElementById('buttons-container').scrollTo({
            left: parseInt(savedPosition),
            behavior: 'instant'
        });
    }
};

// Call when the document is ready
document.addEventListener('DOMContentLoaded', () => {
    restoreScrollPosition();
});
""")

def Years(years, years_selected):
    # Container with relative positioning for arrow placement
    return Div(
        # Left arrow button
        Button(UkIcon('chevron-left'), 
               cls='h-full py-0 p-0.5 absolute left-0 top-1/2 -translate-y-1/2 z-10 bg-white/80 hover:bg-white p-2 rounded-r shadow-md',
               id='scroll-left'),
        # Scrollable container for year buttons
        YearsButtons(years, years_selected),
        # Right arrow button
        Button(UkIcon('chevron-right'), 
               cls='h-full py-0 p-0.5 absolute right-0 top-1/2 -translate-y-1/2 z-10 bg-white/80 hover:bg-white p-2 rounded-l shadow-md',
               id='scroll-right'),
        # JavaScript for scroll behavior
        Script("""
            document.getElementById('scroll-left').addEventListener('click', () => {
                document.getElementById('buttons-container').scrollBy({
                    left: -200,
                    behavior: 'smooth'
                });
                setTimeout(() => {
                    saveScrollPosition();
                }, 500);
            });
            
            document.getElementById('scroll-right').addEventListener('click', () => {
                document.getElementById('buttons-container').scrollBy({
                    left: 200,
                    behavior: 'smooth'
                });
                setTimeout(() => {
                    saveScrollPosition();
                }, 500);
            });
            // Add listeners to year buttons after HTMX swaps
            document.body.addEventListener('htmx:afterSwap', function(evt) {
                restoreScrollPosition();
            });
        """), 
        cls='relative w-full no-scrollbar',
        style="height: 20px",
        id='years-container'
    )

@rt("/")
def index(sess):
    years = list(range(1950, 2026))
    # if session does not have 'years_selected' set, set it to the first year in the list
    if 'years_selected' not in sess:
        sess['years'] = years
        sess['years_selected'] = []
    # Create Mapbox container with initialization script
    map_container = Div(
        id="map",
        cls="w-full h-full rounded-lg",
        style="position: relative; height: calc(100vh - 2rem);"
    )
    print(f"Index: Session: {sess}")
    sess['selected_person'] = 'no user selected'
    sess['users_with_markers'] = []
    city_locs.xtra(username='no user selected')

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
        Years(sess['years'], sess['years_selected']),
        map_container,
        map_script,
        cls="flex-1 p-2 h-screen overflow-hidden"
    )
    
    # Create layout with sidebar and right content
    layout = Div(scroll_position(),
        Div(get_distinct_users(sess['selected_person']), 
            city_buttons(active_city), cls="p-2 h-screen overflow-y-auto"),
        right_content,
        cls="flex h-screen overflow-hidden"
    )
    
    return Title("Life Map"), layout

# Start the server
serve() 
