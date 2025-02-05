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