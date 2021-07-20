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
        """
        Called when the websocket is handshaking as part of initial connection.
        """
        print("Chat: connect: " + str(self.scope["user"]))
        self.room_uri = self.scope['url_route']['kwargs']['uri']
        # let everyone connect. But limit read/write to authenticated users
        await self.accept()
        #self.room_id = None

    async def disconnect(self, code):
        """
        Called when the WebSocket closes for any reason.
        """
        # leave the room
        print("Chat: disconnect")
        '''try:
        if self.room_id != None:
        await self.leave_room(self.room_id)
        except Exception:
        pass'''


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        #print(message)
        """
        Called when we get a text frame. Channels will JSON-decode the payload
        for us and pass it as the first argument.
        """
        command = text_data_json.get("command")
        if command == "send":
            if len(text_data_json["message"].lstrip()) != 0:
                await self.send_room(text_data_json["room_uri"], text_data_json["message"],text_data_json["username"])
    


    async def send_room(self, room_uri, message,username):
        """
        Called by receive_json when someone sends a message to a room.
        """
        # Check they are in this room
        #print("Chat: send_room")
        # Get the room and send to the group about it
        room = await get_room_or_error(room_uri)
        user = await get_user_or_error(username)
        
        await create_room_chat_message(room, user, message)

        await self.channel_layer.group_send(
            self.room_uri,
            {
                "type": "chat_message",
                "message": message,
            }
        )

    
    async def chat_message(self, event):
        """
        Called when someone has messaged our chat.
        """
        message = event['message']
        print(message)
        await self.send(text_data=json.dumps({
            'message': message
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



