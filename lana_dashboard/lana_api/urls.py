from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from lana_dashboard.lana_api import views

router = DefaultRouter(trailing_slash=False)
router.register(r'hiera', views.HieraViewSet, basename='hiera')
router.register(r'subnet/ipv4', views.IPv4SubnetViewSet, basename='ipv4')
router.register(r'whois', views.WhoisViewSet, basename='whois')

app_name = "lana_api"
urlpatterns = [
	url(r'^', include(router.urls)),
]
