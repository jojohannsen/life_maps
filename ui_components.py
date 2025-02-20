from fasthtml.common import *
from monsterui.all import *
from models import city_locs, CityLocation
from map_utils import add_person_markers

# UI Constants
CITY_NAV_WIDTH = 'w-48'

def city_buttons(selected_city: CityLocation | None = None):
    user_city_data = city_locs()
    city_buttons = [make_city_button(city, selected_city) for city in user_city_data]

    return Div(
        *city_buttons,
        id='city-buttons-container',
        cls='space-y-2'
    )

def make_city_button(city, selected_city: CityLocation | None = None):
    button = Button(city.name, 
                   hx_trigger='click',
                   hx_get=f'/change-city/{city.id}',
                   hx_target='#city-buttons-container',
                   cls=f'text-left justify-start hover:bg-muted {CITY_NAV_WIDTH} ' + 
                       ('bg-blue-500 text-white' if selected_city and city.id == selected_city.id else 'bg-blue-50'))
    return DivLAligned(
        button,
        id=f'citybutton-{city.id}',
    )

def get_distinct_users(selected_person: str):
    from models import db
    
    result = db.query("select distinct username from city_location")
    options = [Option("Select person", value="")]  # Placeholder option
    options.extend([Option(row['username'], value=row['username']) for row in result])
    
    if not selected_person:
        options[0].selected = True
    else:
        for opt in options[1:]:
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

# MUST KEEP IN SYNC MANUALLY WITH static/js/map-init.js
circle_colors = ['#01bcfe', '#ff7d00', '#ff006d', '#adff02', '#8f00ff']

def selected_users_marked(selected_users):
    return [user['name'] for user in selected_users if user['is_shown_above_map']]

def _years_str(years_selected):
    if not years_selected: return ""
    elif len(years_selected) == 1: return f"{str(years_selected[0])}"
    else: return f"{years_selected[0]}-{years_selected[-1]}"

def user_display(user, selected_person, selected_city, years_selected, color):
    if user == selected_person:
        return (Span(user + ", ", cls="p-0 text-xs italic font-semibold", style=color), 
            Span(selected_city + ", ", cls="p-0 text-xs font-semibold"),
            Span(_years_str(years_selected), style=color, cls="p-0 text-xs italic")) 
    else: return Span(user, cls="p-0 text-xs italic font-semibold", style=color)

def MarkedUsers(selected_users, selected_city, selected_person, years_selected):
    print(f"MarkedUsers: {selected_users}")
    print(f"selected_city: {selected_city}")
    print(f"selected_person: {selected_person}")
    print(f"years_selected: {years_selected}")
    return Div(
        Grid(Div(*[Div(user_display(user, selected_person, selected_city, years_selected, f"color: {circle_colors[i % len(circle_colors)]}")) 
            for i, user in enumerate(selected_users_marked(selected_users))], cls="text-xs"), 
            cols=1, cls="gap-0"),
        hx_swap_oob="true",
        cls="relative w-full p-0",
        id="marked-users-container"
    )

# Years UI Components
def create_year_buttons(years, years_selected, base_css, selected_css, unselected_css):
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

def YearsButtons(years, years_selected):
    selected_css = 'text-gray-700 bg-green-200 hover:bg-green-400'
    unselected_css = 'text-gray-500 bg-yellow-200 hover:bg-yellow-400'
    base_css = 'italic text-xs h-full rounded-none pl-1 pr-1 py-0 border'
    buttons = create_year_buttons(years, years_selected, base_css, selected_css, unselected_css)
    
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
        YearsButtons(years, years_selected),
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