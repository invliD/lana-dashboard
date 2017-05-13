from django.conf.urls import url

from lana_dashboard.lana_data import views


urlpatterns = [
	url(r'^institutions/$', views.list_institutions, name='institutions'),
	url(r'^institutions/create$', views.edit_institution, name='institution-create'),
	url(r'^institutions/(?P<code>.+)/autonomous_systems/$', views.list_institution_autonomous_systems, name='institution-autonomous_systems'),
	url(r'^institutions/(?P<code>.+)/tunnels/$', views.list_institution_tunnels, name='institution-tunnels'),
	url(r'^institutions/(?P<code>.+)/$', views.show_institution, name='institution-details'),
	url(r'^institutions/(?P<code>.+)/delete$', views.delete_institution, name='institution-delete'),
	url(r'^institutions/(?P<code>.+)/edit$', views.edit_institution, name='institution-edit'),

	url(r'^autonomous-systems/$', views.list_autonomous_systems, name='autonomous_systems'),
	url(r'^autonomous-systems/create$', views.edit_autonomous_system, name='autonomous_system-create'),
	url(r'^autonomous-systems/AS(?P<as_number>\d+)/$', views.show_autonomous_system, name='autonomous_system-details'),
	url(r'^autonomous-systems/AS(?P<as_number>\d+)/delete$', views.delete_autonomous_system, name='autonomous_system-delete'),
	url(r'^autonomous-systems/AS(?P<as_number>\d+)/edit$', views.edit_autonomous_system, name='autonomous_system-edit'),
	url(r'^autonomous-systems/AS(?P<as_number>\d+)/hosts/create$', views.edit_host, name='host-create'),

	url(r'^hosts/(?P<fqdn>.+)/$', views.show_host, name='host-details'),
	url(r'^hosts/(?P<fqdn>.+)/delete$', views.delete_host, name='host-delete'),
	url(r'^hosts/(?P<fqdn>.+)/edit$', views.edit_host, name='host-edit'),

	url(r'^ipv4/$', views.list_ipv4, name='ipv4'),
	url(r'^ipv4/create$', views.edit_ipv4, name='ipv4-create'),
	url(r'^ipv4/(?P<network>.+)/$', views.show_ipv4, name='ipv4-details'),
	url(r'^ipv4/(?P<network>.+)/delete$', views.delete_ipv4, name='ipv4-delete'),
	url(r'^ipv4/(?P<network>.+)/edit$', views.edit_ipv4, name='ipv4-edit'),

	url(r'^peerings/create$', views.edit_peering, name='peering-create'),
	url(r'^peerings/AS(?P<as_number1>\d+)-AS(?P<as_number2>\d+)/$', views.show_peering, name='peering-details'),
	url(r'^peerings/AS(?P<as_number1>\d+)-AS(?P<as_number2>\d+)/delete$', views.delete_peering, name='peering-delete'),
	url(r'^peerings/AS(?P<as_number1>\d+)-AS(?P<as_number2>\d+)/edit$', views.edit_peering, name='peering-edit'),

	url(r'^tunnels/$', views.list_tunnels, name='tunnels'),
	url(r'^tunnels/create$', views.edit_tunnel, name='tunnel-create'),
	url(r'^tunnels/create/form$', views.generate_tunnel_form, name='tunnel-create-form'),
	url(r'^tunnels/AS(?P<as_number1>\d+)-AS(?P<as_number2>\d+)/$', views.show_tunnel, name='tunnel-details'),
	url(r'^tunnels/AS(?P<as_number1>\d+)-AS(?P<as_number2>\d+)/delete$', views.delete_tunnel, name='tunnel-delete'),
	url(r'^tunnels/AS(?P<as_number1>\d+)-AS(?P<as_number2>\d+)/edit$', views.edit_tunnel, name='tunnel-edit'),
	url(r'^tunnels/AS(?P<as_number1>\d+)-AS(?P<as_number2>\d+)/autonomous_systems/$', views.list_tunnel_autonomous_systems, name='tunnel-autonomous_systems'),

	url(r'^search/(.+)?$', views.search, name='search'),
]
