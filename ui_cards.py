from fasthtml.common import *
from monsterui.all import *
from models import _years_str, CityLocation

def make_single_bar_div(city_location, pixel_width, color, index):
    """
    Creates a single bar div representing a city in a person's timeline.
    
    Parameters:
    -----------
    city_location : CityLocation
        The city object containing name, start_year, and years data
    pixel_width : int
        The width of the bar in pixels, proportional to years spent in the city
    color : str
        The CSS class for the color used by default
    index : int
        The position of this bar in the sequence, used for styling
        
    Returns:
    --------
    Div
        A styled div element representing the city with tooltip information
    """
    bright_color, subdued_color = f"bg-{color}-500", f"bg-{color}-200" 
    return Div(
        cls=f"h-2 group-hover:{bright_color} hover:{bright_color} {subdued_color} {'ml-2' if (index == 0) else ''} {'mt-0' if (index%2) == 0 else 'mt-2'} inline-block cursor-pointer", 
        style=f"width: {pixel_width}px", 
        uk_tooltip=f"title:{_years_str(city_location.start_year, city_location.years)}<br>{city_location.name}; cls: {subdued_color} text-gray-800 uk-active;",
        onclick=f"select_city('{city_location.name}')"
    )

def make_bar_divs(cities_occupied_by_person, pixel_widths, color):
    return Div(
        *[make_single_bar_div(city, width, color, i) 
          for i, (width, city) in enumerate(zip(pixel_widths, cities_occupied_by_person))],
        cls="flex flex-row justify-between h-4"
    )

def make_card(name, birth_year, color, cities_occupied_by_person):
    # get proportion of years to total years
    total_years = sum(city.years for city in cities_occupied_by_person)
    proportion_of_years = [city.years / total_years for city in cities_occupied_by_person]
    TOTAL_PIXEL_WIDTH = 180
    pixel_widths = [int(p * TOTAL_PIXEL_WIDTH) for p in proportion_of_years]
    bar_divs = make_bar_divs(cities_occupied_by_person, pixel_widths, color)

    return A(
            Div(
                Div(name, cls="mt-1 ml-2 font-serif bold text-sm"),
                DivLAligned(
                    P(f"{birth_year}", cls="font-sans ml-2 italic text-xs text-gray-400 inline-block"),
                    Div(
                        *bar_divs,
                        cls="flex flex-row justify-between h-4"
                    ),
                    cls="mb-1 ml-1",
                ),
                cls=(CardT.hover, "max-w-sm", "m-1", "w-60", "group", "cursor-pointer")  # Added 'cursor-pointer'
            ),
            href="/select-person",
            hx_post="/select-person",
            hx_vals=f'{{"selected_person": "{name}"}}',
            cls="no-underline"
        )
