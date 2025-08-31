# -*- coding:utf-8 -*-
# @author mark
# @since 2022/04/03 20:20:57
# @modified 2022/04/03 22:17:05
# @filename system_boot.py

import webbrowser
import threading
import time
import xutils
import tracemalloc

from xnote.core import xmanager
from xnote.core import xconfig
from xnote.core import xauth
from tracemalloc import Snapshot
from xnote.plugin import BasePlugin
from handlers.config import LinkConfig
from xnote.service.system_info_service import SystemInfoEnum
from xutils import mem_util

_boot_snapshot = None
_boot_mem_info = None

if xconfig.WebConfig.ringtone:
    xutils.say("系统已经启动上线")


# 启动打开浏览器选项
if xconfig.WebConfig.open_browser:
    class OpenThread(threading.Thread):
        def run(self):
            time.sleep(2)
            webbrowser.open("http://localhost:%s/" % xconfig.PORT)

    thread = OpenThread()
    thread.start()

if SystemInfoEnum.trace_malloc_enabled.bool_value:
    tracemalloc.start()
    _boot_snapshot = tracemalloc.take_snapshot()
    _boot_mem_info = mem_util.get_mem_info()


@xmanager.listen("sys.init")
def boot_onload(ctx):
    print(ctx)


class TraceMallocHandler(BasePlugin):
    require_admin = True
    title = "trace_malloc"
    rows = 0
    parent_link = LinkConfig.system_index

    def handle(self, input=""):
        if _boot_snapshot is None:
            return "trace malloc not enabled"
        current = tracemalloc.take_snapshot()
        diff = current.compare_to(_boot_snapshot, "lineno")
        result = []
        result.append("boot_mem_info:" + str(_boot_mem_info))
        result.append("current_mem_info:" + str(mem_util.get_mem_info()))
        for item in diff[:20]:
            result.append(str(item))
        
        return "\n".join(result)


xurls = (
    "/system/trace_malloc", TraceMallocHandler,
)