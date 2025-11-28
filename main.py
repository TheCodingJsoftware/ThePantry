import os

import tornado.httpserver
import tornado.web
from tornado.ioloop import IOLoop

from config.environments import Environment
from config.logging_config import setup_logging
from routes import route_map
from utils.database import init_master_pool

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


async def async_init():
    await init_master_pool()


if __name__ == "__main__":
    IOLoop.current().run_sync(async_init)

    app = tornado.httpserver.HTTPServer(make_app(), xheaders=True)
    app.listen(Environment.PORT, address="0.0.0.0")

    print(f"Backend running on port {Environment.PORT}...")

    IOLoop.current().start()
