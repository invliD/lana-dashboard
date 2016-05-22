from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from lana_dashboard.lana_api import views

router = DefaultRouter(trailing_slash=False)

urlpatterns = [
	url(r'^', include(router.urls)),
]
