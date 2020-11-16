
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("new_post", views.new_post, name="new_post"),
    path("register", views.register, name="register"),
    path('following', views.following, name='following'),
    path('follow/<int:user_id>', views.follow, name='follow'),
    path('posts/<int:post_id>', views.toggle_like, name='like'),
    path('edit/<int:post_id>', views.edit_post, name='edit'),
    path("profile/<str:username>", views.user, name="user"),
]
