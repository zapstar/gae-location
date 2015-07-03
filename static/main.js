//This is the only JS file that is written by the user *-min.js are production suite JS files related
//to jQuery and Geographical Location Retrieval functions


//Callback function for successfully getting Latitude/Longitude of a client
function success_callback(p) {	
	//p has the latitude and longitude
	
	//position in Google Maps format
	var position = new google.maps.LatLng(p.coords.latitude,p.coords.longitude);
	
	//Google Maps Geocoder
	geocoder = new google.maps.Geocoder();
	
	//Tell the geoCoder to get the address from Latitude, Longitude
	geocoder.geocode({'latLng': position}, function(results,status){
		//Postal address variable
		var paddress;
		
		//self explanatory checks
		if (status == google.maps.GeocoderStatus.OK) {
			if(results[1]) {
				//all checks passed
				//put the formatted address into the paddress variable
				paddress = results[1].formatted_address
				
				//display the address, lat and long
				$("p#geoloc").replaceWith('<p id="geoloc"><b>Address:</b> ' + paddress + '<br><br><b>Latitude:</b> ' + p.coords.latitude + '<br><b>Longitude:</b> ' + p.coords.longitude + '</p>');
			} else {
				//if address not available, just show lat and long
				$("p#geoloc").replaceWith('<p id="geoloc"><b>Error Occured while getting the address.</b><br><br><b>Latitude:</b> ' + p.coords.latitude + '<br><br><b>Longitude:</b> ' + p.coords.longitude + '</p>');
			}
			
			//whatever the case, we have lat/long we post it into the datastore using
			//AJAX's POST method
			$.ajax({
				type: 'POST',
				url: '../store',
				data: 'address=' + paddress + '&lat=' + p.coords.latitude + '&long=' + p.coords.longitude,
				success: function(){
					//if POST is successful, then we append 'data sent' statement in the div
					$("p#geoloc").append('<center><p><br>Your Geo-Location Data Sent to the Server<br></p><center>');
				}
			});
		}
	});
}

//Error Callback after the geo-location position has been asked for and been rejected
function error_callback(p) {
	$("p#geoloc").replaceWith('<p id="geoloc"></b>Error: ' + p.code + '.</b> You have declined Geo-location identification, we value your privacy.</p>');
}

//when the document is ready, then execute
$(document).ready(function() {
	//see if the geo-position is available, if so call success_callback else the other one
	//high accuracy is enabled so that mobile devices give out more accurate gps locations
	if (geo_position_js.init()) {
		geo_position_js.getCurrentPosition(success_callback, error_callback, { enableHighAccuracy : true });
	} else {
		//if the above initalization fails, then the browser can't give you location data
		$("p#geoloc").replaceWith('<p id="geoloc">Geo location functionality not available</p>');
	}
});