from django.conf.urls import url

from . import views

app_name = 'data_reader'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
]