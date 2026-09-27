from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("users/", views.users_view, name="users"),
    path("send-request/<int:user_id>/", views.send_friend_request, name="send_friend_request"),
    path("requests/", views.friend_requests_view, name="requests"),
    path("accept-request/<int:request_id>/", views.accept_friend_request, name="accept_request"),
    path("create-post/", views.create_post, name="create_post"),
    path("edit-post/<int:post_id>/", views.edit_post, name="edit_post"),
    path("delete-post/<int:post_id>/", views.delete_post, name="delete_post"),
    path("my-friends/", views.my_friends, name="my_friends"),
    path("profile/", views.profile_view, name="profile"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path("chat/<int:user_id>/", views.chat_view, name="chat"),
    path("delete-message/<int:message_id>/",views.delete_message,name="delete_message"),
]