Array.prototype.unique = function() {
	var n = {}, r=[];
	for(var i = 0; i < this.length; i++) {
		if (!n[this[i]]) {
			n[this[i]] = true;
			r.push(this[i]);
		}
	}
	return r;
};

LANA = {};

LANA.createMap = function(center_lat, center_lng, zoom) {
	var map = new mapboxgl.Map({
		container: 'map',
		style: 'mapbox://styles/mapbox/streets-v9',
		center: [center_lng, center_lat],
		zoom: zoom
	});
	map.dragRotate.disable();
	map.touchZoomRotate.disableRotation();

	// Create fake top layer
	map.on('load', function() {
		map.addSource('top', {
			'type': 'geojson',
			'data': {
				'type': 'FeatureCollection',
				'features': []
			}
		});
		map.addLayer({
			'id': 'top',
			'type': 'fill',
			'source': 'top'
		});
	});
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

				colors = data.features.map(function(x) {
					return x.properties.color;
				}).unique().forEach(function (color) {
					map.addLayer({
						'id': 'markers-circle-' + color,
						'type': 'circle',
						'source': 'markers',
						'filter': ["==", "color", color],
						'paint': {
							'circle-radius': 7,
							'circle-color': color,
						}
					});
				});

				map.addLayer({
					'id': 'markers-text',
					'type': 'symbol',
					'source': 'markers',
					'layout': {
						'text-field': '{title}',
						'text-font': ['Open Sans Semibold', 'Arial Unicode MS Bold'],
						'text-offset': [0, 0.6],
						'text-anchor': 'top'
					},
					'paint': {
						'text-halo-color': 'white',
						'text-halo-width': 1
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
						'line-color': '#606060',
						'line-width': 2
					}
				}, 'top');
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
