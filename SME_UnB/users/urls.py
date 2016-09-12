from django.conf.urls import url

from . import views

app_name = 'users'
urlpatterns = [
    url(r'^dashboard/$', views.dashboard, name="dashboard"),
    url(r'^$', views.show_login, name="home"),
    url(r'^login/$', views.show_login, name="login"),
    url(r'^logout/$', views.logout_view, name="logout"),
    url(r'^register/', views.register, name="register"),
    url(r'^list_user/', views.list_user, name="list_user"),
    url(r'^edit_user/(?P<user_id>[0-9]+)/',views.edit_user, name="edit_user"),

    ]
