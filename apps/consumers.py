import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Message


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Xonaga kirgan odamga oxirgi xabarlarni yuboramiz
        for text in await self.get_history():
            await self.send(text_data=json.dumps({"message": text}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "")
        if not message:
            return

        await self.save_message(message)
        await self.channel_layer.group_send(
            self.group_name,
            {"type": "chat_message", "message": message},
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({"message": event["message"]}))

    @database_sync_to_async
    def get_history(self):
        last = Message.objects.filter(room=self.room_name).order_by("-id")[:50]
        return [m.text for m in reversed(list(last))]

    @database_sync_to_async
    def save_message(self, text):
        Message.objects.create(room=self.room_name, text=text)