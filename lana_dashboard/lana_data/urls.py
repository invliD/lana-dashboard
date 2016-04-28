from django.conf.urls import url
from lana_dashboard.lana_data import views

urlpatterns = [
	url(r'^institutions/$', views.list_institutions, name='institutions'),
	url(r'^institutions/create$', views.edit_institution, name='institution-create'),
	url(r'^institutions/(?P<code>.+)/$', views.show_institution, name='institution-details'),
	url(r'^institutions/(?P<code>.+)/edit$', views.edit_institution, name='institution-edit'),
	url(r'^autonomous-systems/$', views.list_autonomous_systems, name='autonomous_systems'),
	url(r'^autonomous-systems/create$', views.edit_autonomous_system, name='autonomous_system-create'),
	url(r'^autonomous-systems/(?P<as_number>.+)/$', views.show_autonomous_system, name='autonomous_system-details'),
	url(r'^autonomous-systems/(?P<as_number>.+)/edit$', views.edit_autonomous_system, name='autonomous_system-edit'),
	url(r'^ipv4/$', views.list_ipv4, name='ipv4'),
	url(r'^ipv4/create$', views.edit_ipv4, name='ipv4-create'),
	url(r'^ipv4/(?P<network_address>.+)/(?P<subnet_bits>\d+)/edit$', views.edit_ipv4, name='ipv4-edit'),
]
