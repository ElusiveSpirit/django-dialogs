import datetime
import json
import time
from urllib.parse import urlencode

import tornadoredis
import tornado.websocket
import tornado.ioloop
from tornado import websocket, web, gen

from django.conf import settings
from importlib import import_module

session_engine = import_module(settings.SESSION_ENGINE)

from django.contrib.auth.models import User
from dialogs.models import Thread

c = tornadoredis.Client()
c.connect()

class MainHandler(web.RequestHandler):
    def get(self):
        self.set_header('Content-Type', 'text/plain')
        self.write('Connected to dialog service')


class MessagesHandler(websocket.WebSocketHandler):

    @tornado.gen.engine
    def open(self, thread_id):
        self.client = tornadoredis.Client()
        self.client.connect()
        session_key = self.get_cookie(settings.SESSION_COOKIE_NAME)
        session = session_engine.SessionStore(session_key)
        try:
            self.user_id = session["_auth_user_id"]
            self.sender_name = User.objects.get(id=self.user_id).username
        except (KeyError, User.DoesNotExist):
            self.close()
            return
        if not Thread.objects.filter(
            id=thread_id,
            participants__id=self.user_id
        ).exists():
            self.close()
            return
        self.channel = "".join(['thread_', thread_id,'_messages'])
        self.thread_id = thread_id
        yield tornado.gen.Task(self.client.subscribe, self.channel)
        self.client.listen(self.show_new_message)

    def check_origin(self, origin):
        return True


    def on_message(self, message):
        data = json.loads(message)
        if data['type'] == 'message':
            http_client = tornado.httpclient.AsyncHTTPClient()
            request = tornado.httpclient.HTTPRequest(
                settings.SEND_MESSAGE_API_URL,
                method="POST",
                body=urlencode({
                    "message_text": data['text'].encode("utf-8"),
                    "api_key": settings.API_KEY,
                    "sender_id": self.user_id,
                    "thread_id" : self.thread_id,
                })
            )
            http_client.fetch(request, self.handle_request)
        elif data['type'] == 'message_status':
            pass

    def show_new_message(self, result):
        self.write_message(str(result.body))

    def on_close(self):
        try:
            self.client.unsubscribe(self.channel)
        except AttributeError:
            pass
        def check():
            if self.client.connection.in_progress:
                tornado.ioloop.IOLoop.instance().add_timeout(
                    datetime.timedelta(0.00001),
                    check
                )
            else:
                self.client.disconnect()
        tornado.ioloop.IOLoop.instance().add_timeout(
            datetime.timedelta(0.00001),
            check
        )

    def handle_request(self, response):
        pass

# TODO Separate tornado apps 

application = tornado.web.Application([
    (r"/", MainHandler),
    (r'/ws/(?P<thread_id>\d+)/', MessagesHandler),
])
