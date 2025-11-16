import { getPixelValue } from './additional-features/getPixelValue.js'
import { signalIconPath } from './additional-features/signalPercentBar.js'

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

const cachedTowers = new Map();
let apiTowerDetails = 0

map.on('mouseenter', 'cells-layer', async (e) => {
            

            // Call API for advanced tower tooltip infos
            let hoveredTowerFid = e.features[0].properties.tower_fid
            if (!cachedTowers.has(hoveredTowerFid)) {
                let apiTowerDetailsResponse = await fetch("https://api.netzkarte.app/towers/" + hoveredTowerFid)
                apiTowerDetails = await apiTowerDetailsResponse.json()
                cachedTowers.set(hoveredTowerFid, apiTowerDetails);
            } else {
                apiTowerDetails = cachedTowers.get(hoveredTowerFid)
            }

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
            
            // 1und1 Zusatztext
            
            let Text1und1 = ""
            if(apiTowerDetails.provider_1und1){
                Text1und1 = '<span class="einsundeins-notice"> ✓ auch <span class="einsundeins_span">1&1</span> (5G) </span><br>'
            }
            

            let popupMessage = "<b>" + e.features.length + 
                ( e.features[0].properties.provider === 't'   ? '</b> Mobilfunksender der <span class="telekom_span">Telekom</span>'
                : e.features[0].properties.provider === 'v'   ? '</b> Mobilfunksender der <span class="vodafone_span">Vodafone</span>'
                : e.features[0].properties.provider === 'b'   ? '</b> Mobilfunksender der <span class="telefonica_span">Telefonica/o2</span>'
                : e.features[0].properties.provider === 'tv'  ? '</b> Mobilfunksender der <span class="telekom_span">Telekom</span> und <span class="vodafone_span">Vodafone</span>'
                : e.features[0].properties.provider === 'tb'  ? '</b> Mobilfunksender der <span class="telekom_span">Telekom</span> und <span class="telefonica_span">o2</span>'
                : e.features[0].properties.provider === 'vb'  ? '</b> Mobilfunksender der <span class="vodafone_span">Vodafone</span> und <span class="telefonica_span">o2</span>'
                : e.features[0].properties.provider === 'tvb' ? '</b> Mobilfunksender <b><i>aller drei <span class="rainbow"><span style="color:#00fc00;">M</span><span style="color:#00fd61;">o</span><span style="color:#00fec2;">b</span><span style="color:#00efef;">i</span><span style="color:#00c6c6;">l</span><span style="color:#009d9d;">f</span><span style="color:#0069b1;">u</span><span style="color:#0031d9;">n</span><span style="color:#0700f7;">k</span><span style="color:#4200d2;">n</span><span style="color:#7e00ae;">e</span><span style="color:#ae00ae;">t</span><span style="color:#d400d4;">z</span><span style="color:#fa00fa;">b</span><span style="color:#ff00aa;">e</span><span style="color:#ff0048;">t</span><span style="color:#fe0c00;">r</span><span style="color:#fd3c00;">e</span><span style="color:#fc6c00;">i</span><span style="color:#fc9d00;">b</span><span style="color:#fdce00;">e</span><span style="color:#ffff00;">r</span></span></b></i>'
                : '</b> Mobilfunksender eines unbekannten Netzbetreibers') + " in diese Richtung. <br>"
                + "<span class=\"tooltip-summary\">Sendeeinheiten insgesamt: <b>" + apiTowerDetails.units.length + "</b></span><br>"
                + Text1und1 
                + "<div class=\"tooltip-footer\"> Datum: " + apiTowerDetails.creation_date + ' · <a href="https://www.bundesnetzagentur.de/emf-karte/hf.aspx?fid=' + apiTowerDetails.fid + '" target="_blank" rel="noopener noreferrer"> fID: ' + apiTowerDetails.fid + "<br>"
                + "</div>"
            popup.setLngLat(coordinates[0][0]).setHTML(popupMessage).addTo(map);
        });


map.on('mouseenter', 'unitless-towers', async (e) => {

    let hoveredTowerFid = e.features[0].properties.tower_fid
    let apiTowerDetails = 0

    if (!cachedTowers.has(hoveredTowerFid)) {
        let apiTowerDetailsResponse = await fetch("https://api.netzkarte.app/towers/" + hoveredTowerFid)
        apiTowerDetails = await apiTowerDetailsResponse.json()
        cachedTowers.set(hoveredTowerFid, apiTowerDetails);
    } else {
        apiTowerDetails = cachedTowers.get(hoveredTowerFid)
    }

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


    // 1und1 Zusatztext
    let Text1und1 = ""
    if(apiTowerDetails.provider_1und1){
        Text1und1 = '<span class="einsundeins-notice"> ✓ auch <span class="einsundeins_span">1&1</span> (5G) </span><br>'
    }


    let popupMessage = "Unbekannter " +
        ( e.features[0].properties.provider === 't' ? 'Mobilfunksender der <span class="telekom_span">Telekom</span>' 
        : e.features[0].properties.provider === 'v' ? 'Mobilfunksender der <span class="vodafone_span">Vodafone</span>'
        : e.features[0].properties.provider === 'b' ? 'Mobilfunksender der <span class="telefonica_span">Telefonica/o2</span>'

        : e.features[0].properties.provider === 'tv' ? 'Mobilfunksender der <span class="telekom_span">Telekom</span> und <span class="vodafone_span">Vodafone</span>'
        : e.features[0].properties.provider === 'tb' ? 'Mobilfunksender der <span class="telekom_span">Telekom</span> und <span class="telefonica_span">o2</span>'
        : e.features[0].properties.provider === 'vb' ? 'Mobilfunksender der <span class="vodafone_span">Vodafone</span> und <span class="telefonica_span">o2</span>'

        : e.features[0].properties.provider === 'tvb' ? 'Mobilfunksender von <b><i>allen drei <span class="colorize_fun"><span style="color:#00fc00;">M</span><span style="color:#00fd61;">o</span><span style="color:#00fec2;">b</span><span style="color:#00efef;">i</span><span style="color:#00c6c6;">l</span><span style="color:#009d9d;">f</span><span style="color:#0069b1;">u</span><span style="color:#0031d9;">n</span><span style="color:#0700f7;">k</span><span style="color:#4200d2;">n</span><span style="color:#7e00ae;">e</span><span style="color:#ae00ae;">t</span><span style="color:#d400d4;">z</span><span style="color:#fa00fa;">b</span><span style="color:#ff00aa;">e</span><span style="color:#ff0048;">t</span><span style="color:#fe0c00;">r</span><span style="color:#fd3c00;">e</span><span style="color:#fc6c00;">i</span><span style="color:#fc9d00;">b</span><span style="color:#fdce00;">e</span><span style="color:#ffff00;">rn</span></span></b></i>'

        : 'Funksender von unbekanntem Netzbetreiber')
        + "<br>"
        + Text1und1 
        + "<div class=\"tooltip-footer\"> Datum: " + apiTowerDetails.creation_date + ' · <a href="https://www.bundesnetzagentur.de/emf-karte/hf.aspx?fid=' + apiTowerDetails.fid + '" target="_blank" rel="noopener noreferrer"> fID: ' + apiTowerDetails.fid + "<br>"
        + "</div>"
    popup.setLngLat(coordinates[0][0]).setHTML(popupMessage).addTo(map);
});


map.on('mouseenter', 'small-cells-polygons', (e) => {
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
    let popupMessage = '<a href="https://de.wikipedia.org/wiki/Small_Cell" target="_blank">Kleinzellen-Funkanlage</a>'
    popup.setLngLat(coordinates[0][0]).setHTML(popupMessage).addTo(map);
});


map.on('mouseleave', 'cells-layer', () => {
    map.getCanvas().style.cursor = '';
});
map.on('mouseleave', 'unitless-towers', () => {
    map.getCanvas().style.cursor = '';
});
map.on('mouseleave', 'small-cells-polygons', () => {
    map.getCanvas().style.cursor = '';
});


let pixelData = 0
const bubble = document.getElementById("receptionBubble");
map.on('mousemove', async (e) => {
    const lon = e.lngLat.lng;
    const lat = e.lngLat.lat;
    const zoom = 13; // fixed zoom level

    // --- Compute tile indices ---
    const scale = 1 << zoom;
    const xTile = Math.floor((lon + 180) / 360 * scale);
    const yTile = Math.floor((1 - Math.log(Math.tan(lat * Math.PI/180) + 1/Math.cos(lat * Math.PI/180)) / Math.PI) / 2 * scale);
    

    // --- Compute pixel offset inside tile (0–255) ---
    const worldX = (lon + 180) / 360 * scale * 256;
    const worldY = (1 - Math.log(Math.tan(lat * Math.PI/180) + 1/Math.cos(lat * Math.PI/180)) / Math.PI) / 2 * scale * 256;
    const pixelX = Math.floor(worldX % 256);
    const pixelY = Math.floor(worldY % 256);

    // --- Build tile URL ---
    const url = `https://tiles.netzkarte.app/${zoom}/${xTile}/${yTile}.png`;

//   console.clear();
//   console.log("Mousemove event:");
//   console.log("WGS84:", e.lngLat);
//   console.log("Tile indices:", {x: xTile, y: yTile, z: zoom});
//   console.log("Pixel in tile:", {px: pixelX, py: pixelY});
//   console.log("Tile URL:", url);

    pixelData = await getPixelValue(url, pixelX, pixelY)
    console.log(pixelData)

    bubble.innerHTML = `
        <img src="${signalIconPath(pixelData.r)}" class="signalIcon" /> <span class="light_vodafone_span">Vodafone.de: ${Math.round(pixelData.r/2.55)}% </span> <br>
        <img src="${signalIconPath(pixelData.g)}" class="signalIcon" /> <span class="light_telekom_span">Telekom.de: ${Math.round(pixelData.g/2.55)}% </span> <br>
        <img src="${signalIconPath(pixelData.b)}" class="signalIcon" /> <span class="light_telefonica_span">o2-de: ${Math.round(pixelData.b/2.55)}% </span> <br>
        ⓘ Diese Infos sind vermutlich noch falsch. 
    `;

    bubble.style.display = "block";
    bubble.style.left = e.originalEvent.pageX + "px";
    bubble.style.top = e.originalEvent.pageY + "px";


    // // Example usage
    // getPixelValue("https://tiles.netzkarte.app/13/4354/2764.png", 120, 80).then(color => {
    //   console.log(`Pixel at (120,80): R=${color.r}, G=${color.g}, B=${color.b}, A=${color.a}`);
    // }).catch(err => {
    //   console.error("Error loading image:", err);
    // });

});






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

