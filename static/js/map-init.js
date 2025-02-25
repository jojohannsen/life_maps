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

// map lat_lon_key to a dictionary of person to years
const latlon_to_person_years_dict = {};

function digit_only(str) {
    return str.replace(/[^0-9]/g, '');
}

const tailwindColors = {
    slate: {
      50: 'rgb(248, 250, 252)',
      100: 'rgb(241, 245, 249)',
      200: 'rgb(226, 232, 240)',
      300: 'rgb(203, 213, 225)',
      400: 'rgba(148, 163, 184, 0.5)',
      500: 'rgb(100, 116, 139)',
      600: 'rgb(71, 85, 105)',
      700: 'rgb(51, 65, 85)',
      800: 'rgb(30, 41, 59)',
      900: 'rgb(15, 23, 42)',
    },
    gray: {
      50: 'rgb(249, 250, 251)',
      100: 'rgb(243, 244, 246)',
      200: 'rgb(229, 231, 235)',
      300: 'rgb(209, 213, 219)',
      400: 'rgba(156, 163, 175, 0.5)',
      500: 'rgb(107, 114, 128)',
      600: 'rgb(75, 85, 99)',
      700: 'rgb(55, 65, 81)',
      800: 'rgb(31, 41, 55)',
      900: 'rgb(17, 24, 39)',
    },
    zinc: {
      50: 'rgb(250, 250, 250)',
      100: 'rgb(244, 244, 245)',
      200: 'rgb(228, 228, 231)',
      300: 'rgb(212, 212, 216)',
      400: 'rgba(161, 161, 170, 0.5)',
      500: 'rgb(113, 113, 122)',
      600: 'rgb(82, 82, 91)',
      700: 'rgb(63, 63, 70)',
      800: 'rgb(39, 39, 42)',
      900: 'rgb(24, 24, 27)',
    },
    neutral: {
      50: 'rgb(250, 250, 250)',
      100: 'rgb(245, 245, 245)',
      200: 'rgb(229, 229, 229)',
      300: 'rgb(212, 212, 212)',
      400: 'rgba(163, 163, 163, 0.5)',
      500: 'rgb(115, 115, 115)',
      600: 'rgb(82, 82, 82)',
      700: 'rgb(64, 64, 64)',
      800: 'rgb(38, 38, 38)',
      900: 'rgb(23, 23, 23)',
    },
    stone: {
      50: 'rgb(250, 250, 249)',
      100: 'rgb(245, 245, 244)',
      200: 'rgb(231, 229, 228)',
      300: 'rgb(214, 211, 209)',
      400: 'rgba(168, 162, 158, 0.5)',
      500: 'rgb(120, 113, 108)',
      600: 'rgb(87, 83, 78)',
      700: 'rgb(68, 64, 60)',
      800: 'rgb(41, 37, 36)',
      900: 'rgb(28, 25, 23)',
    },
    red: {
      50: 'rgb(254, 242, 242)',
      100: 'rgb(254, 226, 226)',
      200: 'rgb(254, 202, 202)',
      300: 'rgb(252, 165, 165)',
      400: 'rgba(248, 113, 113, 0.5)',
      500: 'rgb(239, 68, 68)',
      600: 'rgb(220, 38, 38)',
      700: 'rgb(185, 28, 28)',
      800: 'rgb(153, 27, 27)',
      900: 'rgb(127, 29, 29)',
    },
    orange: {
      50: 'rgb(255, 247, 237)',
      100: 'rgb(255, 237, 213)',
      200: 'rgb(254, 215, 170)',
      300: 'rgb(253, 186, 116)',
      400: 'rgba(251, 146, 60, 0.5)',
      500: 'rgb(249, 115, 22)',
      600: 'rgb(234, 88, 12)',
      700: 'rgb(194, 65, 12)',
      800: 'rgb(154, 52, 18)',
      900: 'rgb(124, 45, 18)',
    },
    amber: {
      50: 'rgb(255, 251, 235)',
      100: 'rgb(254, 243, 199)',
      200: 'rgb(253, 230, 138)',
      300: 'rgb(252, 211, 77)',
      400: 'rgba(251, 191, 36, 0.5)',
      500: 'rgb(245, 158, 11)',
      600: 'rgb(217, 119, 6)',
      700: 'rgb(180, 83, 9)',
      800: 'rgb(146, 64, 14)',
      900: 'rgb(120, 53, 15)',
    },
    yellow: {
      50: 'rgb(254, 252, 232)',
      100: 'rgb(254, 249, 195)',
      200: 'rgb(254, 240, 138)',
      300: 'rgb(253, 224, 71)',
      400: 'rgba(250, 204, 21, 0.5)',
      500: 'rgb(234, 179, 8)',
      600: 'rgb(202, 138, 4)',
      700: 'rgb(161, 98, 7)',
      800: 'rgb(133, 77, 14)',
      900: 'rgb(113, 63, 18)',
    },
    lime: {
      50: 'rgb(247, 254, 231)',
      100: 'rgb(236, 252, 203)',
      200: 'rgb(217, 249, 157)',
      300: 'rgb(190, 242, 100)',
      400: 'rgba(163, 230, 53, 0.5)',
      500: 'rgb(132, 204, 22)',
      600: 'rgb(101, 163, 13)',
      700: 'rgb(77, 124, 15)',
      800: 'rgb(63, 98, 18)',
      900: 'rgb(54, 83, 20)',
    },
    green: {
      50: 'rgb(240, 253, 244)',
      100: 'rgb(220, 252, 231)',
      200: 'rgb(187, 247, 208)',
      300: 'rgb(134, 239, 172)',
      400: 'rgba(74, 222, 128, 0.5)',
      500: 'rgb(34, 197, 94)',
      600: 'rgb(22, 163, 74)',
      700: 'rgb(21, 128, 61)',
      800: 'rgb(22, 101, 52)',
      900: 'rgb(20, 83, 45)',
    },
    emerald: {
      50: 'rgb(236, 253, 245)',
      100: 'rgb(209, 250, 229)',
      200: 'rgb(167, 243, 208)',
      300: 'rgb(110, 231, 183)',
      400: 'rgba(52, 211, 153, 0.5)',
      500: 'rgb(16, 185, 129)',
      600: 'rgb(5, 150, 105)',
      700: 'rgb(4, 120, 87)',
      800: 'rgb(6, 95, 70)',
      900: 'rgb(6, 78, 59)',
    },
    teal: {
      50: 'rgb(240, 253, 250)',
      100: 'rgb(204, 251, 241)',
      200: 'rgb(153, 246, 228)',
      300: 'rgb(94, 234, 212)',
      400: 'rgba(45, 212, 191, 0.5)',
      500: 'rgb(20, 184, 166)',
      600: 'rgb(13, 148, 136)',
      700: 'rgb(15, 118, 110)',
      800: 'rgb(17, 94, 89)',
      900: 'rgb(19, 78, 74)',
    },
    cyan: {
      50: 'rgb(236, 254, 255)',
      100: 'rgb(207, 250, 254)',
      200: 'rgb(165, 243, 252)',
      300: 'rgb(103, 232, 249)',
      400: 'rgba(34, 211, 238, 0.5)',
      500: 'rgb(6, 182, 212)',
      600: 'rgb(8, 145, 178)',
      700: 'rgb(14, 116, 144)',
      800: 'rgb(21, 94, 117)',
      900: 'rgb(22, 78, 99)',
    },
    sky: {
      50: 'rgb(240, 249, 255)',
      100: 'rgb(224, 242, 254)',
      200: 'rgb(186, 230, 253)',
      300: 'rgb(125, 211, 252)',
      400: 'rgba(56, 189, 248, 0.5)',
      500: 'rgb(14, 165, 233)',
      600: 'rgb(2, 132, 199)',
      700: 'rgb(3, 105, 161)',
      800: 'rgb(7, 89, 133)',
      900: 'rgb(12, 74, 110)',
    },
    blue: {
      50: 'rgb(239, 246, 255)',
      100: 'rgb(219, 234, 254)',
      200: 'rgb(191, 219, 254)',
      300: 'rgb(147, 197, 253)',
      400: 'rgba(96, 165, 250, 0.5)',
      500: 'rgb(59, 130, 246)',
      600: 'rgb(37, 99, 235)',
      700: 'rgb(29, 78, 216)',
      800: 'rgb(30, 64, 175)',
      900: 'rgb(30, 58, 138)',
    },
    indigo: {
      50: 'rgb(238, 242, 255)',
      100: 'rgb(224, 231, 255)',
      200: 'rgb(199, 210, 254)',
      300: 'rgb(165, 180, 252)',
      400: 'rgba(129, 140, 248, 0.5)',
      500: 'rgb(99, 102, 241)',
      600: 'rgb(79, 70, 229)',
      700: 'rgb(67, 56, 202)',
      800: 'rgb(55, 48, 163)',
      900: 'rgb(49, 46, 129)',
    },
    violet: {
      50: 'rgb(245, 243, 255)',
      100: 'rgb(237, 233, 254)',
      200: 'rgb(221, 214, 254)',
      300: 'rgb(196, 181, 253)',
      400: 'rgba(167, 139, 250, 0.5)',
      500: 'rgb(139, 92, 246)',
      600: 'rgb(124, 58, 237)',
      700: 'rgb(109, 40, 217)',
      800: 'rgb(91, 33, 182)',
      900: 'rgb(76, 29, 149)',
    },
    purple: {
      50: 'rgb(250, 245, 255)',
      100: 'rgb(243, 232, 255)',
      200: 'rgb(233, 213, 255)',
      300: 'rgb(216, 180, 254)',
      400: 'rgba(192, 132, 252, 0.5)',
      500: 'rgb(168, 85, 247)',
      600: 'rgb(147, 51, 234)',
      700: 'rgb(126, 34, 206)',
      800: 'rgb(107, 33, 168)',
      900: 'rgb(88, 28, 135)',
    },
    fuchsia: {
      50: 'rgb(253, 244, 255)',
      100: 'rgb(250, 232, 255)',
      200: 'rgb(245, 208, 254)',
      300: 'rgb(240, 171, 252)',
      400: 'rgba(232, 121, 249, 0.5)',
      500: 'rgb(217, 70, 239)',
      600: 'rgb(192, 38, 211)',
      700: 'rgb(162, 28, 175)',
      800: 'rgb(134, 25, 143)',
      900: 'rgb(112, 26, 117)',
    },
    pink: {
      50: 'rgb(253, 242, 248)',
      100: 'rgb(252, 231, 243)',
      200: 'rgb(251, 207, 232)',
      300: 'rgb(249, 168, 212)',
      400: 'rgba(244, 114, 182, 0.5)',
      500: 'rgb(236, 72, 153)',
      600: 'rgb(219, 39, 119)',
      700: 'rgb(190, 24, 93)',
      800: 'rgb(157, 23, 77)',
      900: 'rgb(131, 24, 67)',
    },
    rose: {
      50: 'rgb(255, 241, 242)',
      100: 'rgb(255, 228, 230)',
      200: 'rgb(254, 205, 211)',
      300: 'rgb(253, 164, 175)',
      400: 'rgba(251, 113, 133, 0.5)',
      500: 'rgb(244, 63, 94)',
      600: 'rgb(225, 29, 72)',
      700: 'rgb(190, 18, 60)',
      800: 'rgb(159, 18, 57)',
      900: 'rgb(136, 19, 55)',
    }
  };
  


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
        console.log("person: " + person + ", color: " + people_colors[person])
        el.style.background = i === 0 ? `${tailwindColors[people_colors[person]]['500']}` : 'transparent';   
        s = `1px solid ${tailwindColors[people_colors[person]]['500']}`;
        console.log("person: " + person + ", border css: " + s);
        el.style.border = i === 0 ? 'none' : s;
        console.log("Adding marker element colored circle, year ", i, "color: ", people_colors[person])
    }

    return el;
}

function add_person_location(person, lat_lon_key, map, lat, lon, years) {
    person_color = people_colors[person];

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
                .replace('COLOR_1', tailwindColors[people_colors[person]]['400'])
                .replace('COLOR_2', tailwindColors[people_colors[other_person]]['400']);
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
    console.log("Adding person to latlon_to_person_years_dict: ", person, lat_lon_key, years)
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