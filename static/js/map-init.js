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

// list of transparent colors
const transparent_colors = ['#ff000080', '#0000ff80', '#ff00ff80', '#00ffff80', '#ffffff80', '#00000080'];
// dictionary mapping person to color
const person_colors = {};
// next color to assign
let next_color = 0;
// non transparent colors
const non_transparent_colors = ['#ff0000', '#0000ff', '#ff00ff', '#00ffff', '#ffffff', '#000000'];
// dictionary mapping person to non transparent color
const person_non_transparent_colors = {};
// next non transparent color to assign
let next_non_transparent_color = 0;

function add_person_location(person, map, lat, lon, years) {
    console.log("Adding person marker", lat, lon, years)


    // get color for person, or assign a new one if they don't have one
    if (!person_colors[person]) {
        person_colors[person] = transparent_colors[next_color];
        next_color = (next_color + 1) % transparent_colors.length;
    }   
    if (!person_non_transparent_colors[person]) {
        person_non_transparent_colors[person] = non_transparent_colors[next_non_transparent_color];
        next_non_transparent_color = (next_non_transparent_color + 1) % non_transparent_colors.length;
    }
    // make concentric circles from 1 to years
    for (let i = 0; i < years; i++) {
        const width = 8 + i * 6;
        const height = 8 + i * 6;
        const el = document.createElement('div');
        el.className = 'mkr_' + alpha_only(person);
        el.style.width = `${width}px`;
        el.style.height = `${height}px`;
        el.style.backgroundSize = '100%';
        el.style.borderRadius = '50%';

        // first circle is solid, no border, the rest are transparent with border
        el.style.background = i === 0 ? person_non_transparent_colors[person] : 'transparent';
        el.style.border = i === 0 ? 'none' : `1px solid ${person_non_transparent_colors[person]}`;
        el.addEventListener('click', () => {
            window.alert(marker.properties.message);
        });

        // Add markers to the map.
        new mapboxgl.Marker(el)
            .setLngLat([lon, lat])
            .addTo(map);
    }
}