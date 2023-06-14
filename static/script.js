
function httpGet(theUrl) {
	let xmlHttpReq = new XMLHttpRequest();
	xmlHttpReq.open("GET", theUrl, false);
	xmlHttpReq.send(null);
	return xmlHttpReq.responseText;
}

document.addEventListener("DOMContentLoaded",function(){
		var loc = [47.6045, -122.3347]
		var map = L.map('map').setView(loc, 17); //would change to current location if ported to mobile and expanded
		var busIcons = []
		var busIcon = L.icon({
			iconUrl: '/static/busicon.png',
			iconSize: [64,64]
		})
		// Add OpenStreetMap tile layer
		var Thunderforest_Neighbourhood = L.tileLayer('https://{s}.tile.thunderforest.com/neighbourhood/{z}/{x}/{y}.png?apikey={apikey}', {
			attribution: '&copy; <a href="http://www.thunderforest.com/">Thunderforest</a>, &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
			apikey: '3dbe21d5d69a47e6abee3ee3f364faf4',
			maxZoom: 22
		}).addTo(map)
		var locationMarker = L.circleMarker(loc, {
			radius:15,
	})
	locationMarker.setStyle({color:'green',background_color:'green'})
	locationMarker.bindTooltip('Current Location')
	locationMarker.addTo(map);

	//render nearby

	nearbyBuses = httpGet(`http://localhost/api/vehiclesForLL?lat=${loc[0]}&lon=${loc[1]}&limit=5`)
	nearbyBuses = JSON.parse(nearbyBuses)
	for(i=0;i<nearbyBuses.length;i++){
		//render icons on map
		bus = nearbyBuses[i]
		latestIcon = L.marker([bus.location[0],bus.location[1]],{icon:busIcon})
		latestIcon.bindTooltip(`${bus.headsign} (${bus.route_no}) <img width=16 src='/static/orcacard.png'/>`)
		busIcons.push(latestIcon)
		latestIcon.addTo(map)

		//render nearby list

	}

	document.getElementsByClassName('reportButton')[0].addEventListener('click',function(){
		document.getElementById('myModal').style.display = 'block'
	})
	document.getElementsByClassName('close')[0].addEventListener('click',function(){
		document.getElementById('myModal').style.display = 'none'
	})

	document.getElementById('problem-type').addEventListener('change',function(e){
		selected = document.getElementById('problem-type').value
		console.log(selected)
		if(selected.startsWith('stop')){
			//get nearest stop
			stop = JSON.parse(httpGet(`http://localhost/api/stopsForLL?lat=${loc[0]}&lon=${loc[1]}`))
			document.getElementById('detectLocation').innerText = 'We detect that you are at: '+stop['name']
		}
	})

	document.getElementById('submit').addEventListener('click',function(){
		httpGet(`/api/submitIssue?issueType=${document.getElementById('problem-type').value}&stopId=${stop['id']}&lat=${stop.location[0]}&lon=${stop.location[1]}`)
		/*    issueType = flask.request.args['issue']
    stopId = flask.request.args['stopId']
    lat = float(flask.request.args['lat'])
    lon = float(flask.request.args['lon'])*/
	})


})



