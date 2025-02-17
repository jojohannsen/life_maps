function initMap(mapboxToken, initialCenter, initialZoom) {
    mapboxgl.accessToken = mapboxToken;
    const map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/streets-v12',
        projection: 'mercator',
        center: initialCenter,
        zoom: initialZoom,
        antialias: true
    });

    // Add navigation controls
    map.addControl(new mapboxgl.NavigationControl());
    
    // Add fullscreen control
    map.addControl(new mapboxgl.FullscreenControl());
    
    // Add scale control
    map.addControl(new mapboxgl.ScaleControl({
        maxWidth: 80,
        unit: 'metric'
    }));

    return map;
}

function alpha_only(str) {
    return str.replace(/[^a-zA-Z]/g, '');
}

const scrollToButton = (id, alignment) => {
    // run this in 1/2 second
    setTimeout(() => {
        const button = document.getElementById(id);
        if (button) {
            button.scrollIntoView({
        behavior: 'smooth',
                block: 'nearest',
                inline: alignment
            });
        }
    }, 500);
};

// non transparent colors, duplicated in ui-components.py (MUST KEEP IN SYNC MANUALLY)
const circle_colors = ['#ff0000', '#0000ff', '#ff00ff', '#00ffff', '#ffffff', '#000000'];
// dictionary mapping person to non transparent color
const person_circle_colors = {};
// next non transparent color to assign
let next_circle_color = 0;
// map lat_lon_key to a dictionary of person to years
const latlon_to_person_years_dict = {};

function digit_only(str) {
    return str.replace(/[^0-9]/g, '');
}

const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
            console.log('Style changed:', mutation.target.style.opacity);
            console.trace(); // This will show the stack trace of what's changing it
        }
    });
});


function createMarkerElement(person, lat_lon_key, i, width, height, two_color_gradient_css) {
    const el = document.createElement('div');
    el.id = 'mkr_' + digit_only(lat_lon_key) + '_' + i;
    el.className = 'mkr_' + alpha_only(person);
    el.style.width = `${width}px`;
    el.style.height = `${height}px`;
    el.style.backgroundSize = '100%';
    el.style.borderRadius = '50%';
    if (two_color_gradient_css) {
        el.style.background = two_color_gradient_css;
        const ystr = i === 0 ? 'year' : 'years';
        el.title = `${person}, ${i + 1} ${ystr} shared`; 
    } else {
        // first circle is solid, the rest are transparent with border
        el.style.background = i === 0 ? person_circle_colors[person] : 'transparent';   
        el.style.border = i === 0 ? 'none' : `1px solid ${person_circle_colors[person]}`;
        const ystr = i === 0 ? 'year' : 'years';
        el.title = `${person}, ${i + 1} ${ystr}`; 
    }

    return el;
}

function add_person_location(person, lat_lon_key, map, lat, lon, years) {
    // get color for person, or assign a new one if they don't have one
    if (!person_circle_colors[person]) {
        person_circle_colors[person] = circle_colors[next_circle_color];
        next_circle_color = (next_circle_color + 1) % circle_colors.length;
    }
    person_color = person_circle_colors[person];
    console.log("Adding marker: ", person, person_color, lat_lon_key, years)
    const two_color_gradient_template = 'conic-gradient(COLOR_1 0deg 180deg, COLOR_2 180deg 360deg)';
    let two_color_gradient_css = '';
    let max_years_in_common = 0;
    let other_person = '';

    // if there is no one at this lat/lon, add them to the dictionary
    if (!latlon_to_person_years_dict[lat_lon_key]) {
        latlon_to_person_years_dict[lat_lon_key] = {};
    } else {
        console.log("People at this location: ", latlon_to_person_years_dict[lat_lon_key])
        // if there is someone at this lat/lon, markers depend on years difference
        const other_people = Object.keys(latlon_to_person_years_dict[lat_lon_key])
            .filter(p => p !== person);
        // for now, just use the first other person
        if (other_people.length > 0) {
            other_person = other_people[0];
            const other_years = latlon_to_person_years_dict[lat_lon_key][other_person];
            two_color_gradient_css = two_color_gradient_template
                .replace('COLOR_1', person_circle_colors[person] + '80')
                .replace('COLOR_2', person_circle_colors[other_person] + '80');
            console.log("Two color CSS:", two_color_gradient_css)
            max_years_in_common = Math.min(years, other_years);

            // remove existing markers for the years in common
            // so if there are two people, "johannes" and "farahnaz", and they have 3 years in common,
            // we would remove .mkr_johannes_0, .mkr_farahnaz_0, .mkr_johannes_1, .mkr_farahnaz_1, .mkr_johannes_2, .mkr_farahnaz_2
            function removeMarkers(person) {
                try {
                    const markerPrefix = 'mkr_' + digit_only(lat_lon_key) + '_';
                    const regex = new RegExp(`^${markerPrefix}\\d+$`);
                    const matchingMarkers = Array.from(document.querySelectorAll('[id]'))
                        .filter(el => regex.test(el.id) && el.className.includes('mkr_' + alpha_only(person)))
                        .filter(el => parseInt(el.id.split('_').pop()) < max_years_in_common);
                    matchingMarkers.forEach(m => m.remove());
                } catch (error) {
                    //console.error(`No existing markers found for ${person}:`, error);
                }
            }
            removeMarkers(person);
            removeMarkers(other_person);
        }
    }
    latlon_to_person_years_dict[lat_lon_key][person] = years;
    // make concentric circles from 1 to years
    // however, if max_years_in_common is non-zero, instead of individual circles,
    // make a single circle with a two color gradient
    if (max_years_in_common > 0) {
        const width = 2 + max_years_in_common * 6;
        const height = 2 + max_years_in_common * 6;
        console.log("Adding two color background, max_years_in_common: ", max_years_in_common, ", width: ", width, ", height: ", height)
        const el = createMarkerElement(person + " & " + other_person, lat_lon_key, max_years_in_common, width, height, two_color_gradient_css);
        // Add markers to the map.
        new mapboxgl.Marker(el)
            .setLngLat([lon, lat])
            .addTo(map);
        el.style.opacity = 0.5;
    } 
    for (let i = max_years_in_common; i < years; i++) {
        const width = 8 + i * 6;
        const height = 8 + i * 6;
        const el = createMarkerElement(person, lat_lon_key, i, width, height, '');
        console.log("Adding marker element colored circle, year ", i)
        // Add markers to the map.
        new mapboxgl.Marker(el)
            .setLngLat([lon, lat])
            .addTo(map);
    }
}