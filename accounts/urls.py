from django.urls import path
from .views import page_register, page_login, home_page, create_publication, like_publication, out, create_comments, open_publication

urlpatterns = [
    path("register/", page_register, name = "register"),
    path("login/", page_login, name = "login"),
    path("test/", create_publication, name = "create_publication"),
    path("", home_page, name = "home_page"),
    path("like/<slug:slug>/", like_publication, name="like_publication"),
    path("logout/", out),
    path("create_c/<slug:slug>/", create_comments, name="create_comments"),
    path('create_c/<slug:slug>/<int:parent>/', create_comments, name='create_reply'),
    path('pub/<slug:slug>/', open_publication, name="pub"),

]
