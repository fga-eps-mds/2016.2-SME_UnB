from django.conf.urls import url

from . import views

app_name = 'data_reader'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^new$', views.new, name='new'),
    url(r'^(?P<transductor_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^(?P<transductor_id>[0-9]+)/edit/$', views.edit, name='edit'),
    url(r'^(?P<transductor_id>[0-9]+)/delete/$', views.delete, name='delete'),
    url(r'^model$', views.model_index, name='model_index'),
    url(r'^model/new$', views.model_new, name='model_new'),
]
