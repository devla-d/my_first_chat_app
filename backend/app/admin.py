from django.contrib import admin
from .models import Account,Friend,RoomMember,Room,Message

admin.site.register(Account)
admin.site.register(Friend)
admin.site.register(RoomMember)
admin.site.register(Room)
admin.site.register(Message)


