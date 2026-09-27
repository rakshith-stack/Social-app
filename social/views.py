from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.db import models

from .models import FriendRequest, Friendship, Post, Profile,  Message


def register_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        print("USERNAME RECEIVED:", repr(username))

        if User.objects.filter(username=username).exists():

            print("USERNAME ALREADY EXISTS")

            return render(
                request,
                "social/register.html",
                {
                    "error": "Username already exists. Please choose another username."
                }
            )

        print("USERNAME IS NEW")

        User.objects.create_user(
            username=username,
            password=password
        )

        return redirect("login")

    return render(
        request,
        "social/register.html"
    )

def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect("home")

        return render(
            request,
            "social/login.html",
            {
                "error": "Invalid username or password"
            }
        )

    return render(
        request,
        "social/login.html"
    )


def logout_view(request):

    logout(request)

    return redirect("login")


@login_required
def home(request):

    friends = []

    friendships = Friendship.objects.filter(user1=request.user)

    for friendship in friendships:
        friends.append(friendship.user2)

    friendships = Friendship.objects.filter(user2=request.user)

    for friendship in friendships:
        friends.append(friendship.user1)

    # Add the logged-in user
    friends.append(request.user)

    # Show own posts + friends' posts
    posts = Post.objects.filter(
        user__in=friends
    ).order_by("-created_at")

    return render(
        request,
        "social/home.html",
        {"posts": posts}
    )

@login_required
def users_view(request):

    search = request.GET.get("search", "")

    if search:
        users = User.objects.filter(
            username__icontains=search
        ).exclude(id=request.user.id)
    else:
        users = User.objects.exclude(
            id=request.user.id
        )

    friends = []

    friendships = Friendship.objects.filter(user1=request.user)

    for friendship in friendships:
        friends.append(friendship.user2.id)

    friendships = Friendship.objects.filter(user2=request.user)

    for friendship in friendships:
        friends.append(friendship.user1.id)

    sent_requests = FriendRequest.objects.filter(
        sender=request.user,
        accepted=False
    ).values_list("receiver_id", flat=True)

    return render(
        request,
        "social/friends.html",
        {
            "users": users,
            "friends": friends,
            "sent_requests": sent_requests,
            "search": search,
        }
    )


@login_required
def send_friend_request(request, user_id):

    receiver = User.objects.get(id=user_id)

    # Don't send request to yourself
    if receiver == request.user:
        return redirect("users")

    # Check if already friends
    already_friends = Friendship.objects.filter(
        user1=request.user,
        user2=receiver
    ).exists() or Friendship.objects.filter(
        user1=receiver,
        user2=request.user
    ).exists()

    if already_friends:
        return redirect("users")

    # Check if a request already exists in either direction
    existing_request = FriendRequest.objects.filter(
        sender=request.user,
        receiver=receiver,
        accepted=False
    ).exists()

    reverse_request = FriendRequest.objects.filter(
        sender=receiver,
        receiver=request.user,
        accepted=False
    ).exists()

    # Create request only if neither exists
    if not existing_request and not reverse_request:

        FriendRequest.objects.create(
            sender=request.user,
            receiver=receiver
        )

    return redirect("users")


@login_required
def accept_friend_request(request, request_id):
    friend_request = FriendRequest.objects.get(
        id=request_id,
        receiver=request.user
    )

    friend_request.accepted = True
    friend_request.save()

    Friendship.objects.get_or_create(
        user1=friend_request.sender,
        user2=friend_request.receiver
    )

    return redirect("requests")


@login_required
def friend_requests_view(request):

    requests = FriendRequest.objects.filter(
        receiver=request.user,
        accepted=False
    )

    return render(
        request,
        "social/requests.html",
        {
            "requests": requests
        }
    )
# 
@login_required
def create_post(request):

    if request.method == "POST":

        content = request.POST.get("content")
        image = request.FILES.get("image")
        video = request.FILES.get("video")

        if content or image or video:

            Post.objects.create(
                user=request.user,
                content=content,
                image=image,
                video=video
            )

        return redirect("home")

    return redirect("home")


@login_required
def my_friends(request):

    friends = []

    friendships = Friendship.objects.filter(
        user1=request.user
    )

    for friendship in friendships:
        if friendship.user2 not in friends:
            friends.append(friendship.user2)

    friendships = Friendship.objects.filter(
        user2=request.user
    )

    for friendship in friendships:
        if friendship.user1 not in friends:
            friends.append(friendship.user1)

    # Get latest message for every friend
    friend_data = []

    for friend in friends:

        latest_message = Message.objects.filter(
            sender__in=[request.user, friend],
            receiver__in=[request.user, friend]
        ).order_by("-created_at").first()

        friend_data.append({
            "friend": friend,
            "latest_message": latest_message
        })

    # Friends with messages come first.
    # Friends without messages come after them.
    friend_data.sort(
        key=lambda x: (
            x["latest_message"] is not None,
            x["latest_message"].created_at
            if x["latest_message"]
            else datetime.min
        ),
        reverse=True
    )

    unread_messages = Message.objects.filter(
        receiver=request.user,
        is_read=False
    ).exists()

    return render(
        request,
        "social/my_friends.html",
        {
            "friend_data": friend_data,
            "unread_messages": unread_messages,
        }
    )

@login_required
def profile_view(request):

    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    friends = []

    friendships = Friendship.objects.filter(
        user1=request.user
    )

    for friendship in friendships:

        if friendship.user2 not in friends:
            friends.append(friendship.user2)

    friendships = Friendship.objects.filter(
        user2=request.user
    )

    for friendship in friendships:

        if friendship.user1 not in friends:
            friends.append(friendship.user1)

    friend_count = len(friends)

    # Get posts created by this user
    posts = Post.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "social/profile.html",
        {
            "profile_user": request.user,
            "profile": profile,
            "friend_count": friend_count,
            "posts": posts,
        }
    )


@login_required
def edit_profile(request):

    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        request.user.email = request.POST.get("email")
        request.user.save()

        if request.FILES.get("profile_picture"):
            profile.profile_picture = request.FILES["profile_picture"]
            profile.save()

        return redirect("profile")

    return render(
        request,
        "social/edit_profile.html",
        {
            "profile_user": request.user,
            "profile": profile,
        }
    )


@login_required
def delete_post(request, post_id):

    post = Post.objects.get(
        id=post_id,
        user=request.user
    )

    post.delete()

    return redirect("home")

@login_required
def edit_post(request, post_id):

    post = Post.objects.get(
        id=post_id,
        user=request.user
    )

    if request.method == "POST":

        content = request.POST.get("content")
        image = request.FILES.get("image")
        video = request.FILES.get("video")

        post.content = content

        # Replace image if a new image is selected
        if image:
            post.image = image

        # Replace video if a new video is selected
        if video:
            post.video = video

        post.save()

        return redirect("home")

    return render(
        request,
        "social/edit_post.html",
        {
            "post": post
        }
    )


@login_required
def chat_view(request, user_id):

    other_user = User.objects.get(id=user_id)

    are_friends = Friendship.objects.filter(
        user1=request.user,
        user2=other_user
    ).exists() or Friendship.objects.filter(
        user1=other_user,
        user2=request.user
    ).exists()

    if not are_friends:
        return redirect("my_friends")

    # Mark messages from this friend as read
    Message.objects.filter(
        sender=other_user,
        receiver=request.user,
        is_read=False
    ).update(is_read=True)

    messages = Message.objects.filter(
        models.Q(sender=request.user, receiver=other_user) |
        models.Q(sender=other_user, receiver=request.user)
    ).order_by("created_at")

    if request.method == "POST":

        content = request.POST.get("content")

        if content:
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                content=content
            )

        return redirect("chat", user_id=other_user.id)

    return render(
    request,
    "social/chat.html",
    {
        "other_user": other_user,
        "messages": messages,
        "current_user": request.user,
    }
)

@login_required
def delete_message(request, message_id):

    message = Message.objects.get(
        id=message_id,
        sender=request.user
    )

    other_user = message.receiver

    message.delete()

    return redirect("chat", user_id=other_user.id)