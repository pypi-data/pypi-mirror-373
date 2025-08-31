import os
import xutils
import web

from xutils import Storage
from xnote.core import xconfig
from xnote.core import xauth
from xnote.core import xtemplate
from . import plugin_util
from .dao import add_visit_log

class TccHandler:

    C_TEMPLATE = """
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int main(int argc, char* argv) {
    printf("hello,world!");
    return 0;
}
"""

    @xauth.login_required("admin")
    def GET(self):
        code = xutils.get_argument_str("code")
        return_json = xutils.get_argument_bool("json")
        output = ""
        if code == "":
            code = self.C_TEMPLATE
        else:
            path = os.path.join(xconfig.TMP_DIR, "temp.c")
            xutils.savetofile(path, code)
            status, output = xutils.getstatusoutput("D:\\tcc\\tcc.exe -run %s" % path)

            if return_json:
                return xutils.json_str(status=status, output=output)
        return xtemplate.render("tools/tcc.html", 
            show_aside = False,
            code = code,
            output = output)
            
    def POST(self):
        return self.GET()


class LoadInnerToolHandler:

    def GET(self, name: str):
        user_name = xauth.current_name_str()
        url = "/tools/" + name
        fname = xutils.unquote(name)
        if not name.endswith(".html"):
            fname += ".html"
        # Chrome下面 tools/timeline不能正常渲染
        web.header("Content-Type", "text/html")
        fpath = os.path.join(xconfig.HANDLERS_DIR, "tools", fname)
        if os.path.exists(fpath):
            if user_name != None:
                add_visit_log(user_name, url)
            kw = Storage()
            kw.show_aside = False
            kw.parent_link = plugin_util.get_dev_link()
            return xtemplate.render("tools/" + fname, **kw)
        else:
            raise web.notfound()

    def POST(self, name):
        return self.GET(name)


xurls = (
    r"/tools/tcc", TccHandler,
    r"/tools/(.+)", LoadInnerToolHandler,
)