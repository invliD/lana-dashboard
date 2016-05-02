LANA = {};

LANA.createMap = function(center_lat, center_lng, zoom) {
	var map = new mapboxgl.Map({
		container: 'map',
		style: 'mapbox://styles/mapbox/streets-v8',
		center: [center_lng, center_lat],
		zoom: zoom
	});
	map.dragRotate.disable();
	map.touchZoomRotate.disableRotation();
	return map;
};

LANA.loadGeoJSONPoints = function(map, url, completion) {
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

				if (completion) {
					completion();
				}
			}
		});
	});
};

LANA.loadGeoJSONLines = function(map, url) {
	map.on('load', function() {
		$.ajax({
			url: url,
			headers: {
				'Accept': 'application/vnd.geo+json'
			},
			success: function(data) {
				map.addSource('tunnels', {
					'type': 'geojson',
					'data': data
				});

				map.addLayer({
					'id': 'tunnels',
					'type': 'line',
					'source': 'tunnels',
					'layout': {
						'line-join': 'round',
						'line-cap': 'round'
					},
					'paint': {
						'line-color': '#888',
						'line-width': 2
					}
				}, 'markers');
			}
		})
	});
};

LANA.fitBoundsToSource = function(map, source_id) {
	var geo = map.getSource(source_id)._data;
	if (geo.features.length > 0) {
		var bounds = new mapboxgl.LngLatBounds();
		geo.features.forEach(function (feature) {
			bounds.extend(feature.geometry.coordinates);
		});
		if (bounds.getNorth() == bounds.getSouth() && bounds.getWest() == bounds.getEast()) {
			map.flyTo({
				center: bounds.getCenter().toArray(),
				zoom: 9
			});
		} else {
			map.fitBounds(bounds, {
				padding: 40
			});
		}
	}
};
