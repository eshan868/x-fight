from channels.generic.websocket import WebsocketConsumer

class MatchroomConsumer(WebsocketConsumer):
    def connect(self):
        return super().connect()