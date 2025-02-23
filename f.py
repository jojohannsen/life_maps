from random import randint
from fasthtml.common import *
from monsterui.all import *
from models import _years_str

from models import CityLocation

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

def make_colors(color):
    return f"bg-{color}-500", f"bg-{color}-200"

def make_card(name, birth_year, color):
    bright_color, subdued_color = make_colors(color)
    return Div(
            Div(name, cls="mt-1 ml-2 font-serif bold text-sm"),
            DivLAligned(
                P(f"{birth_year}", cls="font-sans ml-2 italic text-xs text-gray-400 inline-block"),
                Div(
                    Div(cls=f"mt-0 w-20 h-2 {subdued_color} group-hover:{bright_color} hover:{bright_color} inline-block ml-2"),
                    Div(cls=f"mt-2 w-20 h-2 {subdued_color} group-hover:{bright_color} hover:{bright_color} inline-block"),
                    cls="flex flex-row justify-between h-4"
                ),
                cls="mb-1 ml-1",
            ),
            cls=(CardT.hover, "max-w-sm", "m-4", "w-60", "group")  # Added 'group' class
        )

def make_bar_divs(cities_occupied_by_person, pixel_widths, bright_color, subdued_color):
    return Div(
        *[Div(title=f"{p[1].name} {_years_str(p[1].start_year, p[1].years)}", cls=f"h-2 group-hover:{bright_color} hover:{bright_color} {subdued_color} {'ml-2' if (i == 0) else ''} {'mt-0' if (i%2) == 0 else 'mt-2'} inline-block", 
              style=f"width: {p[0]}px") for i,p in enumerate(zip(pixel_widths, cities_occupied_by_person))],
        cls="flex flex-row justify-between h-4"
    )

def make_card2(name, birth_year, color, cities_occupied_by_person):
    bright_color, subdued_color = make_colors(color)
    # get proportion of years to total years
    total_years = sum(city.years for city in cities_occupied_by_person)
    proportion_of_years = [city.years / total_years for city in cities_occupied_by_person]
    TOTAL_PIXEL_WIDTH = 180
    pixel_widths = [int(p * TOTAL_PIXEL_WIDTH) for p in proportion_of_years]
    bar_divs = make_bar_divs(cities_occupied_by_person, pixel_widths, bright_color, subdued_color)
    print(f"{name} bar_divs: {bar_divs}")
    return Div(
            Div(name, cls="mt-1 ml-2 font-serif bold text-sm"),
            DivLAligned(
                P(f"{birth_year}", cls="font-sans ml-2 italic text-xs text-gray-400 inline-block"),
                Div(
                    *bar_divs,
                    cls="flex flex-row justify-between h-4"
                ),
                cls="mb-1 ml-1",
            ),
            cls=(CardT.hover, "max-w-sm", "m-4", "w-60", "group")  # Added 'group' class
        )

# First, add the CSS styles
tooltip_style = Style("""
    .tooltip-container {
        position: relative;
        display: inline-block;
    }
    
    .tooltip-container .tooltip {
        visibility: hidden;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%);
        padding: 8px;
        background-color: rgba(0, 0, 0, 0.8);
        color: white;
        border-radius: 4px;
        font-size: 14px;
        white-space: nowrap;
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .tooltip-container:hover .tooltip {
        visibility: visible;
        opacity: 1;
    }
    
    /* Add arrow */
    .tooltip-container .tooltip::after {
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: rgba(0, 0, 0, 0.8) transparent transparent transparent;
    }
""")

def make_tooltip_div(tooltip_text):
    return Div(
        Div(
            Div(cls="tooltip", _t=tooltip_text),
            cls="h-2 group-hover:bg-lime-500 hover:bg-lime-500 bg-lime-200 ml-2 mt-0 inline-block",
            style="width: 57px"
        ),
        cls="tooltip-container"
    )

@rt("/acard")
def artistic_card():
    return Div(
        make_card2("Diana", 1937, "yellow", cities_occupied_by_person("Diana")),
        make_card2("Johannes", 1959, "orange", cities_occupied_by_person("Johannes")),
        make_card2("Farahnaz", 1961, "rose", cities_occupied_by_person("Farahnaz")),
        make_card2("Hannes", 1933, "slate", cities_occupied_by_person("Hannes")),
        make_card2("Abbas", 1940, "lime", cities_occupied_by_person("Abbas")),
        make_card2("Akhtar", 1944, "blue", cities_occupied_by_person("Akhtar")),
    )

import random

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
   
@rt("/artistic-card")
def artistic_card():
    return Div(
        make_card("Diana", 1937, "yellow"),
        make_card("Johannes", 1959, "orange"),
        make_card("Farahnaz", 1961, "rose"),
        make_card("Hannes", 1933, "slate"),
        make_card("Abbas", 1940, "lime"),
        make_card("Akhtar", 1944, "blue"),
    )

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
