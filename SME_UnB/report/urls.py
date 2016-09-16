from django.conf.urls import url

from . import views

app_name = 'report'
urlpatterns = [
    url(r'^report/$', views.report, name="report"),

]
