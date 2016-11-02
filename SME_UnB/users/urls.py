from django.conf.urls import url

from . import views

app_name = 'users'
urlpatterns = [
    url(r'^dashboard/$', views.dashboard, name="dashboard"),
    url(r'^$', views.show_login, name="home"),
    url(r'^login/$', views.show_login, name="login"),
    url(r'^logout/$', views.logout_view, name="logout"),
    url(r'^register/', views.register, name="register"),
    url(r'^forgot/', views.forgot_password, name="forgot"),
    url(r'^list_user_edit/', views.list_user_edit, name="list_user_edit"),
    url(r'^list_user_delete/', views.list_user_delete, name="list_user_delete"),
    url(r'^edit_user/(?P<user_id>[0-9]+)/',views.edit_user, name="edit_user"),
    url(r'^delete_user/(?P<user_id>[0-9]+)/',views.delete_user, name="delete_user"),
]
