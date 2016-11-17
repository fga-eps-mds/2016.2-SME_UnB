from django.conf.urls import url

from . import views

app_name = 'retrieve_password'
urlpatterns = [
url(r'^forgot/', views.forgot_password, name="forgot"),
url(r'^reset/(?P<token>[0-9a-f]+)/', views.confirm_email, name="reset"),
url(r'^reset_password/', views.reset_password, name="reset_password"),
]
