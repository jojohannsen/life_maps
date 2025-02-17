from fasthtml.common import database
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