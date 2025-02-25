from random import randint
import random
from fasthtml.common import *
from monsterui.all import *
from models import _years_str

from models import CityLocation
from ui_cards import make_card

app, rt = fast_app(hdrs=Theme.slate.headers())

def IconCard(icon_name):
    return Card(
        DivCentered(
            UkIcon(icon_name, height=40, width=40),
            H4(icon_name, cls="mt-4"),
            cls="p-4"
        ),
        cls=(CardT.hover, "cursor-pointer")  # Use CardT.hover for proper hover effect
    )


@rt("/acard")
def artistic_card():
    return Div(
        make_card("Diana", 1937, "yellow", cities_occupied_by_person("Diana")),
        make_card("Johannes", 1959, "orange", cities_occupied_by_person("Johannes")),
        make_card("Farahnaz", 1961, "rose", cities_occupied_by_person("Farahnaz")),
        make_card("Hannes", 1933, "slate", cities_occupied_by_person("Hannes")),
        make_card("Abbas", 1940, "lime", cities_occupied_by_person("Abbas")),
        make_card("Akhtar", 1944, "blue", cities_occupied_by_person("Akhtar")),
    )


def random_subset(cities, min_count, max_count):
    return random.sample(cities, randint(min_count, max_count))

def cities_occupied_by_person(person_name):
    cities = []
    start_year = 1900 + randint(0, 125)
    city_start_year = start_year
    for city_name in random_subset(["Tucson", "Yuma", "Los Angeles, CA", 
                      "San Francisco, CA", "New Orleans, LA", "Dallas, TX",
                      "Houston, TX", "San Antonio, TX", "Phoenix, AZ",
                      "St. Louis, MO", "Kansas City, MO", "Chicago, IL",
                      "Minneapolis, MN", "St. Paul, MN", "Seattle, WA",
                      "Portland, OR", "Honolulu, HI", "Washington, DC",
                      "New York, NY", "Philadelphia, PA", "Baltimore, MD",
                      "Miami, FL", "Atlanta, GA", "Charlotte, NC",
                      "Raleigh"], 2, 5):
        years = randint(1, 10)
        city_start_year += years
        city_loc = CityLocation(name=city_name, 
                                zoomlevel=10, 
                                username=person_name, 
                                years=years, 
                                start_year=city_start_year)
        cities.append(city_loc)
    return cities
   

@rt("/")
def get():
    icons = [
        "user", "user-circle", "users", "user-round", 
        "user-cog", "user-check", "male", "female", "baby"
    ]
    
    return Titled("User & Gender Icons",
        Container(
            H1("User & Gender Icons from Lucide"),
            P("Click any icon card to copy its name", cls="mb-6 text-gray-600"),
            Grid(*[IconCard(icon) for icon in icons], 
                 cols_sm=2, cols_md=3, cols_lg=4, 
                 gap=4),
            Script("""
                document.querySelectorAll('.card').forEach(card => {
                    card.onclick = (e) => {
                        const text = card.querySelector('h4').textContent;
                        navigator.clipboard.writeText(text);
                        alert('Copied: ' + text);
                    }
                });
            """)
        )
    )

serve()
