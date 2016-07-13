from django.conf.urls import url

from lana_dashboard.usermanagement import views

urlpatterns = [
	url(r'^(?P<username>.*)/tokens/$', views.list_tokens, name='tokens'),
	url(r'^(?P<username>.*)/tokens/create$', views.create_token, name='token-create'),
	url(r'^(?P<username>.*)/tokens/(?P<token>[a-f0-9]+)/delete$', views.delete_token, name='token-delete'),
	url(r'^(?P<username>.*)/$', views.show_user_profile, name='profile'),
	url(r'^(?P<username>.*)/edit$', views.edit_user_profile, name='profile-edit'),
]
