from django.contrib import admin
from .models import FriendRequest, Friendship, Post


admin.site.register(FriendRequest)
admin.site.register(Friendship)
admin.site.register(Post)