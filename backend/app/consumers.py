# chat/consumers.py
import json
from django.core.serializers.python import Serializer
from django.core.paginator import Paginator
from django.core.serializers import serialize
from channels.generic.websocket import AsyncJsonWebsocketConsumer,AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from django.utils import timezone



from .models import Room,Message,RoomMember,Account,Friend





class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = self.scope['url_route']['kwargs']['uri']

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json["username"]
        room_uri = text_data_json["room_uri"]

        if len(message.lstrip()) != 0:
            room = await get_room_or_error(room_uri)
            user = await get_user_or_error(username)
            user_dict = {
                'id': user.id, 'username': user.username, 'email': user.email,
            }

            await create_room_chat_message(room, user, message)
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user': user_dict,
                }
            )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        user = event['user']
        #print(user)

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'user': user
        }))










@database_sync_to_async
def create_room_chat_message(room, user, message):
    return Message.objects.create(room=room, user=user, message=message)



@database_sync_to_async
def get_room_or_error(room_uri):
    """
    Tries to fetch a room for the user
    """
    try:
        room = Room.objects.get(uri=room_uri)
    except Room.DoesNotExist:
        raise ClientError("ROOM_INVALID", "Invalid room.")
    return room


@database_sync_to_async
def get_user_or_error(username):
    """
    Tries to fetch a room for the user
    """
    print("username :- " + username)
    try:
        user = Account.objects.get(username=username)
    except Account.DoesNotExist:
        raise ClientError("ROOM_INVALID", "Invalid room.")
    return user



