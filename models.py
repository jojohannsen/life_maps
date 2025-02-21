from fasthtml.common import database, Span, Div
import pathlib

# Database setup
pathlib.Path('data').mkdir(exist_ok=True)
DB_PATH = 'data/cities.db'
db = database(DB_PATH)

class CityLocation:
    id:int
    username:str
    name:str
    lat:float
    lon:float
    zoomlevel:int
    years:int
    start_year:int

city_locs = db.create(CityLocation, pk='id')
initial_user = 'no user selected'  # default user
city_locs.xtra(username=initial_user)  # Set initial filter 

class DBPersonContextManager:
    def __init__(self, temp_person, selected_person):
        self.temp_person = temp_person
        self.selected_person = selected_person

    def __enter__(self):
        city_locs.xtra(username=self.temp_person)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        city_locs.xtra(username=self.selected_person)

def _years_str(years_selected):
    if not years_selected: return ""
    elif len(years_selected) == 1: return f"{str(years_selected[0])}"
    else: return f"{years_selected[0]}-{years_selected[-1]}"

def person_years_in_city(person, selected_person, first_selected_year, lighter_color, selected_city):
    if not selected_city:
        return ""
    with DBPersonContextManager(person, selected_person):
        result = city_locs()
        if result:
            city_entries = [city for city in result if city.name == selected_city]
            if city_entries:
                # sort by start_year
                city_entries.sort(key=lambda x: x.start_year)
                # get the years for the city
                year_strs = [_years_str((city.start_year, city.start_year + city.years)) for city in city_entries]
                year_strs = [year_str.replace("-2026", "-present") + ", " for year_str in year_strs[:-1]] + [year_strs[-1]]
                if person == selected_person:
                    year_spans = []
                    for year_range, city in zip(year_strs, city_entries):
                        if city.start_year == first_selected_year:
                            year_spans.append(Span(year_range, cls="p-0 text-xs", style=f"color: {lighter_color}"))
                        else:
                            year_spans.append(Span(year_range, cls="p-0 text-xs text-gray-300"))
                    
                    return Span(*year_spans, cls="p-0 text-xs")
                else:
                    return ", ".join(year_strs)
    return 0