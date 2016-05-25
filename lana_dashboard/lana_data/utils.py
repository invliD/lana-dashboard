from django.core.exceptions import PermissionDenied
from django.http import Http404


def get_object_for_view_or_404(klass, request, *args, with_subclasses=False, **kwargs):
	objs = klass.get_view_qs(request.user).filter(*args, **kwargs)
	if with_subclasses:
		objs = objs.select_subclasses()
	num = len(objs)
	if num == 1:
		return objs.first()
	if not num:
		raise Http404('No %s matches the given query.' % klass._meta.object_name)
	raise klass.MultipleObjectsReturned(
		"get() returned more than one %s -- it returned %s!" %
		(klass._meta.object_name, num)
	)


def get_object_for_edit_or_40x(klass, request, *args, with_subclasses=False, **kwargs):
	obj = get_object_for_view_or_404(klass, request, with_subclasses=with_subclasses, *args, **kwargs)
	if not obj.can_edit(request.user):
		raise PermissionDenied
	return obj


def list_objects_for_view(klass, request, *args, with_subclasses=False, **kwargs):
	qs = klass.get_view_qs(request.user).filter(*args, **kwargs)
	if with_subclasses:
		qs = qs.select_subclasses()
	return qs


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
