// ++++++++++++++++++++++++
// sample implementation:
// - points that take advantage of clustering but do not "spider" out like typical clusters
// - custom icons through CSS
// -combining the pop up content from all points within a cluster, when applicable
// Source data in JSON format with lat/longs used for placement and other attributes
// used for pop up text
// Mollie Webb
// molliewebb@wustl.edu
// June 2021

// sources of code snippets and inspiration:
// Clustering Markers on Leaflet Maps
// See post: http://asmaloney.com/2015/06/code/clustering-markers-on-leaflet-maps
// https://github.com/asmaloney/Leaflet_Cluster_Example

// Working with Clusters in Leaflet: Increasing Useability
// https://digital-geography.com/working-with-clusters-in-leaflet-increasing-useability/
// ++++++++++++++++++++++++

// Creates the map object, center, zoom level
var map = L.map('map', {
  center: [48.864716, 2.349014],
  minZoom: 2,
  zoom: 12,
})
// Creates basemap
L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/toner-background/{z}/{x}/{y}{r}.png', {
	attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  subdomains: ['a', 'b', 'c'],
}).addTo(map)

// Creating the clusters and settings, turn off "spidering", etc
// Also added custom icon creation function
var markerClusters = new L.MarkerClusterGroup({
    spiderfyOnMaxZoom: false,
    showCoverageOnHover: false,
    zoomToBoundsOnClick: true,
    singleMarkerMode: true,
    maxClusterRadius: 10,
    iconCreateFunction: function (cluster) {
        return L.divIcon({ html: "", className: 'mycluster'});
      },
});

// Loop through all of the points from the "markers" variable
// which is a JSON list of all of the info from the shapefile
for (var i = 0; i < markers.length; ++i) {
  // Creates a string that is HTML, each point has one
  var popup =
    "<b>Name: " + markers[i]['properties']['Name'] + '</b><br><br>' +
    markers[i]['properties']['snippet'] + '<br><b>- ' +
    markers[i]['properties']['docAuthor'] + ', ' +
    markers[i]['properties']['docTitle'] + ', ' +
    markers[i]['properties']['docDate'] + ', p.' +
    markers[i]['properties']['doc_page_n'] + '</b><br><br>'

  // Gets the lat/long from the JSON and drops the symbol and popup there
  var m = L.marker([markers[i]['properties']['Latitude'],
                   markers[i]['properties']['Longitude']]).bindPopup(popup)

  // Associates the clusters with the layer
  markerClusters.addLayer(m)
} // End loop through each feature in the JSON

// Sets the action that happens when a cluster is clicked
markerClusters.on('clusterclick', function(a){
    // Starts a new string that will hold the HTML for all of the points
    // in the cluster
    popUpText = ""
    // Loops through all of the points and gets the HTML string
    // adds it to the pop up string
    for (feat in a.layer.getAllChildMarkers()){
      popUpText += a.layer.getAllChildMarkers()[feat]._popup._content
    }
    // Gets the first instance of the place name
    var name_first = new RegExp ("^(<b>Name:)(.+?)(<\/b><br><br>)")
    // Gets all of the other instances of the place name
    var name_other = new RegExp("(<b>Name:)(.+?)(<\/b><br><br>)", 'g')
    // Holds the first instance of place name as a variable
    var name_first_match = popUpText.match(name_first)[0]

    // These next lines remove the non-first instances of the place name
    popUpText = popUpText.replace(name_first,"REPLACED")
    popUpText = popUpText.replace(name_other,"")
    popUpText = popUpText.replace("REPLACED",name_first_match)

    // Adds this new string as the pop up for the cluster
    var popup = L.popup({maxHeight:100}).setLatLng([a.layer._cLatLng.lat, a.layer._cLatLng.lng]).setContent(popUpText).openOn(map);
    })

// Adds the clusters as a layer in the map
map.addLayer(markerClusters)
