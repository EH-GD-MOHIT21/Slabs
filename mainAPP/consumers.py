import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Challenge
from channels.db import database_sync_to_async


class ChallengeConsumer(AsyncWebsocketConsumer):


    def validate_user(self):
        user = self.scope["user"]
        try:
            challenge = Challenge.objects.get(id=int(self.room_name))
            users = challenge.participates.all()
            if user in users:
                return True
            else:
                return False
        except Exception as e:
            return False


    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'challenge_%s' % self.room_name
        if not self.scope['user'].is_authenticated:
            self.close()
        else:
            if await database_sync_to_async(self.validate_user)():
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

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'challenge_message',
                'message': message
            }
        )

    # Receive message from room group
    async def challenge_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))