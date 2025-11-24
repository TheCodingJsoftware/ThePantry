import os

from handlers.page import PageHandler
from handlers.static.custom import CustomStaticFileHandler
from routes.route import route

page_routes = [
    route(r"/", PageHandler, name="index", template_name="index.html"),
]

api_routes = []

static_routes = [
    (
        r"/static/(.*)",
        CustomStaticFileHandler,
        {
            "path": os.path.abspath("dist/static"),
        },
    ),
    route(r"/dist/(.*)", CustomStaticFileHandler, path="dist"),
    route(
        r"/(favicon\.ico|manifest\.json|robots\.txt|apple-touch-icon\.png|service-worker\.js|service-worker\.js\.map|workbox-.*\.js|workbox-.*\.js\.map|icon\.png)",
        CustomStaticFileHandler,
        path="dist",
    ),
]

routes = page_routes + api_routes + static_routes
