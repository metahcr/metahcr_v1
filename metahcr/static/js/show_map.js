/**
 * Created by pcmarks on 7/15/2017.
 */
var MAP_WIDTH = 500;
var MAP_HEIGHT = 500;
/**
 * Construct and show a google map for a location. Map is show in a modeless dialog.
 * @param latitude
 * @param longitude
 */
browse_show_map = function(latitude, longitude) {
    var gmap, locMarker, options;
    var map_window = $('#location-map-window');
    map_window.window({width: MAP_WIDTH, height: MAP_HEIGHT, modal: false});
    $('#location-map').empty();
    // google maps does not accept jquery selectors, e.g., $('#location-map')
    var map_div = document.getElementById('location-map');
    options = {
        center: new google.maps.LatLng(latitude, longitude),
        scaleControl: true,
        zoom: 7,
        mapTypeId: google.maps.MapTypeId.HYBRID,
        navigationControl: true,
        disableDoubleClickZoom: true,
        navigationControlOptions: {
            style: google.maps.NavigationControlStyle.ZOOM_PAN
        }
    };
    gmap = new google.maps.Map(map_div, options);
    locMarker = new google.maps.Marker({
        position: new google.maps.LatLng(latitude, longitude),
        map: gmap
    })
};
