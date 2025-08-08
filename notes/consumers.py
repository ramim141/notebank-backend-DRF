import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'notifications_group'
        # Accept regardless to avoid crashing when no layer
        await self.accept()

        if not self.channel_layer:
            return

        # Join global notifications group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Join per-user group if authenticated
        user = self.scope.get('user')
        if getattr(user, 'is_authenticated', False):
            self.user_group = f'user_{user.id}'
            await self.channel_layer.group_add(
                self.user_group,
                self.channel_name
            )
        else:
            self.user_group = None

    async def disconnect(self, close_code):
        if not self.channel_layer:
            return
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        if getattr(self, 'user_group', None):
            await self.channel_layer.group_discard(
                self.user_group,
                self.channel_name
            )

    async def broadcast_notification(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'payload': message
        }))