import os

from handlers.colony_items import ColonyItemsAPIGetHandler, ColonyItemsPageHandler
from handlers.colony_page import ColonyPageHandler
from handlers.colony_settings import ColonySettingsAPIHandler, ColonySettingsPageHandler
from handlers.login import ColonyAdminLoginHandler
from handlers.logout import ColonyAdminLogoutHandler
from handlers.page import PageHandler
from handlers.register import RegisterHandler
from handlers.static.custom import CustomStaticFileHandler
from routes.route import route

page_routes = [
    # Specific pages first
    route(r"/", PageHandler, name="index", template_name="index.html"),
    route(r"/register", PageHandler, name="register_page", template_name="register.html"),
    # Colony sub-pages
    route(r"/([a-z0-9_\-]+)/logout", ColonyAdminLogoutHandler, name="colony_logout"),
    route(r"/([a-z0-9_\-]+)/login", ColonyAdminLoginHandler, name="colony_login"),
    route(r"/([a-z0-9_\-]+)/items", ColonyItemsPageHandler, name="colony_items"),
    route(r"/([a-z0-9_\-]+)/settings", ColonySettingsPageHandler, name="colony_settings"),
    # Colony dashboard LAST
    route(r"/([a-z0-9_\-]+)", ColonyPageHandler, name="colony_dashboard"),
]

api_routes = [
    route(r"/api/register", RegisterHandler, name="register_api"),
    route(r"/api/colony/([a-z0-9_\-]+)/settings", ColonySettingsAPIHandler, name="colony_settings_api"),
    route(r"/api/colony/([a-z0-9_\-]+)/items", ColonyItemsAPIGetHandler, name="colony_get_items_api"),
    route(r"/api/colony/([a-z0-9_\-]+)/items/add", ColonyItemsPageHandler, name="colony_add_item_api"),
]

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
    route(r"/uploaded_banners/(.*)", CustomStaticFileHandler, path=os.path.join(os.getenv("DATA_PATH", "data"), "uploaded_banners")),
]

routes = api_routes + static_routes + page_routes
