from fasthtml.common import *
from hmac import compare_digest
import argparse

db = database("data/cities.db")

class CityLocation:
    id:int 
    name:str
    lat:float
    lon:float 
    zoomlevel:int
    username:str
    years:int
    start_year:int

city_locs = db.create(CityLocation)

def city_loc_generator(data, username, start_year=None):
    for s in data:
        years = 1
        if ',' in s:
            # if part to left of comma is a number, use it as the number of years   
            try:
                years = int(s.split(',',1)[0])
                s = s.split(',',1)[1]
            except ValueError:  
                pass
        s = s.strip()
        city_loc = CityLocation(name=s, zoomlevel=10, username=username, years=years, start_year=start_year)
        start_year = start_year + years if start_year is not None else None
        yield city_loc

# Define the default username
USERNAME = 'johannes'

# Parse command line arguments
parser = argparse.ArgumentParser(description='Process city locations for a user')
parser.add_argument('--username', default=USERNAME, help='Username to create/view city locations for')
args = parser.parse_args()

# Use command line username if provided, otherwise use default
active_username = args.username

table_name = "city_location"
if table_name in db.t:
    city_locs = db.t[table_name]
    # Set the username filter for all operations
    city_locs.xtra(username=active_username)
    result = city_locs()
else:
    result = []
    # Set the username filter for all operations
    city_locs.xtra(username=active_username)

if len(result) == 0:
    try:
        with open(f'people/{active_username}.txt', 'r') as f:
            data = [line.strip() for line in f if line.strip()]
        
        if data[0].startswith("born:"):
            start_year = int(data[0].split(':')[1])
            data = data[1:]
        else:
            start_year = None
        print(f"Creating user {active_username}")
        for offset, cl in enumerate(city_loc_generator(data, active_username, start_year)):
            city_locs.insert(cl)
    except FileNotFoundError:
        print(f"No locations file found for user {active_username}")
else:
    print(f"User found")

# Get all records for this username
result = city_locs()  # This automatically uses the xtra filter
print(list(result))

db.close()
