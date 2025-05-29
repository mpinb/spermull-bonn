// Initialize Leaflet map
var map = L.map('map').setView([50.7374, 7.0982], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

let geojsonData = null;
let geoJsonLayer = null; // Store the current layer so we can remove it

// Dynamically update circleMarker radius on zoom
map.on('zoomend', function () {
    if (geoJsonLayer) {
        const zoom = map.getZoom();
        // Example: base radius 2 at zoom 13, increase by 1.2 per zoom level above 13
        let radius = 2 + Math.max(0, zoom - 13) * 1.2;
        geoJsonLayer.eachLayer(function (layer) {
            console.log('Layer type:', layer);
            if (layer instanceof L.circleMarker) {
                console.log('Updating radius for layer:', layer);
                layer.setRadius(radius);
            }
        });
    }
});

// --- Address Autocomplete ---
function setupAddressAutocomplete() {
    const locationInput = document.getElementById('location');
    const datalist = document.getElementById('address-list');
    let addresses = [];

    // Fetch addresses from JSON
    fetch('data/addresses.json')
        .then(response => response.json())
        .then(data => { addresses = data; });

    locationInput.addEventListener('input', function() {
        const value = this.value.toLowerCase();
        // Filter addresses that include the input value
        const matches = addresses.filter(addr => addr.toLowerCase().includes(value)).slice(0, 10);
        // Clear previous options
        datalist.innerHTML = '';
        // Add new options
        matches.forEach(addr => {
            const option = document.createElement('option');
            option.value = addr;
            datalist.appendChild(option);
        });
    });
}

// --- Set Default Dates ---
function setDefaultDates() {
    const date1 = document.getElementById('date1');
    const date2 = document.getElementById('date2');
    const today = new Date();
    const nextWeek = new Date();
    nextWeek.setDate(today.getDate() + 2);

    // Format as yyyy-mm-dd
    const toISO = d => d.toISOString().split('T')[0];
    date1.value = toISO(today);
    date2.value = toISO(nextWeek);
}

// --- Filter GeoJSON by Date ---
function filterGeoJsonByDate(geojsonData, fromDate, toDate) {
    const filteredFeatures = geojsonData.features.filter(feature => {
        let dates = feature.properties.date;
        if (!dates) return false;
        if (!Array.isArray(dates)) dates = [dates];
        // Keep feature if ANY date is in range
        return dates.some(date => date >= fromDate && date <= toDate);
    });
    return {
        type: "FeatureCollection",
        features: filteredFeatures
    };
}

// --- Get Filtered GeoJSON from Inputs ---
function getFilteredGeoJson(geojsonData) {
    const date1 = document.getElementById('date1').value.replace(/-/g, '');
    const date2 = document.getElementById('date2').value.replace(/-/g, '');
    return filterGeoJsonByDate(geojsonData, date1, date2);
}

// --- Render GeoJSON on Map ---
function renderGeoJsonOnMap(filtered, fillColor, erasePrevious = true) {
    // Remove previous layer if it exists
    if (erasePrevious) {
        map.eachLayer(function(layer) {
            // Don't remove the tile layer (keep the base map)
            if (layer !== geoJsonLayer && layer instanceof L.TileLayer) return;
            if (layer !== geoJsonLayer && !(layer instanceof L.GeoJSON)) return;
            map.removeLayer(layer);
        });
    }
    // Add new filtered GeoJSON layer
    geoJsonLayer = L.geoJSON(filtered, {
        pointToLayer: function(feature, latlng) {
            return L.circleMarker(latlng, {
                radius: 2,
                fillColor: fillColor || "#007bff", // Default color
                color: "#fff",
                weight: 0.3,
                opacity: 0.8,
                fillOpacity: 0.8
            });
        },
        onEachFeature: function(feature, layer) {
            const address = feature.properties.strasse || "No address";
            let dates = feature.properties.date || [];
            if (!Array.isArray(dates)) dates = [dates];
            // Format all dates
            const formattedDates = dates.map(date => {
                if (/^\d{8}$/.test(date)) {
                    const year = date.substring(0, 4);
                    const month = date.substring(4, 6);
                    const day = date.substring(6, 8);
                    const d = new Date(`${year}-${month}-${day}`);
                    return d.toLocaleDateString('en-EN', { day: '2-digit', month: 'long', year: 'numeric' });
                }
                return date;
            }).join('<br>');
            layer.bindTooltip(
                `<strong>${address}</strong><br>${formattedDates}`,
                { direction: "top", offset: [0, -8] }
            );
        }
    }).addTo(map);

    // Optionally fit map to markers
    if (filtered.features.length > 0) {
        const bounds = geoJsonLayer.getBounds();
        map.fitBounds(bounds, { maxZoom: 13 });
    }
}

// --- Load GeoJSON Data ---
function loadGeoJsonData() {
    fetch('data/merged.geojson')
        .then(response => response.json())
        .then(data => {
            geojsonData = data;
            filtered = getFilteredGeoJson(geojsonData);
            renderGeoJsonOnMap(filtered, "#007bff");
            console.log('GeoJSON loaded:', geojsonData);
        })
        .catch(err => {
            console.error('Failed to load GeoJSON:', err);
        });
}


// --- Setup Filter Button ---
function setupFilterButton() {
    var filtered = null; // Store the filtered GeoJSON
    const filterBtn = document.getElementById('filter-btn');
    if (filterBtn) {
        filterBtn.addEventListener('click', function() {
            if (geojsonData) {
                filtered = getFilteredGeoJson(geojsonData);
                renderGeoJsonOnMap(filtered, "#007bff");
            } else {
                console.warn('GeoJSON data not loaded yet.');
            }
        });
    }
}

// --- Find Dates Button ---
function setupFindDatesButton() {
    const findDatesBtn = document.getElementById('find-dates-btn');
    if (findDatesBtn) {
        findDatesBtn.addEventListener('click', function() {
            if (!geojsonData) {
                console.warn('GeoJSON data not loaded yet.');
                return;
            }
            const locationInput = document.getElementById('location').value.trim().toLowerCase();
            if (!locationInput) {
                alert('Please enter a location.');
                return;
            }
            // Find features where strasse matches the input (case-insensitive)
            const matches = geojsonData.features.filter(feature => {
                const strasse = (feature.properties.strasse || '').toLowerCase();
                return strasse === locationInput;
            });

            if (matches.length === 0) {
                alert('No matching address found.');
            } else {
                // Show all dates for the matched address
                const dates = matches.flatMap(f => Array.isArray(f.properties.date) ? f.properties.date : [f.properties.date]).filter(Boolean);
                const nextDatesDiv = document.getElementById('next_dates');
                nextDatesDiv.style.display = 'block';
                nextDatesDiv.innerHTML = '';
                dates.forEach(date => {
                    // Format date as DD MMMM YYYY
                    let formatted = date;
                    if (/^\d{8}$/.test(date)) {
                        const year = date.substring(0, 4);
                        const month = date.substring(4, 6);
                        const day = date.substring(6, 8);
                        const d = new Date(`${year}-${month}-${day}`);
                        formatted = d.toLocaleDateString('en-EN', { day: '2-digit', month: 'long', year: 'numeric' });
                    }
                    const div = document.createElement('div');
                    div.textContent = formatted;
                    nextDatesDiv.appendChild(div);
                });
                const loc_filter = filterGeoJsonByDate(geojsonData, dates[0], dates[0]);
                console.log('Filtered GeoJSON for location:', loc_filter);
                renderGeoJsonOnMap(loc_filter, "#007bff");
                renderGeoJsonOnMap(matches, "#ff7b00", false);
            }
        });
    }
}

// --- DOMContentLoaded Event ---
document.addEventListener('DOMContentLoaded', function() {
    setupAddressAutocomplete();
    setDefaultDates();
    setupFilterButton();
    setupFindDatesButton();
    loadGeoJsonData();
    const modeLocation = document.getElementById('mode-location');
    const modeDate = document.getElementById('mode-date');
    const dateFields = document.getElementById('date-fields');
    const locationFields = document.getElementById('location-fields');
    const next_dates_div = document.getElementById('next_dates');

    function showLocationMode() {
        next_dates_div.style.display = 'block';
        if (geoJsonLayer) {
        map.removeLayer(geoJsonLayer);
        }
        modeLocation.classList.add('active');
        modeDate.classList.remove('active');
        dateFields.style.display = 'none';
        locationFields.style.display = '';
    }
    function showDateMode() {
        next_dates_div.style.display = 'none';
        modeDate.classList.add('active');
        modeLocation.classList.remove('active');
        dateFields.style.display = '';
        locationFields.style.display = 'none';
    }

    // Default: show location mode
    showDateMode();

    modeLocation.addEventListener('click', showLocationMode);
    modeDate.addEventListener('click', function () {
        showDateMode();
        if (geojsonData) {
            filtered = getFilteredGeoJson(geojsonData);
            renderGeoJsonOnMap(filtered, "#007bff");
        }
    });
});


