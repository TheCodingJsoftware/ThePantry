import os

import tornado
from tornado.ioloop import IOLoop

from config.environments import Environment
from config.logging_config import setup_logging
from routes import route_map

setup_logging()


def make_app():
    return tornado.web.Application(
        route_map.routes,
        template_path=os.path.abspath("dist"),
        cookie_secret=Environment.COOKIE_SECRET,
        websocket_ping_interval=25,
        websocket_ping_timeout=25,
        debug=Environment.DEBUG,
    )


def shutdown():
    print("Shutting down cleanly...")
    IOLoop.current().stop()


if __name__ == "__main__":
    app = tornado.httpserver.HTTPServer(make_app(), xheaders=True)

    app.listen(int(Environment.PORT), address="0.0.0.0")
    tornado.ioloop.IOLoop.current().start()
