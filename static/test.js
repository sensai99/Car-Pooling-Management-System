    
var AUTOCOMPLETION_URL = 'https://autocomplete.geocoder.ls.hereapi.com/6.2/suggest.json',
ajaxRequest = new XMLHttpRequest(),
query = '';

/**
* If the text in the text box  has changed, and is not empty,
* send a geocoding auto-completion request to the server.
*
* @param {Object} textBox the textBox DOM object linked to this event
* @param {Object} event the DOM event which fired this listener
*/
function autoCompleteListener(textBox, event) {

if (query != textBox.value){
    if (textBox.value.length >= 1){

        /**
         * A full list of available request parameters can be found in the Geocoder Autocompletion
         * API documentation.
         *
         */
        var params = '?' +
            'query=' +  encodeURIComponent(textBox.value) +   // The search text which is the basis of the query
            '&beginHighlight=' + encodeURIComponent('<mark>') + //  Mark the beginning of the match in a token.
            '&endHighlight=' + encodeURIComponent('</mark>') + //  Mark the end of the match in a token.
            '&maxresults=5' +  // The upper limit the for number of suggestions to be included
            // in the response.  Default is set to 5.
            '&apikey=' + APIKEY;
        ajaxRequest.open('GET', AUTOCOMPLETION_URL + params );
        ajaxRequest.send();
    }
}
query = textBox.value;
}


/**
*  This is the event listener which processes the XMLHttpRequest response returned from the server.
*/
function onAutoCompleteSuccess() {
/*
 * The styling of the suggestions response on the map is entirely under the developer's control.
 * A representitive styling can be found the full JS + HTML code of this example
 * in the functions below:
 */
clearOldSuggestions();
addSuggestionsToPanel(this.response);  // In this context, 'this' means the XMLHttpRequest itself.
addSuggestionsToMap(this.response);
}


/**
* This function will be called if a communication error occurs during the XMLHttpRequest
*/
function onAutoCompleteFailed() {
alert('Ooops!');
}

// Attach the event listeners to the XMLHttpRequest object
ajaxRequest.addEventListener("load", onAutoCompleteSuccess);
ajaxRequest.addEventListener("error", onAutoCompleteFailed);
ajaxRequest.responseType = "json";


/**
* Boilerplate map initialization code starts below:
*/


// set up containers for the map  + panel
var mapContainer = document.getElementById('map'),
suggestionsContainer = document.getElementById('panel');

//Step 1: initialize communication with the platform
var APIKEY = '3Z7958BKQnwVgrS2RvT_8ujlglfJ_YMQbAJC7RHC0DM';

var platform = new H.service.Platform({
apikey: APIKEY,
useCIT: false,
useHTTPS: true
});
var defaultLayers = platform.createDefaultLayers();
var geocoder = platform.getGeocodingService();
var group = new H.map.Group();

group.addEventListener('tap', function (evt) {
map.setCenter(evt.target.getGeometry());
openBubble(
    evt.target.getGeometry(), evt.target.getData());
}, false);


//Step 2: initialize a map - this map is centered over Europe
var map = new H.Map(mapContainer,
defaultLayers.vector.normal.map,{
    center: {lat:52.5160, lng:13.3779},
    zoom: 3
});

map.addObject(group);

//Step 3: make the map interactive
// MapEvents enables the event system
// Behavior implements default interactions for pan/zoom (also on mobile touch environments)
var behavior = new H.mapevents.Behavior(new H.mapevents.MapEvents(map));

// Create the default UI components
var ui = H.ui.UI.createDefault(map, defaultLayers);

// Hold a reference to any infobubble opened
var bubble;

/**
* Function to Open/Close an infobubble on the map.
* @param  {H.geo.Point} position     The location on the map.
* @param  {String} text              The contents of the infobubble.
*/
function openBubble(position, text){
if(!bubble){
    bubble =  new H.ui.InfoBubble(
        position,
        // The FO property holds the province name.
        {content: '<small>' + text+ '</small>'});
    ui.addBubble(bubble);
} else {
    bubble.setPosition(position);
    bubble.setContent('<small>' + text+ '</small>');
    bubble.open();
}
}


/**
* The Geocoder Autocomplete API response retrieves a complete addresses and a `locationId`.
* for each suggestion.
*
* You can subsequently use the Geocoder API to geocode the address based on the ID and
* thus obtain the geographic coordinates of the address.
*
* For demonstration purposes only, this function makes a geocoding request
* for every `locationId` found in the array of suggestions and displays it on the map.
*
* A more typical use-case would only make a single geocoding request - for example
* when the user has selected a single suggestion from a list.
*
* @param {Object} response
*/
function addSuggestionsToMap(response){
/**
 * This function will be called once the Geocoder REST API provides a response
 * @param  {Object} result          A JSONP object representing the  location(s) found.
 */
var onGeocodeSuccess = function (result) {
        var marker,
            locations = result.Response.View[0].Result,
            i;

        // Add a marker for each location found
        for (i = 0; i < locations.length; i++) {
            marker = new H.map.Marker({
                lat : locations[i].Location.DisplayPosition.Latitude,
                lng : locations[i].Location.DisplayPosition.Longitude
            });
            marker.setData(locations[i].Location.Address.Label);
            group.addObject(marker);
        }

        map.getViewModel().setLookAtData({
            bounds: group.getBoundingBox()
        });
        if(group.getObjects().length < 2){
            map.setZoom(15);
        }
    },
    /**
     * This function will be called if a communication error occurs during the JSON-P request
     * @param  {Object} error  The error message received.
     */
    onGeocodeError = function (error) {
        alert('Ooopseee!');
    },
    /**
     * This function uses the geocoder service to calculate and display information
     * about a location based on its unique `locationId`.
     *
     * A full list of available request parameters can be found in the Geocoder API documentation.
     * see: http://developer.here.com/rest-apis/documentation/geocoder/topics/resource-search.html
     *
     * @param {string} locationId    The id assigned to a given location
     */
    geocodeByLocationId = function (locationId) {
        geocodingParameters = {
            locationId : locationId
        };

        geocoder.geocode(
            geocodingParameters,
            onGeocodeSuccess,
            onGeocodeError
        );
    }

/*
 * Loop through all the geocoding suggestions and make a request to the geocoder service
 * to find out more information about them.
 */

response.suggestions.forEach(function (item, index, array) {
    geocodeByLocationId(item.locationId);
});
}


/**
* Removes all H.map.Marker points from the map and adds closes the info bubble
*/
function clearOldSuggestions(){
group.removeAll ();
if(bubble){
    bubble.close();
}
}

/**
* Format the geocoding autocompletion repsonse object's data for display
*
* @param {Object} response
*/
function addSuggestionsToPanel(response){
var suggestions = document.getElementById('suggestions');
suggestions.innerHTML = JSON.stringify(response, null, ' ');
}



var content =  '<strong style="font-size: large;">' + 'Geocoding Autocomplete'  + '</strong></br>';

content  += '<br/><input type="text" id="auto-complete" style="margin-left:5%; margin-right:5%; min-width:90%"  onkeyup="return autoCompleteListener(this, event);"><br/>';
content  += '<br/><strong>Response:</strong><br/>';
content  += '<div style="margin-left:5%; margin-right:5%;"><pre style="max-height:235px"><code  id="suggestions" style="font-size: small;">' +'{}' + '</code></pre></div>';

suggestionsContainer.innerHTML = content;