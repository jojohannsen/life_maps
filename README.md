# life_maps
Where people have lived visualization

##### Data

The **people** folder has a text file for each person.  The format is just a sequence of lines of text:

[years,] <place lived>

The "place lived" is looked up in MapBox, so it can be as precise as you want.  Here's an example in 'johannes.txt' showing roughly where I've lived.

```
born: 1959
1,Tucson, AZ
17,Gadsden, AZ
7,Cambridge, MA
1,Oakland, CA
34,Los Angeles, CA
*,Joshua Tree, CA
```

The **repop** shell script takes all the text files in the **people** folder, and puts them in **data/cities.db** which the application uses.

Since the DB doesn't have latitude/longitude locations initially, it uses the MapBox API to get those locations.   This requires a MapBox API Key, code is looking for a **MAPBOX_TOKEN** environment variable.
