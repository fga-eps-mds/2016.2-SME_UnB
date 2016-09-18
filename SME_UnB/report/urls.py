from django.conf.urls import url

from . import views

app_name = 'report'
urlpatterns = [
    url(r'^report/$', views.report, name="report"),
    url(r'^open_pdf/$', views.open_pdf, name="open_pdf"),


]
