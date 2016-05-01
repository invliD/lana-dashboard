LANA = {};

LANA.createMap = function(center_lat, center_lng) {
	var map = new mapboxgl.Map({
		container: 'map',
		style: 'mapbox://styles/mapbox/streets-v8',
		center: [center_lng, center_lat],
		zoom: 9
	});
	return map;
};

LANA.loadGeoJSON = function(map, url) {
	map.on('load', function () {
		$.ajax({
			url: url,
			headers: {
				'Accept': 'application/vnd.geo+json'
			},
			success: function(data) {
				map.addSource('markers', {
					'type': 'geojson',
					'data': data
				});

				map.addLayer({
					'id': 'markers',
					'type': 'symbol',
					'source': 'markers',
					'layout': {
						'icon-image': '{marker-symbol}-15',
						'text-field': '{title}',
						'text-font': ['Open Sans Semibold', 'Arial Unicode MS Bold'],
						'text-offset': [0, 0.6],
						'text-anchor': 'top'
					}
				});
			}
		});
	});
};
