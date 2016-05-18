from django.conf.urls import url

from lana_dashboard.lana_generator import views

urlpatterns = [
	url(r'^fastd/AS(?P<as_number1>\d+)-AS(?P<as_number2>\d+)/(?P<endpoint_number>\d+)/$', views.generate_fastd, name='generate-fastd'),
]
