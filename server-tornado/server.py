#!/usr/local/bin/python3

"""
Messing around with Tornado, trying to figure things out.

Pretty much a copy of https://github.com/tornadoweb/tornado/blob/master/demos/websocket/chatdemo.py
"""

# "Hello World" dependencies
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

# Websocket demo dependencies
import logging
import tornado.escape
import tornado.websocket
import os.path
import uuid

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

# Main web app class
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/chatsocket", ChatSocketHandler),
        ]
        settings = dict(
            cookie_secret="TODO:_Figure_This_Out",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
        )
        super(Application, self).__init__(handlers, **settings)

# Handler class for the main page
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", messages=ChatSocketHandler.cache)

# Handler class for the websocket route
class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    cache = []
    cache_size = 200

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        ChatSocketHandler.waiters.add(self)

    def on_close(self):
        ChatSocketHandler.waiters.remove(self)

    @classmethod
    def update_cache(cls, chat): # cls is ChatSocketHandler
        # Add the message to the cache
        cls.cache.append(chat)
        # If the cache has been exceeded, clear it
        if (len(cls.cache) > cls.cache_size):
            cls.cache = cls.cache[-cls.cache_size]

    @classmethod
    def send_updates(cls, chat):
        logging.info("sending message to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            try:
                waiter.write_message(chat)
            except:
                loggin.error("Eerror sending message", exc_info=True)

    def on_message(self, message):
        logging.info("got message %r", message)
        parsed = tornado.escape.json_decode(message)
        chat = {
            "id": str(uuid.uuid4()),
            "body": parsed["body"]
        }
        chat["html"] = tornado.escape.to_basestring(
            self.render_string("message.html", message=chat)
        )
        ChatSocketHandler.update_cache(chat)
        ChatSocketHandler.send_updates(chat)

# Main method
def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
