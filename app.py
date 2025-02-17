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

@rt('/change-user')
def change_user(username: str, sess):
    sess['selected_person'] = username
    if username not in sess['selected_users']:
        sess['selected_users'].append(username)
    city_locs.xtra(username=username)
    
    active_city = get_active_city(sess)
    
    if active_city:
        print(f"CHANGE_USER: Selected users: {sess['selected_users']}, active city: {active_city.name}")
        return (Div(
            Script(f"""
                {add_person_markers(sess)}
                map.flyTo({{
                    center: [{active_city.lon}, {active_city.lat}],
                    zoom: {active_city.zoomlevel},
                    essential: true
                }});
            """),
            city_buttons(active_city)
        ),MarkedUsers(sess['selected_users']))
    print(f"CHANGE_USER: Selected users: {sess['selected_users']}")
    return (city_buttons(active_city), MarkedUsers(sess['selected_users']))

@rt('/change-city/{city_id}')
def change_city(city_id: int, sess):
    print(f"CHANGE_CITY: City ID: {city_id}")
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
        ), Years(sess['years'], sess['years_selected']))
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

@rt("/")
def index(sess):
    years = list(range(1950, 2026))
    if 'years_selected' not in sess:
        sess['years'] = years
        sess['years_selected'] = []
        sess['selected_users'] = []

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
        MarkedUsers(sess['selected_users']),
        Years(sess['years'], sess['years_selected']),
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
