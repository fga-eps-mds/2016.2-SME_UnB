"""SME_UnB URL Configuration

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
from plugins.plugins import BasePlugin
from djangoplugins.utils import include_plugins
import home.views
import plugins.views

urlpatterns = [
    url(r'^$', home.views.index),
    url(r'^admin/', admin.site.urls),
    url(r'^data_reader/', include('data_reader.urls')),
    url(r'^plugins/', plugins.views.index),
    url(r'^content/', include_plugins(BasePlugin)),
    url(r'^content/', include_plugins(
        BasePlugin, '{plugin}/(?P<pk>\d+)/', 'instance_urls'
    )),
]
