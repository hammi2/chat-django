from django.contrib import admin

from .models import (FriendRequest, Message, MessageGroup, MessageRoom,
                     Notification, UserProfile)

# Register your models here.

admin.site.register(Message)
admin.site.register(MessageRoom)
admin.site.register(MessageGroup)
admin.site.register(UserProfile)
admin.site.register(FriendRequest)
admin.site.register(Notification)
