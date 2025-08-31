# encoding=utf-8
import web
import xutils
from xutils import webutil
from xnote.core import xtemplate
from xnote.core import xauth

class LogoutHandler:

    def GET(self):
        _format = xutils.get_argument_str("_format")
        xauth.logout_current_user()
        web.setcookie("sid", "", expires=-1)
        if _format == "json":
            return webutil.SuccessResult()
        raise web.seeother("/")

xurls = (
    r"/logout", LogoutHandler
)