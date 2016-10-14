from django.conf.urls import url

from . import views

app_name = 'report'
urlpatterns = [
    url(r'^report/(?P<transductor_id>[0-9]+)/$', views.report, name="report"),
    url(r'^open_pdf/$', views.open_pdf, name="open_pdf"),
    url(r'^transductors_filter/$', views.transductors_filter, name="transductors_filter"),



]
