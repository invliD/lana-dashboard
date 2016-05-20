from django.http import Http404


def get_object_with_subclasses_or_404(klass, *args, **kwargs):
	objs = klass.objects.filter(*args, **kwargs).select_subclasses()
	num = len(objs)
	if num == 1:
		return objs.first()
	if not num:
		raise Http404('No %s matches the given query.' % klass._meta.object_name)
	raise klass.MultipleObjectsReturned(
		"get() returned more than one %s -- it returned %s!" %
		(klass._meta.object_name, num)
	)


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
				'marker-symbol': 'circle',
				'color': autonomous_system.institution.color,
			}
		})
	return obj


def geojson_from_tunnels(tunnels):
	obj = {
		'type': 'FeatureCollection',
		'features': []
	}
	for tunnel in tunnels:
		as1 = tunnel.endpoint1.autonomous_system
		as2 = tunnel.endpoint2.autonomous_system

		if as1.location_lat is None or as1.location_lng is None or as2.location_lat is None or as2.location_lng is None:
			continue

		obj['features'].append({
			'type': 'Feature',
			'geometry': {
				'type': 'LineString',
				'coordinates': [
					[as1.location_lng, as1.location_lat],
					[as2.location_lng, as2.location_lat]
				]
			}
		})
	return obj
