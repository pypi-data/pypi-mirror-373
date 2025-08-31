
from xnote.plugin.table_plugin import BaseTablePlugin
from handlers.config import LinkConfig
from xutils import Storage, dateutil
from xnote.core import xauth
from xnote.plugin.table import TableActionType
from xnote.plugin import iter_plugins
from .plugin_page import list_all_plugins

class PluginManageHandler(BaseTablePlugin):
    title = "插件管理"
    parent_link = LinkConfig.plugin_index
    require_admin = True
    show_pagenation = False
    NAV_HTML = ""

    def handle_page(self):
        table = self.create_table()
        table.default_head_style.min_width = "100px"
        table.add_head("插件类别", "category")
        table.add_head("插件名称", "title", link_field="view_url")
        table.add_head("最近使用", "visit_date")
        table.add_head("访问次数", "visit_cnt")

        table.add_action("编辑", link_field="edit_url", type=TableActionType.link, css_class="btn btn-default")
        table.action_bar.add_edit_button(text="新增插件", url="?action=edit")
        table.action_bar.add_link(text="查看插件目录", href="/fs_link/scripts/plugins", css_class="btn btn-default")
        user_name = xauth.current_name_str()

        for plugin in list_all_plugins(user_name):
            if plugin.is_builtin:
                # 不管理内置的工具
                continue

            row = {}
            row["category"] = plugin.category
            row["title"] = plugin.title
            row["visit_date"] = dateutil.format_date(plugin.visit_time)
            row["visit_cnt"] = plugin.visit_cnt
            row["view_url"] = plugin.abs_url
            row["edit_url"] = plugin.edit_link
            table.add_row(row)

        kw = Storage()
        kw.table = table
        return self.response_page(**kw)

xurls = (
    "/plugin_manage", PluginManageHandler,
)