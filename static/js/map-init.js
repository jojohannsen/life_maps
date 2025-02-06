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

function add_person_location(person, map, lat, lon, years) {
    console.log("Adding person marker", lat, lon, years)
    const el = document.createElement('div');
    const width = 14 + years * 2;
    const height = 14 + years * 2;
    el.className = 'mkr_' + alpha_only(person);
    el.style.backgroundColor = '#ff000080';
    el.style.width = `${width}px`;
    el.style.height = `${height}px`;
    el.style.backgroundSize = '100%';
    el.style.borderRadius = '50%';

    el.addEventListener('click', () => {
        window.alert(marker.properties.message);
    });

    // Add markers to the map.
    new mapboxgl.Marker(el)
        .setLngLat([lon, lat])
        .addTo(map);
//    return marker;
}