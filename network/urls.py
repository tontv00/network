from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("following/<str:username>", views.following, name="following"),
    path("posts/<int:post_id>/edit", views.edit, name="edit"),
    path("profile/settings/<str:username>", views.settings, name="settings"),
    path("profile/<str:username>/newpost", views.newpost, name="newpost"),
    path("<str:post_id>/delete", views.delete, name="delete"),
    url(r'^likepost/$', views.likepost, name='like-post')
]
