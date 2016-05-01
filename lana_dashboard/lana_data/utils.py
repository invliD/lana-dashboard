def geojson_from_autonomous_systems(autonomous_systems):
	obj = {
		'type': 'FeatureCollection',
		'features': [],
	}
	for autonomous_system in autonomous_systems:
		if autonomous_system.location_lat is None or autonomous_system.location_lng is None:
			continue

		obj['features'].append({
			'type': 'Feature',
			'geometry': {
				'type': 'Point',
				'coordinates': [autonomous_system.location_lng, autonomous_system.location_lat],
			},
			'properties': {
				'title': str(autonomous_system),
				'marker-symbol': 'marker',
			}
		})
	return obj
