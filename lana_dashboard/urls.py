"""lana_dashboard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
	https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
	1. Add an import:  from my_app import views
	2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
	1. Add an import:  from other_app.views import Home
	2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
	1. Import the include() function: from django.conf.urls import url, include
	2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin

from lana_dashboard.lana_data import urls as data_urls
from lana_dashboard.main import views as main
from lana_dashboard.usermanagement import views as usermanagement

urlpatterns = [
	url(r'^admin/', admin.site.urls),
	url(r'^$', main.index, name='main-index'),
	url(r'^lana-apis.js', main.apis, name='main-apis'),
	url(r'^login$', usermanagement.login, name='usermanagement-login'),
	url(r'^logout$', usermanagement.logout, name='usermanagement-logout'),
	url(r'^lana/', include(data_urls, namespace='lana_data')),
]
