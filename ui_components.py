from fasthtml.common import *
from monsterui.all import *
from models import cities_occupied_by_person, CityLocation
from models import person_years_in_city

# UI Constants
CITY_NAV_WIDTH = 'w-52'

def city_buttons(selected_person: str, selected_city: CityLocation | None = None):
    print(f"city_buttons: {selected_person=}, {selected_city=}")
    user_city_data = cities_occupied_by_person(selected_person)
    if user_city_data:
        selected_person_start_year = min(L(user_city_data).attrgot('start_year').map(int))
        selected_person_total_years = sum(L(user_city_data).attrgot('years').map(int))
        buttons = [make_city_button(city, selected_city, selected_person_start_year, selected_person_total_years) for city in user_city_data]
    else:
        buttons = []

    return Div(
        *buttons,
        id='city-buttons-container',
        cls='space-y-2'
    )

def make_city_button(city, selected_city: CityLocation | None = None, 
                    selected_person_start_year: int | None = None,
                    selected_person_total_years: int | None = None):
    single_percent = 100 / selected_person_total_years
    left_percent = round(single_percent * (city.start_year - selected_person_start_year))
    middle_percent = round(single_percent * city.years)
    right_percent = 100 - left_percent - middle_percent
    button_style = 'bg-blue-500 text-white' if selected_city and city.id == selected_city.id else 'bg-blue-50'

    button = Button(
        Div(DivLAligned(city.name), 
            Div(Div(cls="h-1 bg-blue-200", style=f"width: {left_percent}%"),
                Div(cls="h-1 bg-green-400", style=f"width: {middle_percent}%"),
                Div(cls="h-1 bg-blue-200", style=f"width: {right_percent}%"),
                cls="w-full flex"),
            cls="w-full"),
        hx_trigger='click',
        hx_vals="js:{zoom: get_zoom()}",
        hx_get=f'/change-city/{city.id}',
        hx_target='#city-buttons-container',
        cls=f'w-fulltext-left justify-start hover:bg-muted {CITY_NAV_WIDTH} {button_style}')

    return DivLAligned(
        Div(
            button,
            cls="flex flex-col"
        ),
        id=f'citybutton-{city.id}',
    )

def get_distinct_users(selected_person: str):
    from models import db
    
    result = db.query("select distinct username from city_location")
    people = [row['username'] for row in result]
    people_start_years = {}
    for person in people:
        result = db.query("select min(start_year) as start_year from city_location where username = ?", (person,))
        if result:
            result = list(result)
        start_years = [row['start_year'] for row in result]
        people_start_years[person] = min(start_years)

    options = [Option("Select person", value="")]
    # order people by start year
    people.sort(key=lambda x: people_start_years[x])
    options.extend([Option(person, cls="text-xs", value=person) for person in people])
    
    if not selected_person:
        options[0].selected = True
    else:
        for opt in options[1:]:
            if opt.value == selected_person:
                opt.selected = True
                break
    
    return Select(
        *options,
        name='selected_person',
        hx_trigger='change',
        hx_post='/select-person',
        hx_target='#city-buttons-container',
        hx_swap='outerHTML',
        cls=f'{CITY_NAV_WIDTH} mb-2'
    )

# MUST KEEP IN SYNC MANUALLY WITH static/js/map-init.js
circle_colors = ['#01bcfe', '#ff7d00', '#ff006d', '#adff02', '#8f00ff']

def lighten_color(hex_color, amount=0.3):
    """
    Lightens a hex color by the given amount (0-1 range).
    """
    # Remove the '#' if present
    hex_color = hex_color.lstrip('#')
    
    # Convert hex to RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    # Lighten RGB values
    r = min(255, int(r + (255 - r) * amount))
    g = min(255, int(g + (255 - g) * amount))
    b = min(255, int(b + (255 - b) * amount))
    
    # Convert back to hex
    return f'#{r:02x}{g:02x}{b:02x}'


def selected_users_marked(selected_users):
    return [user['name'] for user in selected_users if user['is_shown_above_map']]

def person_header_display(person, people_cities_for_year, selected_person, selected_city, first_selected_year, color):
    print(f"PERSON HEADER DISPLAY: {person}, {selected_person}, {selected_city}, {people_cities_for_year=}")
    lighter_color = lighten_color(color, 0.2)
    year_str_for_city = person_years_in_city(person, selected_person, first_selected_year, lighter_color, selected_city)
    if person == selected_person:
        if year_str_for_city:
            return (Span(person + ", ", cls="p-0 text-xs italic font-semibold", style=f"color: {color}"), 
                    Span(selected_city + ", ", cls="p-0 text-xs font-semibold"),
                    Span(year_str_for_city, cls="p-0 text-xs")) 
        else:
            return Span(person + ", ", cls="p-0 text-xs italic font-semibold", style=f"color: {color}")
    else:
        print(f"NOT SELECTED PERSON, {year_str_for_city=}")
        if year_str_for_city:
            return (Span(person + ", ", cls="p-0 text-xs", style=f"color: {color}"),
                    Span(selected_city + ", ", cls="p-0 text-xs text-gray-300"),
                    Span(year_str_for_city, cls="p-0 text-xs text-gray-300")) 
        else:
            if people_cities_for_year:
                for city in people_cities_for_year:
                    print(f"CHECKING CITY: {city} for {person}")
                    if city.username == person:
                        person_city_span = Span(city.name + ", ", cls="p-0 text-xs text-gray-300")
                        year_str_for_city = person_years_in_city(person, selected_person, first_selected_year, lighter_color, city.name)
                        return (Span(person + ", ", cls="p-0 text-xs italic font-semibold", style=f"color: {color}"), 
                            person_city_span,
                            Span(year_str_for_city, cls="p-0 text-xs text-gray-300"))

            return Span(person, cls="p-0 text-xs italic font-semibold", style=f"color: {color}")

def MarkedUsers(people_cities_for_year, marker_update_script, selected_users, selected_city, selected_person, years_selected):
    first_selected_year = years_selected[0] if years_selected else None
    print(f"MarkedUsers, {selected_person=}, {selected_city=}: {marker_update_script}")
    
    return Div(
        Script(marker_update_script),
        Grid(Div(*[Div(person_header_display(user, people_cities_for_year, selected_person, selected_city, first_selected_year, f"{circle_colors[i % len(circle_colors)]}")) 
            for i, user in enumerate(selected_users_marked(selected_users))], cls="text-xs"), 
            cols=1, cls="gap-0"),
        hx_swap_oob="true",
        cls="relative w-full p-0",
        id="marked-users-container"
    )

# Years UI Components
def YearsButtons(years, years_selected, base_css, selected_css, unselected_css):
    buttons = []
    for year in years:
        if year in years_selected:
            buttons.append(Button(str(year), 
                                hx_get=f'/unselect/{year}', 
                                hx_target='#years-container', 
                                cls=f'year_button {base_css} {selected_css}',
                                id=f'y-{year}') )
        else:
            buttons.append(Button(str(year), 
                                hx_get=f'/select/{year}', 
                                hx_target='#years-container', 
                                cls=f'year_button {base_css} {unselected_css}',
                                id=f'y-{year}'))
    return buttons

def ScrollableYearsButtons(years, years_selected):
    selected_css = 'text-gray-700 bg-green-200 hover:bg-green-400'
    unselected_css = 'text-gray-500 bg-yellow-200 hover:bg-yellow-400'
    base_css = 'italic text-xs h-full rounded-none pl-1 pr-1 py-0 border'
    buttons = YearsButtons(years, years_selected, base_css, selected_css, unselected_css)
    
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

def Years(years, years_selected):
    return Div(
        Button(UkIcon('chevron-left'), 
               cls='h-full py-0 p-0.5 absolute left-0 top-1/2 -translate-y-1/2 z-10 bg-white/80 hover:bg-white p-2 rounded-r shadow-md',
               id='scroll-left'),
        ScrollableYearsButtons(years, years_selected),
        Button(UkIcon('chevron-right'), 
               cls='h-full py-0 p-0.5 absolute right-0 top-1/2 -translate-y-1/2 z-10 bg-white/80 hover:bg-white p-2 rounded-l shadow-md',
               id='scroll-right'),
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
            document.body.addEventListener('htmx:afterSwap', function(evt) {
                restoreScrollPosition();
            });
        """), 
        cls='relative w-full no-scrollbar',
        style="height: 20px",
        hx_swap_oob="true",
        id='years-container'
    )

def scroll_position():
    return Script("""
    const saveScrollPosition = () => {
        const scrollPosition = document.getElementById('buttons-container').scrollLeft;
        localStorage.setItem('buttonsScrollPosition', scrollPosition);
    };

    const restoreScrollPosition = () => {
        const savedPosition = localStorage.getItem('buttonsScrollPosition');
        if (savedPosition !== null) {
            document.getElementById('buttons-container').scrollTo({
                left: parseInt(savedPosition),
                behavior: 'instant'
            });
        }
    };

    document.addEventListener('DOMContentLoaded', () => {
        restoreScrollPosition();
    });
    """) 
