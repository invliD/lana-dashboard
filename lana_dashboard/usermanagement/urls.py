from django.conf.urls import url

from lana_dashboard.usermanagement import views

urlpatterns = [
	url(r'^(?P<username>.*)/$', views.show_user_profile, name='profile'),
]
