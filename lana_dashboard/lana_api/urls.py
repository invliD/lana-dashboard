from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from lana_dashboard.lana_api import views

router = DefaultRouter(trailing_slash=False)
router.register(r'hiera', views.HieraViewSet, base_name='hiera')
router.register(r'subnet/ipv4', views.IPv4SubnetViewSet, base_name='ipv4')
router.register(r'whois', views.WhoisViewSet, base_name='whois')

urlpatterns = [
	url(r'^', include(router.urls)),
]
