# -*- coding:utf-8 -*-
# @author xupingmao <578749341@qq.com>
# @since 2019/07/18 22:55:08
# @modified 2019/07/20 22:42:44
import xutils
import logging

from xnote.core import xmanager
from xnote.core.xtemplate import BasePlugin
from xnote.plugin import sidebar
from xnote.plugin.table_plugin import BaseTablePlugin
from xutils import dateutil
from xutils import dbutil, BaseDataRecord
from xutils import textutil

ASIDE_HTML = """
{% include system/component/admin_nav.html %}
"""


dbutil.register_table("clip_log", "剪切板历史")

class ClipLogDO(BaseDataRecord):

    def __init__(self):
        self.create_time = ""
        self.content = ""

class ClipLogDao:

    db = dbutil.get_table("clip_log")
    last_log_content = ""
    max_log_count = 500
    max_content_size = 1024 * 1024 # 1MB

    @classmethod
    def init(cls):
        last = cls.db.get_last()
        if last != None:
            cls.last_log_content = last.content

    @classmethod
    def add_log(cls, log_content=""):
        log_content = log_content.strip()
        if log_content == "":
            return
        if log_content == cls.last_log_content:
            return
        
        if len(log_content) > cls.max_content_size:
            logging.warn("clipboard data too large")
            log_content = log_content[:cls.max_content_size]
        
        record = ClipLogDO()
        record.create_time = dateutil.format_datetime()
        record.content = log_content
        cls.db.insert(record)
        cls.last_log_content = log_content
        cls.clear_old_logs()
    
    @classmethod
    def clear_old_logs(cls):
        buf_size = 10
        if cls.db.count() > cls.max_log_count + buf_size:
            for record in cls.db.list(limit=buf_size):
                cls.db.delete(record)

    @classmethod
    def list_recent(cls, offset=0, limit=100):
        result = cls.db.list(reverse=True, limit=limit)
        return ClipLogDO.from_dict_list(result)
    
    @classmethod
    def get_by_id(cls, id=""):
        return cls.db.get_by_id(id)
    
    @classmethod
    def count(cls):
        return cls.db.count()


ClipLogDao.init()

class Main(BaseTablePlugin):

    title = "剪切板记录"
    # 提示内容
    description = ""
    # 访问权限
    require_admin = True
    # 插件分类 {note, dir, system, network}
    category = "system"

    editable = False
    show_aside = True
    
    NAV_HTML = """
{% include system/component/system_log_tab.html %}
"""

    def get_aside_html(self):
        return sidebar.get_admin_sidebar_html()

    def handle_page(self):
        # 输入框的行数
        watch_clipboard()
        op = xutils.get_argument_str("op")
        page = xutils.get_argument_int("page", 1)
        page_size = 20
        offset = (page-1) * page_size

        if op == "detail":
            return self.handle_detail()
        
        records = ClipLogDao.list_recent(offset=offset, limit=page_size)
        
        table = self.create_table()
        table.add_head("时间", "create_time")
        table.add_head("内容", "content_short", detail_field="content")

        for item in records:
            item.content_short = textutil.get_short_text(item.content, 200)
            table.add_row(item)


        kw = xutils.Storage()
        kw.table = table
        kw.page = page
        kw.page_size = page_size
        kw.page_total = ClipLogDao.count()
        kw.page_url = "?log_type=clip&page="
        
        return self.response_page(**kw)

    def handle_detail(self):
        id = xutils.get_argument_str("id")
        return dict(
            code = "success",
            data = ClipLogDao.get_by_id(id)
        )

    def on_init(self, context=None):
        # 插件初始化操作
        pass

MAX_CLIP_SIZE = 1024*1024 # 1MB

@xmanager.listen("cron.minute")
def watch_clipboard(ctx=None):
    try:
        import pyperclip
        content = pyperclip.paste()
        if len(content) > MAX_CLIP_SIZE:
            logging.warn("clip content too large: %s, max_size: %s", len(content), MAX_CLIP_SIZE)
            return
        ClipLogDao.add_log(content)
    except:
        pass


xurls = (
    r"/system/clipboard-monitor", Main
)