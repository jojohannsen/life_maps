from fasthtml.common import *
from monsterui.all import *
from models import cities_occupied_by_person, CityLocation, people_colors
from models import person_years_in_city
from models import db
from ui_cards import make_card

# UI Constants
CITY_NAV_WIDTH = 'w-52'

def city_buttons(selected_person: str, selected_city: CityLocation | None = None):
    print(f"city_buttons: {selected_person=}, {selected_city=}")
    user_city_data = cities_occupied_by_person(selected_person)
    if user_city_data:
        selected_person_start_year = min(L(user_city_data).attrgot('start_year').map(int))
        selected_person_total_years = sum(L(user_city_data).attrgot('years').map(int))
        color = people_colors.get(selected_person, "blue") 
        buttons = [make_city_button(city, selected_city, selected_person_start_year, selected_person_total_years, color) for city in user_city_data]
    else:
        buttons = []

    return Div(
        *buttons,
        id='city-buttons-container',
        cls='ml-8 space-y-2'
    )

def make_city_button(city, selected_city: CityLocation | None = None, 
                    selected_person_start_year: int | None = None,
                    selected_person_total_years: int | None = None,
                    color: str = "blue"):
    single_percent = 100 / selected_person_total_years
    left_percent = round(single_percent * (city.start_year - selected_person_start_year))
    middle_percent = round(single_percent * city.years)
    right_percent = 100 - left_percent - middle_percent
    button_style = 'bg-blue-500 text-white' if selected_city and city.id == selected_city.id else 'bg-slate-50'
    text_color = 'text-white' if selected_city and city.id == selected_city.id else 'text-gray-400'
    button = Button(
        Div(DivLAligned(city.name, cls=f"{text_color} city-name"), 
            Div(Div(cls="h-1 bg-blue-200", style=f"width: {left_percent}%"),
                Div(cls=f"h-1 bg-{color}-400", style=f"width: {middle_percent}%"),
                Div(cls="h-1 bg-blue-200", style=f"width: {right_percent}%"),
                cls="w-full flex"),
            cls="w-full"),
        hx_trigger='click',
        hx_vals="js:{zoom: get_zoom()}",
        hx_get=f'/change-city/{city.id}',
        hx_target='#city-buttons-container',
        id=f'city{city.id}',
        cls=f'w-fulltext-left justify-start hover:bg-muted {CITY_NAV_WIDTH} {button_style}')

    return DivLAligned(
        Div(
            button,
            cls="flex flex-col"
        ),
        id=f'citybutton-{city.id}',
    )

def get_distinct_users(selected_person: str, selected_city: CityLocation | None = None):
    result = db.query("select distinct username from city_location")
    people = [row['username'] for row in result]
    people_start_years = {}
    
    # Get birth years and cities for each person
    people_data = {}
    for person in people:
        # Get birth year (minimum start year)
        result = db.query("select min(start_year) as start_year from city_location where username = ?", (person,))
        if result:
            result = list(result)
        start_years = [row['start_year'] for row in result]
        birth_year = min(start_years)
        people_start_years[person] = birth_year
        
        # Get cities occupied by this person
        cities = cities_occupied_by_person(person)
        people_data[person] = {
            'birth_year': birth_year,
            'cities': cities
        }
    
    # Order people by birth year
    people.sort(key=lambda x: people_start_years[x])
    
    # Create cards for each person
    cards = []
    for person in people:
        # Get color from people_colors
        color = people_colors.get(person, "blue")  # Default to blue if no color defined
        cb = city_buttons(person, selected_city) if person == selected_person else None
        print(f"{person=}, {selected_person=}, {cb=}")
        # Create card
        card = make_card(
            name=person,
            birth_year=people_data[person]['birth_year'],
            color=color,
            cities_occupied_by_person=people_data[person]['cities']
        )
        cards.append(card)
        if cb:
            cards.append(cb)
    
    return Div(*cards, cls='grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2')

def selected_users_marked(selected_users):
    return [user['name'] for user in selected_users if user['is_shown_above_map']]

def person_header_display(person, people_cities_for_year, selected_person, selected_city, first_selected_year):
    print(f"PERSON HEADER DISPLAY: {person}, {selected_person}, {selected_city}, {people_cities_for_year=}")
    name_color = f"{tailwind_colors[people_colors[person]]['700']}"
    year_str_for_city = person_years_in_city(person, selected_person, first_selected_year, name_color, selected_city)
    if person == selected_person:
        print("PERSON IS SELECTED PERSON: ", person)
        if people_cities_for_year:
            for city in people_cities_for_year:
                print(f"CHECKING CITY: {city} for {person}")
                if city.username == person:
                    person_city_span = Span(city.name + ", ", cls="p-0 text-xs text-gray-300")
                    year_str_for_city = person_years_in_city(person, selected_person, first_selected_year, name_color, city.name)
                    return (Span(person + ", ", cls=f"p-0 text-xs", style=f"color: {name_color}"), 
                        person_city_span,
                        Span(year_str_for_city, cls="p-0 text-xs", style=f"color: {name_color}"))
        elif year_str_for_city:
            return (Span(person + ", ", cls=f"p-0 text-xs font-mono", style=f"color: {name_color}"), 
                    Span(selected_city + ", ", cls="p-0 text-xs font-semibold"),
                    Span(year_str_for_city, cls=f"p-0 text-xs font-mono", style=f"color: {name_color}")) 
        else:
            return Span(person, cls=f"p-0 text-xs font-mono", style=f"color: {name_color}")
    else:
        print(f"NOT SELECTED PERSON, {year_str_for_city=}")
        if year_str_for_city:
            return (Span(person + ", ", cls=f"p-0 text-xs font-mono", style=f"color: {name_color}"),
                    Span(selected_city + ", ", cls="p-0 text-xs text-gray-300"),
                    Span(year_str_for_city, cls=f"p-0 text-xs font-mono", style=f"color: {name_color}")) 
        else:
            if people_cities_for_year:
                for city in people_cities_for_year:
                    print(f"CHECKING CITY: {city} for {person}")
                    if city.username == person:
                        person_city_span = Span(city.name + ", ", cls="p-0 text-xs text-gray-300")
                        year_str_for_city = person_years_in_city(person, selected_person, first_selected_year, name_color, city.name)
                        return (Span(person + ", ", cls=f"p-0 text-xs", style=f"color: {name_color}"), 
                            person_city_span,
                            Span(year_str_for_city, cls="p-0 text-xs", style=f"color: {name_color}"))

            return Span(person, cls=f"p-0 text-xs font-mono", style=f"color: {name_color}")

def MarkedUsers(people_cities_for_year, marker_update_script, selected_users, selected_city, selected_person, years_selected):
    global people_colors
    first_selected_year = years_selected[0] if years_selected else None
    print(f"MarkedUsers, {selected_person=}, {selected_city=}: {marker_update_script}")
    
    return Div(
        Script(marker_update_script),
        Grid(Div(*[Div(person_header_display(person, people_cities_for_year, selected_person, selected_city, first_selected_year)) 
            for i, person in enumerate(selected_users_marked(selected_users))], cls="text-xs"), 
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
    document.getElementById('years-buttons-container').addEventListener('scroll', function() {
        saveScrollPosition();
    });
    """
    
    return Div(
        *buttons,
        Script(script),
        id='years-buttons-container',
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
                document.getElementById('years-buttons-container').scrollBy({
                    left: -200,
                    behavior: 'smooth'
                });
                setTimeout(() => {
                    saveScrollPosition();
                }, 500);
            });
            
            document.getElementById('scroll-right').addEventListener('click', () => {
                document.getElementById('years-buttons-container').scrollBy({
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
        const scrollPosition = document.getElementById('years-buttons-container').scrollLeft;
        localStorage.setItem('yearsScrollPosition', scrollPosition);
    };

    const restoreScrollPosition = () => {
        const savedPosition = localStorage.getItem('yearsScrollPosition');
        if (savedPosition !== null) {
            document.getElementById('years-buttons-container').scrollTo({
                left: parseInt(savedPosition),
                behavior: 'instant'
            });
        }
    };

    document.addEventListener('DOMContentLoaded', () => {
        restoreScrollPosition();
    });
    """) 

def LeftNav(selected_person, active_city, script=None):
    return Div(
        script if script else Script(),
        # Include city selection JavaScript
        Script(src="/static/js/city-selection.js"),
        # "Life on Map" unobtrusive text, light gray
        P(Span('Life Map, version 0.2', cls='mr-1'), Span('2025-02-26', cls='text-[10px] text-gray-400'), cls='ml-2 text-xs text-gray-500'),
        Grid(*get_distinct_users(selected_person, active_city), cls='gap-1', cols=1), 
        cls="p-2 h-screen overflow-y-auto",
        id="buttons-container",
        hx_swap_oob="true"
    )

def create_people():
    return Div(
        Dialog(
            Div(
                H3('Hello!', cls='text-lg font-bold'),
                P('Press ESC key or click the button below to close', cls='py-4'),
                Div(                            
                    Form(
                        # <!-- if there is a button in form, it will close the modal -->
                        Button('Close', cls='btn'),
                        method='dialog'
                    ),
                    cls='modal-action'
                ),
            ),
            id='my_modal_1',
            cls='modal-box'
        )
    )

tailwind_colors = {
    "slate": {
        "50": "rgb(248, 250, 252)",
        "100": "rgb(241, 245, 249)",
        "200": "rgb(226, 232, 240)",
        "300": "rgb(203, 213, 225)",
        "400": "rgb(148, 163, 184)",
        "500": "rgb(100, 116, 139)",
        "600": "rgb(71, 85, 105)",
        "700": "rgb(51, 65, 85)",
        "800": "rgb(30, 41, 59)",
        "900": "rgb(15, 23, 42)",
    },
    "gray": {
        "50": "rgb(249, 250, 251)",
        "100": "rgb(243, 244, 246)",
        "200": "rgb(229, 231, 235)",
        "300": "rgb(209, 213, 219)",
        "400": "rgb(156, 163, 175)",
        "500": "rgb(107, 114, 128)",
        "600": "rgb(75, 85, 99)",
        "700": "rgb(55, 65, 81)",
        "800": "rgb(31, 41, 55)",
        "900": "rgb(17, 24, 39)",
    },
    "zinc": {
        "50": "rgb(250, 250, 250)",
        "100": "rgb(244, 244, 245)",
        "200": "rgb(228, 228, 231)",
        "300": "rgb(212, 212, 216)",
        "400": "rgb(161, 161, 170)",
        "500": "rgb(113, 113, 122)",
        "600": "rgb(82, 82, 91)",
        "700": "rgb(63, 63, 70)",
        "800": "rgb(39, 39, 42)",
        "900": "rgb(24, 24, 27)",
    },
    "neutral": {
        "50": "rgb(250, 250, 250)",
        "100": "rgb(245, 245, 245)",
        "200": "rgb(229, 229, 229)",
        "300": "rgb(212, 212, 212)",
        "400": "rgb(163, 163, 163)",
        "500": "rgb(115, 115, 115)",
        "600": "rgb(82, 82, 82)",
        "700": "rgb(64, 64, 64)",
        "800": "rgb(38, 38, 38)",
        "900": "rgb(23, 23, 23)",
    },
    "stone": {
        "50": "rgb(250, 250, 249)",
        "100": "rgb(245, 245, 244)",
        "200": "rgb(231, 229, 228)",
        "300": "rgb(214, 211, 209)",
        "400": "rgb(168, 162, 158)",
        "500": "rgb(120, 113, 108)",
        "600": "rgb(87, 83, 78)",
        "700": "rgb(68, 64, 60)",
        "800": "rgb(41, 37, 36)",
        "900": "rgb(28, 25, 23)",
    },
    "red": {
        "50": "rgb(254, 242, 242)",
        "100": "rgb(254, 226, 226)",
        "200": "rgb(254, 202, 202)",
        "300": "rgb(252, 165, 165)",
        "400": "rgb(248, 113, 113)",
        "500": "rgb(239, 68, 68)",
        "600": "rgb(220, 38, 38)",
        "700": "rgb(185, 28, 28)",
        "800": "rgb(153, 27, 27)",
        "900": "rgb(127, 29, 29)",
    },
    "orange": {
        "50": "rgb(255, 247, 237)",
        "100": "rgb(255, 237, 213)",
        "200": "rgb(254, 215, 170)",
        "300": "rgb(253, 186, 116)",
        "400": "rgb(251, 146, 60)",
        "500": "rgb(249, 115, 22)",
        "600": "rgb(234, 88, 12)",
        "700": "rgb(194, 65, 12)",
        "800": "rgb(154, 52, 18)",
        "900": "rgb(124, 45, 18)",
    },
    "amber": {
        "50": "rgb(255, 251, 235)",
        "100": "rgb(254, 243, 199)",
        "200": "rgb(253, 230, 138)",
        "300": "rgb(252, 211, 77)",
        "400": "rgb(251, 191, 36)",
        "500": "rgb(245, 158, 11)",
        "600": "rgb(217, 119, 6)",
        "700": "rgb(180, 83, 9)",
        "800": "rgb(146, 64, 14)",
        "900": "rgb(120, 53, 15)",
    },
    "yellow": {
        "50": "rgb(254, 252, 232)",
        "100": "rgb(254, 249, 195)",
        "200": "rgb(254, 240, 138)",
        "300": "rgb(253, 224, 71)",
        "400": "rgb(250, 204, 21)",
        "500": "rgb(234, 179, 8)",
        "600": "rgb(202, 138, 4)",
        "700": "rgb(161, 98, 7)",
        "800": "rgb(133, 77, 14)",
        "900": "rgb(113, 63, 18)",
    },
    "lime": {
        "50": "rgb(247, 254, 231)",
        "100": "rgb(236, 252, 203)",
        "200": "rgb(217, 249, 157)",
        "300": "rgb(190, 242, 100)",
        "400": "rgb(163, 230, 53)",
        "500": "rgb(132, 204, 22)",
        "600": "rgb(101, 163, 13)",
        "700": "rgb(77, 124, 15)",
        "800": "rgb(63, 98, 18)",
        "900": "rgb(54, 83, 20)",
    },
    "green": {
        "50": "rgb(240, 253, 244)",
        "100": "rgb(220, 252, 231)",
        "200": "rgb(187, 247, 208)",
        "300": "rgb(134, 239, 172)",
        "400": "rgb(74, 222, 128)",
        "500": "rgb(34, 197, 94)",
        "600": "rgb(22, 163, 74)",
        "700": "rgb(21, 128, 61)",
        "800": "rgb(22, 101, 52)",
        "900": "rgb(20, 83, 45)",
    },
    "emerald": {
        "50": "rgb(236, 253, 245)",
        "100": "rgb(209, 250, 229)",
        "200": "rgb(167, 243, 208)",
        "300": "rgb(110, 231, 183)",
        "400": "rgb(52, 211, 153)",
        "500": "rgb(16, 185, 129)",
        "600": "rgb(5, 150, 105)",
        "700": "rgb(4, 120, 87)",
        "800": "rgb(6, 95, 70)",
        "900": "rgb(6, 78, 59)",
    },
    "teal": {
        "50": "rgb(240, 253, 250)",
        "100": "rgb(204, 251, 241)",
        "200": "rgb(153, 246, 228)",
        "300": "rgb(94, 234, 212)",
        "400": "rgb(45, 212, 191)",
        "500": "rgb(20, 184, 166)",
        "600": "rgb(13, 148, 136)",
        "700": "rgb(15, 118, 110)",
        "800": "rgb(17, 94, 89)",
        "900": "rgb(19, 78, 74)",
    },
    "cyan": {
        "50": "rgb(236, 254, 255)",
        "100": "rgb(207, 250, 254)",
        "200": "rgb(165, 243, 252)",
        "300": "rgb(103, 232, 249)",
        "400": "rgb(34, 211, 238)",
        "500": "rgb(6, 182, 212)",
        "600": "rgb(8, 145, 178)",
        "700": "rgb(14, 116, 144)",
        "800": "rgb(21, 94, 117)",
        "900": "rgb(22, 78, 99)",
    },
    "sky": {
        "50": "rgb(240, 249, 255)",
        "100": "rgb(224, 242, 254)",
        "200": "rgb(186, 230, 253)",
        "300": "rgb(125, 211, 252)",
        "400": "rgb(56, 189, 248)",
        "500": "rgb(14, 165, 233)",
        "600": "rgb(2, 132, 199)",
        "700": "rgb(3, 105, 161)",
        "800": "rgb(7, 89, 133)",
        "900": "rgb(12, 74, 110)",
    },
    "blue": {
        "50": "rgb(239, 246, 255)",
        "100": "rgb(219, 234, 254)",
        "200": "rgb(191, 219, 254)",
        "300": "rgb(147, 197, 253)",
        "400": "rgb(96, 165, 250)",
        "500": "rgb(59, 130, 246)",
        "600": "rgb(37, 99, 235)",
        "700": "rgb(29, 78, 216)",
        "800": "rgb(30, 64, 175)",
        "900": "rgb(30, 58, 138)",
    },
    "indigo": {
        "50": "rgb(238, 242, 255)",
        "100": "rgb(224, 231, 255)",
        "200": "rgb(199, 210, 254)",
        "300": "rgb(165, 180, 252)",
        "400": "rgb(129, 140, 248)",
        "500": "rgb(99, 102, 241)",
        "600": "rgb(79, 70, 229)",
        "700": "rgb(67, 56, 202)",
        "800": "rgb(55, 48, 163)",
        "900": "rgb(49, 46, 129)",
    },
    "violet": {
        "50": "rgb(245, 243, 255)",
        "100": "rgb(237, 233, 254)",
        "200": "rgb(221, 214, 254)",
        "300": "rgb(196, 181, 253)",
        "400": "rgb(167, 139, 250)",
        "500": "rgb(139, 92, 246)",
        "600": "rgb(124, 58, 237)",
        "700": "rgb(109, 40, 217)",
        "800": "rgb(91, 33, 182)",
        "900": "rgb(76, 29, 149)",
    },
    "purple": {
        "50": "rgb(250, 245, 255)",
        "100": "rgb(243, 232, 255)",
        "200": "rgb(233, 213, 255)",
        "300": "rgb(216, 180, 254)",
        "400": "rgb(192, 132, 252)",
        "500": "rgb(168, 85, 247)",
        "600": "rgb(147, 51, 234)",
        "700": "rgb(126, 34, 206)",
        "800": "rgb(107, 33, 168)",
        "900": "rgb(88, 28, 135)",
    },
    "fuchsia": {
        "50": "rgb(253, 244, 255)",
        "100": "rgb(250, 232, 255)",
        "200": "rgb(245, 208, 254)",
        "300": "rgb(240, 171, 252)",
        "400": "rgb(232, 121, 249)",
        "500": "rgb(217, 70, 239)",
        "600": "rgb(192, 38, 211)",
        "700": "rgb(162, 28, 175)",
        "800": "rgb(134, 25, 143)",
        "900": "rgb(112, 26, 117)",
    },
    "pink": {
        "50": "rgb(253, 242, 248)",
        "100": "rgb(252, 231, 243)",
        "200": "rgb(251, 207, 232)",
        "300": "rgb(249, 168, 212)",
        "400": "rgb(244, 114, 182)",
        "500": "rgb(236, 72, 153)",
        "600": "rgb(219, 39, 119)",
        "700": "rgb(190, 24, 93)",
        "800": "rgb(157, 23, 77)",
        "900": "rgb(131, 24, 67)",
    },
    "rose": {
        "50": "rgb(255, 241, 242)",
        "100": "rgb(255, 228, 230)",
        "200": "rgb(254, 205, 211)",
        "300": "rgb(253, 164, 175)",
        "400": "rgb(251, 113, 133)",
        "500": "rgb(244, 63, 94)",
        "600": "rgb(225, 29, 72)",
        "700": "rgb(190, 18, 60)",
        "800": "rgb(159, 18, 57)",
        "900": "rgb(136, 19, 55)",
    }
}
