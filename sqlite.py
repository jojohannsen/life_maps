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
    username:str  # Added username field

city_locs = db.create(CityLocation)

def city_loc_generator(data, username):
    for s in data:
        city_loc = CityLocation(name=s, zoomlevel=10, username=username)
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
        
        print(f"Creating user {active_username}")
        for cl in city_loc_generator(data, active_username):
            city_locs.insert(cl)
    except FileNotFoundError:
        print(f"No locations file found for user {active_username}")
else:
    print(f"User found")

# Get all records for this username
result = city_locs()  # This automatically uses the xtra filter
print(list(result))

db.close()
