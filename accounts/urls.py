from django.urls import path, re_path
from . import views


urlpatterns = [
    path("register/", views.page_register, name = "register"),
    path("login/", views.page_login, name = "login"),
    path("test/", views.create_publication, name = "create_publication"),
    path("", views.home_page, name = "home_page"),
    path("like/<slug:slug>/", views.like_publication, name="like_publication"),
    path("logout/", views.out, name="logout"),
    path("create_c/<slug:slug>/", views.create_comments, name="create_comments"),
    path('create_c/<slug:slug>/<int:parent>/', views.create_comments, name='create_reply'),
    path('pub/<slug:slug>/', views.open_publication, name="pub"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("search/<str:search>/", views.search, name="search"),


    path('testing/<str:search>/', views.test, name='test'),


]
