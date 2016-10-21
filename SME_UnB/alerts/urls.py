from django.conf.urls import url

from . import views

app_name = 'alerts'
urlpatterns = [
    url(r'^alerts/', views , name="alert"),
]
