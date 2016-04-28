from django.conf.urls import url
from lana_dashboard.lana_data import views

urlpatterns = [
	url(r'^institutions/$', views.list_institutions, name='institutions'),
	url(r'^institutions/create$', views.edit_institution, name='institution-create'),
	url(r'^institutions/(?P<code>.+)/$', views.show_institution, name='institution-details'),
	url(r'^institutions/(?P<code>.+)/edit$', views.edit_institution, name='institution-edit'),
	url(r'^autonomous-systems/$', views.list_autonomous_systems, name='autonomous_systems'),
	url(r'^ipv4/$', views.list_ipv4, name='ipv4'),
]
