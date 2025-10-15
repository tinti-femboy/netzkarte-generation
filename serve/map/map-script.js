var searchbar = new maplibreSearchBox.MapLibreSearchControl({
        useMapFocusPoint: true,
        onResultSelected: feature => {
          //add code here to take some action when a result is selected.

        },
        baseUrl: "https://api-eu.stadiamaps.com",
      });

let protocol = new pmtiles.Protocol();
maplibregl.addProtocol("pmtiles", protocol.tile);

// 2. Define the map object
const map = new maplibregl.Map({
    container: 'map', // The container ID
    // style: "map/basemap-style.json",
    style: "map/coveragemap-style.json",

    center: [10.45, 51.16], // Centered on Germany
    zoom: 5.5 // Starting zoom level
});

const popup = new maplibregl.Popup({
closeButton: false, // No close button on a hover popup
closeOnClick: false, // Stays open even if the map is clicked
anchor: 'bottom-left' // Anchors the popup to the feature's location
});

map.addControl(
    new maplibregl.GeolocateControl({
        positionOptions: {
            enableHighAccuracy: true
        },
        trackUserLocation: true
    })
);

map.addControl(searchbar, "top-left");


map.on('mouseenter', 'cells-layer', (e) => {
            // Change the cursor style as a UI indicator.
            map.getCanvas().style.cursor = 'pointer';


            // Get the coordinates and description from the hovered feature.
            const coordinates = e.features[0].geometry.coordinates.slice();
            const description = e.features[0].properties.description;
            
            // Ensure that if the map is zoomed out such that multiple
            // copies of the feature are visible, the popup appears
            // over the copy being pointed to.
            while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
                coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
            }

            // Populate the popup and set its coordinates
            // based on the feature found.
            let popupMessage = "<b>" + e.features.length + 
                ( e.features[0].properties.provider === 't'   ? '</b> Mobilfunksender der <span class="telekom_span">Telekom</span> in diese Richtung'
                : e.features[0].properties.provider === 'v'   ? '</b> Mobilfunksender der <span class="vodafone_span">Vodafone</span> in diese Richtung'
                : e.features[0].properties.provider === 'b'   ? '</b> Mobilfunksender der <span class="telefonica_span">Telefonica/o2</span> in diese Richtung'
                : e.features[0].properties.provider === 'tv'  ? '</b> Mobilfunksender der <span class="telekom_span">Telekom</span> und <span class="vodafone_span">Vodafone</span> in diese Richtung'
                : e.features[0].properties.provider === 'tb'  ? '</b> Mobilfunksender der <span class="telekom_span">Telekom</span> und <span class="telefonica_span">o2</span> in diese Richtung'
                : e.features[0].properties.provider === 'vb'  ? '</b> Mobilfunksender der <span class="vodafone_span">Vodafone</span> und <span class="telefonica_span">o2</span> in diese Richtung'
                : e.features[0].properties.provider === 'tvb' ? '</b> Mobilfunksender <b><i>aller drei <span class="colorize_fun"><span style="color:#00fc00;">M</span><span style="color:#00fd61;">o</span><span style="color:#00fec2;">b</span><span style="color:#00efef;">i</span><span style="color:#00c6c6;">l</span><span style="color:#009d9d;">f</span><span style="color:#0069b1;">u</span><span style="color:#0031d9;">n</span><span style="color:#0700f7;">k</span><span style="color:#4200d2;">n</span><span style="color:#7e00ae;">e</span><span style="color:#ae00ae;">t</span><span style="color:#d400d4;">z</span><span style="color:#fa00fa;">b</span><span style="color:#ff00aa;">e</span><span style="color:#ff0048;">t</span><span style="color:#fe0c00;">r</span><span style="color:#fd3c00;">e</span><span style="color:#fc6c00;">i</span><span style="color:#fc9d00;">b</span><span style="color:#fdce00;">e</span><span style="color:#ffff00;">r</span></span></b></i> in diese Richtung'
                : '</b> Mobilfunksender eines unbekannten Netzbetreibers in diese Richtung')
            popup.setLngLat(coordinates[0][0]).setHTML(popupMessage).addTo(map);
        });

// map.on('mouseleave', 'cells-layer', () => {
//     map.getCanvas().style.cursor = '';
//     popup.remove();
// });

map.on('mouseenter', 'unitless-towers', (e) => {
            // Change the cursor style as a UI indicator.
            map.getCanvas().style.cursor = 'pointer';


            // Get the coordinates and description from the hovered feature.
            const coordinates = e.features[0].geometry.coordinates.slice();
            
            // Ensure that if the map is zoomed out such that multiple
            // copies of the feature are visible, the popup appears
            // over the copy being pointed to.
            while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
                coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
            }

            // Populate the popup and set its coordinates
            // based on the feature found.
            let popupMessage = "Unbekannter " +
                ( e.features[0].properties.provider === 't' ? 'Mobilfunksender der <span class="telekom_span">Telekom</span>' 
                : e.features[0].properties.provider === 'v' ? 'Mobilfunksender der <span class="vodafone_span">Vodafone</span>'
                : e.features[0].properties.provider === 'b' ? 'Mobilfunksender der <span class="telefonica_span">Telefonica/o2</span>'

                : e.features[0].properties.provider === 'tv' ? 'Mobilfunksender der <span class="telekom_span">Telekom</span> und <span class="vodafone_span">Vodafone</span>'
                : e.features[0].properties.provider === 'tb' ? 'Mobilfunksender der <span class="telekom_span">Telekom</span> und <span class="telefonica_span">o2</span>'
                : e.features[0].properties.provider === 'vb' ? 'Mobilfunksender der <span class="vodafone_span">Vodafone</span> und <span class="telefonica_span">o2</span>'

                : e.features[0].properties.provider === 'tvb' ? 'Mobilfunksender von <b><i>allen drei <span class="colorize_fun"><span style="color:#00fc00;">M</span><span style="color:#00fd61;">o</span><span style="color:#00fec2;">b</span><span style="color:#00efef;">i</span><span style="color:#00c6c6;">l</span><span style="color:#009d9d;">f</span><span style="color:#0069b1;">u</span><span style="color:#0031d9;">n</span><span style="color:#0700f7;">k</span><span style="color:#4200d2;">n</span><span style="color:#7e00ae;">e</span><span style="color:#ae00ae;">t</span><span style="color:#d400d4;">z</span><span style="color:#fa00fa;">b</span><span style="color:#ff00aa;">e</span><span style="color:#ff0048;">t</span><span style="color:#fe0c00;">r</span><span style="color:#fd3c00;">e</span><span style="color:#fc6c00;">i</span><span style="color:#fc9d00;">b</span><span style="color:#fdce00;">e</span><span style="color:#ffff00;">rn</span></span></b></i>'

                : 'Funksender von unbekanntem Netzbetreiber')
            popup.setLngLat(coordinates[0][0]).setHTML(popupMessage).addTo(map);
        });

// map.on('mouseleave', 'unitless_towers', () => {
//     map.getCanvas().style.cursor = '';
//     popup.remove();
// });

map.on('mouseenter', 'small-cells-polygons', (e) => {
            // Change the cursor style as a UI indicator.

            map.getCanvas().style.cursor = 'pointer';


            // Get the coordinates and description from the hovered feature.
            const coordinates = e.features[0].geometry.coordinates.slice();
            
            // Ensure that if the map is zoomed out such that multiple
            // copies of the feature are visible, the popup appears
            // over the copy being pointed to.
            while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
                coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
            }

            // Populate the popup and set its coordinates
            // based on the feature found.
            let popupMessage = "Kleinzellen-Funkanlage"
            popup.setLngLat(coordinates[0][0]).setHTML(popupMessage).addTo(map);
        });

// map.on('mouseleave', 'small-cells-polygons', () => {
//     map.getCanvas().style.cursor = '';
//     popup.remove();
// });




// map.on('mousemove', (e) => {
//     const features = map.queryRenderedFeatures(e.point);

//     // Limit the number of properties we're displaying for
//     // legibility and performance
//     const displayProperties = [
//         'type',
//         'properties',
//         'id',
//         'layer',
//         'source',
//         'sourceLayer',
//         'state'
//     ];

//     const displayFeatures = features.map((feat) => {
//         const displayFeat = {};
//         displayProperties.forEach((prop) => {
//             displayFeat[prop] = feat[prop];
//         });
//         return displayFeat;
//     });

//     document.getElementById('features').innerHTML = JSON.stringify(
//         displayFeatures,
//         null,
//         2
//     );
// });

