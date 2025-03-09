from fasthtml.common import database, Span
from datetime import datetime
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
    color:str

city_locs = db.create(CityLocation, pk='id')
people_colors = {}
for city in city_locs():
    people_colors[city.username] = city.color

def _years_str(start_year, number_of_years):
    # get current year
    current_year = datetime.now().year
    if number_of_years == 1: return str(start_year)
    elif (start_year + number_of_years - 1) == current_year: return f"{start_year}-present"
    else: return f"{start_year}-{start_year + number_of_years - 1}"

def person_years_in_city(person, selected_person, first_selected_year, lighter_color, selected_city):
    if not selected_city:
        return ""
    result = cities_occupied_by_person(person)
    if result:
        city_entries = [city for city in result if city.name == selected_city]
        if city_entries:
            # sort by start_year
            city_entries.sort(key=lambda x: x.start_year)
            # get the years for the city
            year_strs = [_years_str(city.start_year, city.years) for city in city_entries]
            year_strs = [year_str + ", " for year_str in year_strs[:-1]] + [year_strs[-1]]
            if person == selected_person:
                year_spans = []
                for year_range, city in zip(year_strs, city_entries):
                    # Check if the selected year falls within this city's year range
                    is_year_in_range = (first_selected_year is not None and 
                                        city.start_year <= first_selected_year < city.start_year + city.years)
                    if is_year_in_range:
                        year_spans.append(Span(year_range, cls="p-0 text-xs", style=f"color: {lighter_color}"))
                    else:
                        year_spans.append(Span(year_range, cls="p-0 text-xs text-gray-300"))
                    
                return Span(*year_spans, cls="p-0 text-xs")
            else:
                return ", ".join(year_strs)
    return 0

# Add a helper function for filtered queries
def cities_occupied_by_person(person_name):
    print(f"cities_occupied_by_person: {person_name}")
    result = [city for city in city_locs() if city.username == person_name]
    # order by start_year
    result.sort(key=lambda x: x.start_year)
    return result

def people_in_year(year):
    result = [city for city in city_locs() if year in range(city.start_year, city.start_year + city.years)]
    return result
