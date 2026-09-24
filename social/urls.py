from django.urls import path
from . import views


urlpatterns = [

    path(
        "",
        views.home,
        name="home"
    ),

    path(
        "register/",
        views.register_view,
        name="register"
    ),

    path(
        "login/",
        views.login_view,
        name="login"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),

    path(
        "users/",
        views.users_view,
        name="users"
    ),

    path(
        "send-request/<int:user_id>/",
        views.send_friend_request,
        name="send_friend_request"
    ),

    path(
        "requests/",
        views.friend_requests_view,
        name="requests"
    ),

    path(
        "accept-request/<int:request_id>/",
        views.accept_friend_request,
        name="accept_request"
    ),
    path(
    "create-post/",
    views.create_post,
    name="create_post"
),

]