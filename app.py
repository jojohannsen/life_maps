import os
from fasthtml.common import *
from monsterui.all import *
from geopy.exc import GeocoderTimedOut
from models import (
    DB_PATH, city_locs, cities_occupied_by_person, people_in_year, people_colors
)
from ui_components import (
    create_people, city_buttons, get_distinct_users, Years, scroll_position, MarkedUsers
)
from map_utils import get_active_city, add_person_markers, geolocator
from constants import SELECTED_CITY_NAME_KEY, ACTIVE_CITY_ID_KEY

# Create FastHTML app with blue theme and add Mapbox CSS/JS
mapbox_token = os.environ['MAPBOX_TOKEN']
mapbox_css = Link(rel="stylesheet", href="https://api.mapbox.com/mapbox-gl-js/v3.1.2/mapbox-gl.css")
mapbox_js = Script(src="https://api.mapbox.com/mapbox-gl-js/v3.1.2/mapbox-gl.js")
map_init_js = Script(src="/static/js/map-init.js")

app, rt = fast_app(
    db_file=DB_PATH,
    hdrs=[
        Theme.slate.headers(),
        mapbox_css,
        mapbox_js,
        map_init_js
    ]
)

def PersonVisualState(name: str, is_shown_above_map: bool = False):
    return {
        'name': name,
        'is_shown_above_map': is_shown_above_map
    }

@rt('/select-person')
def select_person(selected_person: str, sess):
    print(f"select_person: {selected_person}, {sess[SELECTED_CITY_NAME_KEY]=}")
    sess['selected_person'] = selected_person
    if selected_person not in L(sess['people_shown_on_map']).attrgot('name'):
        sess['people_shown_on_map'].append(PersonVisualState(name=selected_person, is_shown_above_map=True))
    cities = cities_occupied_by_person(selected_person)
    print(f"cities: {len(cities)}")
    city_names = [city.name for city in cities]
    if sess[SELECTED_CITY_NAME_KEY] not in city_names:
        sess[SELECTED_CITY_NAME_KEY] = ''
    active_city = None
    marker_script = ''
    selected_city = sess[SELECTED_CITY_NAME_KEY]
    print(f"selected_city: {selected_city}")
    people_cities_for_year = None
    for city in cities:
        if city.name == selected_city:
            print(f"FOUND ACTIVE CITY: {city.name}")
            active_city = city
            sess[ACTIVE_CITY_ID_KEY] = city.id
            marker_script = add_person_markers(sess)
            people_cities_for_year = people_in_year(city.start_year)
            people_colors[city.username] = city.color
            break
    if ACTIVE_CITY_ID_KEY in sess:
        active_city = city_locs.get(sess[ACTIVE_CITY_ID_KEY])
    return (city_buttons(selected_person, active_city), 
            MapHeader(sess, people_cities_for_year, marker_script))
 
def set_people_shown_on_map(sess):
    current_person = sess['selected_person']
    if current_person:
        current_person_state = next((user for user in sess['people_shown_on_map'] if user['name'] == current_person), None)
        if current_person_state:
            current_person_state['is_shown_above_map'] = True
            print(f"Setting {current_person} to shown above map")

@rt('/change-city/{city_id}')
def change_city(city_id: int, zoom: int, sess):
    global people_colors
    print(f"people_colors: {people_colors}")
    set_people_shown_on_map(sess)
    city = city_locs.get(city_id)
    try:
        if not city.lat or not city.lon:
            location = geolocator.geocode(city.name)
            if location:
                city.lat = location.latitude
                city.lon = location.longitude
                city.zoomlevel = zoom
                city_locs.update(city)

        sess[ACTIVE_CITY_ID_KEY] = city_id
        sess[SELECTED_CITY_NAME_KEY] = city.name
        sess['years_selected'] = []
        sess['years_selected'] = list(range(city.start_year, city.start_year + city.years))
        #scroll_script = f"scrollToButton('y-{city.start_year + city.years - 1}', 'center')\n"
        scroll_script = f"scrollToButton('y-{city.start_year}', 'center')"
        return (Div(
            Script(f"""
                {add_person_markers(sess)}
                {scroll_script}
                map.flyTo({{
                    center: [{city.lon}, {city.lat}],
                    zoom: {zoom},
                    essential: true
                }});
            """, id="move-map"),
            city_buttons(sess['selected_person'], city)
        ), MapHeader(sess, people_in_year(city.start_year)))
    except GeocoderTimedOut:
        return "Geocoding timed out"

@rt('/select/{year}')
def get(sess, year: int):
    sess['years_selected'] = [year]
    # find the where people were in this year
    people_cities_for_year = people_in_year(year)
    print(f"people_cities_for_year: {people_cities_for_year}")
    print("CALLING MAP HEADER")
    return MapHeader(sess, people_cities_for_year)

@rt('/unselect/{year}')
def get(sess, year: int):
    sess['years_selected'] = []
    return Years(sess['years'], sess['years_selected'])

def MapHeader(sess, people_cities_for_year = None, marker_script = ''):
    return Div(
        MarkedUsers(people_cities_for_year, marker_script, 
                    sess['people_shown_on_map'], sess[SELECTED_CITY_NAME_KEY], sess['selected_person'], sess['years_selected']),
        Years(sess['years'], sess['years_selected']),
        hx_swap_oob="true",
        id="map-header"
    )

@rt("/")
def index(sess):
    # always start from a known state
    sess.clear()

    years = list(range(1900, 2026))

    sess['years'] = years
    sess['years_selected'] = []
    sess['people_shown_on_map'] = []
    sess[SELECTED_CITY_NAME_KEY] = ''
    sess['selected_person'] = None

    print(f"index: {sess[SELECTED_CITY_NAME_KEY]=}")
    map_container = Div(
        id="map",
        cls="w-full h-full rounded-lg",
        style="position: relative; height: calc(100vh - 2rem);"
    )

    active_city = None
    lat, lon = 40.0, -75.0
    initial_zoom = 9
    
    map_script = Div(
        Script(f"""
const map = initMap('{mapbox_token}', [{lon}, {lat}], {initial_zoom});

function get_zoom() {{
    return Math.round(map.getZoom());
}}

{add_person_markers(sess)}

let people_colors = {{
    {', '.join([f"'{k}': '{v}'" for k, v in people_colors.items()])}
}}
        """)
    )

    right_content = Div(
        MapHeader(sess),
        map_container,
        map_script,
        cls="flex-1 p-2 h-screen overflow-hidden"
    )
    
    layout = Div(
        scroll_position(),
        Div(
            get_distinct_users(sess['selected_person']), 
            city_buttons(sess['selected_person'], active_city), 
            cls="p-2 h-screen overflow-y-auto"
        ),
        right_content,
        cls="flex h-screen overflow-hidden"
    )
    
    return Title("Life Map"), layout

serve() 
