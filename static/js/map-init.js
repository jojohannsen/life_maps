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


// non transparent colors
const circle_colors = ['#ff0000', '#0000ff', '#ff00ff', '#00ffff', '#ffffff', '#000000'];
// dictionary mapping person to non transparent color
const person_circle_colors = {};
// next non transparent color to assign
let next_circle_color = 0;
// map lat_lon_key to a dictionary of person to years
const latlon_to_person_years_dict = {};

function add_person_location(person, lat_lon_key, map, lat, lon, years) {
    console.log("Adding person marker", lat, lon, years)
    const two_color_gradient_template = 'conic-gradient(COLOR_1 0deg 180deg, COLOR_2 180deg 360deg)';
    let two_color_gradient_css = '';
    let years_diff = 0;
    let max_years_in_common = 0;

    // if there is no one at this lat/lon, add them to the dictionary
    if (!latlon_to_person_years_dict[lat_lon_key]) {
        latlon_to_person_years_dict[lat_lon_key] = {};
        latlon_to_person_years_dict[lat_lon_key][person] = years;
    } else {
        // if there is someone at this lat/lon, markers depend on years difference
        const other_people = Object.keys(latlon_to_person_years_dict[lat_lon_key])
            .filter(p => p !== person);
        // for now, just use the first other person
        if (other_people.length > 0) {
            const other_person = other_people[0];
            const other_years = latlon_to_person_years_dict[lat_lon_key][other_person];
            two_color_gradient_css = two_color_gradient_template
                .replace('COLOR_1', person_circle_colors[person])
                .replace('COLOR_2', person_circle_colors[other_person]);
            years_diff = Math.abs(years - other_years);
            max_years_in_common = Math.min(years, other_years);
            if (years_diff > 0) {
                least_years_person = (years_diff > other_years) ? other_person : person;
                most_years_person = (years_diff > other_years) ? person : other_person;
                // remove existing markers for the years in common
                for (let i = 0; i < max_years_in_common; i++) {
                    const common_years_markers = document.querySelectorAll('.mkr_' + alpha_only(least_years_person) + '_' + i);
                    common_years_markers.forEach(m => m.remove());
                }
            } else {
                // remove the existing markers for the other person
                const other_person_markers = document.querySelectorAll('.mkr_' + alpha_only(other_person));
                other_person_markers.forEach(m => m.remove());
            }
        }
    }

    // get color for person, or assign a new one if they don't have one
    if (!person_circle_colors[person]) {
        person_circle_colors[person] = circle_colors[next_circle_color];
        next_circle_color = (next_circle_color + 1) % circle_colors.length;
    }   

    // make concentric circles from 1 to years
    for (let i = 0; i < years; i++) {
        const width = 8 + i * 6;
        const height = 8 + i * 6;
        const el = document.createElement('div');
        el.id = 'mkr_' + alpha_only(person) + '_' + i;
        el.className = 'mkr_' + alpha_only(person);
        el.style.width = `${width}px`;
        el.style.height = `${height}px`;
        el.style.backgroundSize = '100%';
        el.style.borderRadius = '50%';

        // first circle is solid, no border, the rest are transparent with border
        el.style.background = i === 0 ? person_circle_colors[person] : 'transparent';
        if ((i < max_years_in_common) && two_color_gradient_css) {
            el.style.background = two_color_gradient_css;
        }
        el.style.border = i === 0 ? 'none' : `1px solid ${person_circle_colors[person]}`;
        el.addEventListener('click', () => {
            window.alert(marker.properties.message);
        });

        // Add markers to the map.
        new mapboxgl.Marker(el)
            .setLngLat([lon, lat])
            .addTo(map);
    }
}