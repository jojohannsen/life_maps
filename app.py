from fasthtml.common import *
from monsterui.all import *
import os
from geopy.exc import GeocoderTimedOut
from models import db, DB_PATH, city_locs
from ui_components import (
    city_buttons, get_distinct_users, Years, scroll_position, MarkedUsers
)
from map_utils import get_active_city, add_person_markers, geolocator

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

def PersonVisualState(name: str, is_shown_above_map: bool = False):
    return {
        'name': name,
        'is_shown_above_map': is_shown_above_map
    }

@rt('/change-user')
def change_user(username: str, sess):
    sess['selected_person'] = username
    sess['selected_city'] = ''
    if username not in L(sess['people_shown_on_map']).attrgot('name'):
        sess['people_shown_on_map'].append(PersonVisualState(name=username))
    city_locs.xtra(username=username)
    
    active_city = None
    return (city_buttons(active_city), 
            MarkedUsers(sess['people_shown_on_map'], sess['selected_city'], sess['selected_person'], sess['years_selected']))

def set_people_shown_on_map(sess):
    current_person = sess['selected_person']
    if current_person:
        current_person_state = next((user for user in sess['people_shown_on_map'] if user['name'] == current_person), None)
        if current_person_state:
            current_person_state['is_shown_above_map'] = True
            print(f"Setting {current_person} to shown above map")

@rt('/change-city/{city_id}')
def change_city(city_id: int, sess):
    set_people_shown_on_map(sess)
    city = city_locs.get(city_id)
    try:
        if not city.lat or not city.lon:
            location = geolocator.geocode(city.name)
            if location:
                city.lat = location.latitude
                city.lon = location.longitude
                city.zoomlevel = 10
                city_locs.update(city)

        sess['active_city_id'] = city_id
        sess['selected_city'] = city.name
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
                    zoom: {city.zoomlevel},
                    essential: true
                }});
            """, id="move-map"),
            city_buttons(city)
        ), MapHeader(sess))
    except GeocoderTimedOut:
        return "Geocoding timed out"

@rt('/select/{year}')
def get(sess, year: int):
    sess['years_selected'].append(year)
    return Years(sess['years'], sess['years_selected'])

@rt('/unselect/{year}')
def get(sess, year: int):
    sess['years_selected'].remove(year)
    return Years(sess['years'], sess['years_selected'])

def MapHeader(sess):
    print(f"MapHeader: {sess['people_shown_on_map']}")
    return Div(
        MarkedUsers(sess['people_shown_on_map'], sess['selected_city'], sess['selected_person'], sess['years_selected']),
        Years(sess['years'], sess['years_selected']),
        hx_swap_oob="true",
        id="map-header"
    )

first_time = True
@rt("/")
def index(sess):
    # always start from a known state
    sess.clear()

    global first_time
    if first_time and 'years_selected' in sess:
        del sess['years_selected']  # or sess.pop('years_selected', None)
    first_time = False
    years = list(range(1900, 2026))

    sess['years'] = years
    sess['years_selected'] = []
    sess['people_shown_on_map'] = []
    sess['selected_city'] = ''

    map_container = Div(
        id="map",
        cls="w-full h-full rounded-lg",
        style="position: relative; height: calc(100vh - 2rem);"
    )

    sess['selected_person'] = 'no user selected'
    city_locs.xtra(username='no user selected')

    active_city = get_active_city(sess)
    lat, lon = 40.0, -75.0
    initial_zoom = 9
    
    if active_city and active_city.lat and active_city.lon:
        lat = active_city.lat
        lon = active_city.lon
        initial_zoom = active_city.zoomlevel
    
    map_script = Div(
        Script(f"""
            const map = initMap('{mapbox_token}', [{lon}, {lat}], {initial_zoom});
            {add_person_markers(sess)}
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
            city_buttons(active_city), 
            cls="p-2 h-screen overflow-y-auto"
        ),
        right_content,
        cls="flex h-screen overflow-hidden"
    )
    
    return Title("Life Map"), layout

serve() 
