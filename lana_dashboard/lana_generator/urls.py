from django.conf.urls import url

from lana_dashboard.lana_generator import views


app_name = "lana_generator"
urlpatterns = [
	url(r'^fastd/AS(?P<as_number1>\d+)-AS(?P<as_number2>\d+)/(?P<endpoint_number>\d+)/$', views.generate_fastd, name='generate-fastd'),
]
