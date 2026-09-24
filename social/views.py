from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .models import FriendRequest, Friendship, Post


def register_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():

            return render(
                request,
                "social/register.html",
                {
                    "error": "Username already exists"
                }
            )

        user = User.objects.create_user(
            username=username,
            password=password
        )

        login(request, user)

        return redirect("home")

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

    friendships = Friendship.objects.filter(
        user1=request.user
    )

    for friendship in friendships:
        friends.append(friendship.user2)

    friendships = Friendship.objects.filter(
        user2=request.user
    )

    for friendship in friendships:
        friends.append(friendship.user1)

    posts = Post.objects.filter(
        user__in=friends
    ).order_by("-created_at")

    return render(
        request,
        "social/home.html",
        {
            "posts": posts
        }
    )


@login_required
def users_view(request):

    users = User.objects.exclude(
        id=request.user.id
    )

    return render(
        request,
        "social/friends.html",
        {
            "users": users
        }
    )


@login_required
def send_friend_request(request, user_id):

    receiver = User.objects.get(
        id=user_id
    )

    existing_request = FriendRequest.objects.filter(
        sender=request.user,
        receiver=receiver
    ).exists()

    if not existing_request:

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

    Friendship.objects.create(
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
@login_required
def create_post(request):

    if request.method == "POST":

        content = request.POST.get("content")

        if content:

            Post.objects.create(
                user=request.user,
                content=content
            )

        return redirect("home")

    return redirect("home")