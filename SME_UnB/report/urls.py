from django.conf.urls import url

from . import views

app_name = 'report'
urlpatterns = [
    url(r'^report/(?P<transductor_id>[0-9]+)/$', views.report, name="report"),
    url(r'^open_pdf/(?P<transductor_id>[0-9]+)/$', views.open_pdf, name="open_pdf"),
    url(r'^invoice/$', views.invoice, name="invoice"),
    url(r'^transductors_filter/$', views.transductors_filter, name="transductors_filter"),
    url(r'^get_data_by_time/(?P<transductor_id>[0-9]+)/$', views.get_measurements_filter_transductor, name="get_measurements_filter_transductor"),
    url(r'^list_transductors/$', views.list_transductors, name="list_transductors"),
    url(r'^return_chart/$', views.return_chart, name="return_chart"),

]
