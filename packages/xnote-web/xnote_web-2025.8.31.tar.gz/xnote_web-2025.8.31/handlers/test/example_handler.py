# encoding=utf-8
# Created by xupingmao on 2024/09/15
import xutils
import copy

from datetime import date
from xutils import Storage
from xnote.core import xauth
from xnote.core import xtemplate
from xnote.core import xmanager
from xnote.core import xconfig
from xnote.plugin.table_plugin import BaseTablePlugin, BasePlugin
from xnote.plugin import DataTable, TableActionType, TabBox, QueryForm
from xnote.plugin.table import InfoTable, InfoItem, ActionBar
from xnote.plugin.calendar import ContributionCalendar
from xnote.plugin.list import ListView, ListItem, ConfirmButton, TextTag
from xutils import textutil
from xutils import webutil
from xutils.number_utils import IntCounter
from handlers.config import LinkConfig

def get_example_tab():
    tab = TabBox(tab_key="name", title="案例:", css_class="btn-style")
    tab.add_tab("文本示例", value="text", href=f"/test/example?name=text")
    tab.add_tab("按钮示例", value="btn", href=f"/test/example?name=btn")
    tab.add_tab("Tab示例", value="tab", href=f"/test/example?name=tab")
    tab.add_tab("Tag示例", value="tag", href=f"/test/example?name=tag")
    tab.add_tab("Dialog示例", value="dialog", href=f"/test/example?name=dialog")
    tab.add_tab("Dropdown示例", value="dropdown", href=f"/test/example?name=dropdown")
    tab.add_tab("Table示例", value="table", href=f"/test/example/table?name=table")
    tab.add_tab("ListView示例", value="list", href=f"/test/example/list?name=list")
    tab.add_tab("日历组件", value="calendar", href="/test/example/calendar?name=calendar")
    tab.add_tab("Hammer示例", value="hammer", href=f"/test/example?name=hammer")
    return tab

class TableExampleHandler(BaseTablePlugin):

    parent_link = LinkConfig.develop_index
    
    title = "表格测试"

    show_aside = False

    heading_count = IntCounter()

    PAGE_HTML = """
{% include test/component/example_nav_tab.html %}

<div class="card">
    {% render tab %}
</div>

<div class="card">
    {% render info_table %}
</div>

<div class="card">
    {% render query_form %}
</div>

<div class="card">
    {% include common/table/table_v2.html %}
</div>

<div class="card">
    {% set-global xnote_table_var = "weight_table" %}
    {% include common/table/table_v2.html %}
</div>

<div class="card">
    {% render empty_table %}
</div>
"""

    def handle_page(self):
        table = DataTable()
        table.title = "表格1-自动宽度"
        table.add_head("类型", "type", css_class_field="type_class")
        table.add_head("标题", "title", link_field="view_url")
        table.add_head("日期", "date")
        table.add_head("内容", "content")

        table.add_action("编辑", link_field="edit_url", type=TableActionType.edit_form)
        table.add_action("删除", link_field="delete_url", type=TableActionType.confirm, 
                         msg_field="delete_msg", css_class="btn danger")

        row = {}
        row["type"] = "类型1"
        row["title"] = "测试"
        row["type_class"] = "red"
        row["date"] = "2020-01-01"
        row["content"] = "测试内容"
        row["view_url"] = "/note/index"
        row["edit_url"] = "?action=edit"
        row["delete_url"] = "?action=delete"
        row["delete_msg"] = "确认删除记录吗?"
        table.add_row(row)

        kw = Storage()
        kw.table = table
        kw.page = 1
        kw.page_max = 1
        kw.page_url = "?page="

        kw.query_form = self.get_query_form()
        kw.weight_table = self.get_weight_table()
        kw.empty_table = self.get_empty_table()
        kw.tab = self.get_tab_component()
        kw.example_tab = get_example_tab()
        kw.info_table = self.get_info_table()

        return self.response_page(**kw)
    
    def handle_edit(self):
        self.heading_count.add(1)
        show_heading = self.heading_count.value % 2 == 0

        form = self.create_form()

        if show_heading:
            form.add_heading("基础信息")

        form.add_row("id", "id", css_class="hide")
        form.add_row("只读属性", "readonly_attr", value="test", readonly=True)
        
        row = form.add_row("类型", "type", type=self.FormRowType.select)
        row.add_option("类型1", "1")
        row.add_option("类型2", "2")
        
        form.add_row("标题", "title")
        form.add_row("日期", "date", type=self.FormRowType.date)
        form.add_row("内容", "content", type=self.FormRowType.textarea)

        if show_heading:
            form.add_heading("高级信息")

        row = form.add_select("标签", field="tags", multiple=True, value=[1,2])
        row.add_option("标签1", "1")
        row.add_option("标签2", "2")
        row.add_option("标签3", "3")

        form.add_row("备注信息")
            
        kw = Storage()
        kw.form = form
        return self.response_form(**kw)
    
    def handle_save(self):
        data_dict = self.get_param_dict()
        return webutil.FailedResult(code="500", message=f"data_dict={data_dict}")
    
    def get_tab_component(self):
        tab = TabBox(tab_key="tab", tab_default="2", css_class="btn-style", title="后端tab组件")
        tab.add_tab(title="选项1", value="1", href="?tab=1")
        tab.add_tab(title="选项2", value="2")
        tab.add_tab(title="选项3", value="3", css_class="hide")
        tab.add_tab(title="onclick", href="#", onclick="javascript:alert('onclick!')")
        return tab
    
    def get_query_form(self):
        type_str = xutils.get_argument_str("type")
        keyword = xutils.get_argument_str("keyword")
        date_str = xutils.get_argument_str("date")

        form = QueryForm()
        row = form.add_select(title="类型", field="type", value=type_str)
        row.add_option("类型-1", "1")
        row.add_option("类型-2", "2")
        form.add_row(title="关键字", field="keyword", value=keyword)
        form.add_date_input(title="日期", field="date", value=date_str)

        return form

    
    def get_weight_table(self):
        table = DataTable()
        table.title = "表格2-权重宽度"
        table.add_head("权重1", field="value1", width_weight=1)
        table.add_head("权重1", field="value2", width_weight=1)
        table.add_head("权重2", field="value3", width_weight=2)
        table.add_head("权重1", field="value4", width_weight=1)
        table.add_action("编辑", link_field="edit_url", type=TableActionType.edit_form)
        table.add_action("删除", link_field="delete_url", type=TableActionType.confirm, 
                         msg_field="delete_msg", css_class="btn danger")
        
        row = {}
        row["value1"] = "value1"
        row["value2"] = "value2"
        row["value3"] = "value3"
        row["value4"] = "value4"
        row["view_url"] = "/note/index"
        row["edit_url"] = "?action=edit"
        row["delete_url"] = "?action=delete"
        row["delete_msg"] = "确认删除记录吗?"

        table.add_row(row)
        return table
    
    def get_empty_table(self):
        table = DataTable()
        table.add_head("权重1", field="value1", width_weight=1)
        table.add_head("权重1", field="value2", width_weight=1)
        table.add_head("权重2", field="value3", width_weight=2)
        table.add_head("权重1", field="value4", width_weight=1)
        table.add_action("编辑", link_field="edit_url", type=TableActionType.edit_form)
        table.add_action("删除", link_field="delete_url", type=TableActionType.confirm, 
                         msg_field="delete_msg", css_class="btn danger")
        
        action_bar = table.action_bar
        action_bar.add_span(text="表格3-action_bar")
        action_bar.add_edit_button(text="新建", url="?action=edit", float_right=True)
        return table
    
    def get_info_table(self):
        table = InfoTable()
        table.cols = xutils.get_argument_int("cols", 2)
        table.add_item(InfoItem(name="组件名称", value="信息表格"))
        table.add_item(InfoItem(name="用途", value="展示对象的详细信息"))
        table.add_item(InfoItem(name="链接", value="xnote首页", href="/"))
        table.add_item(InfoItem(name="其他"))
        table.bottom_action_bar.add_edit_button("编辑", "?action=edit", css_class="btn-default")
        table.bottom_action_bar.add_confirm_button("删除", url="?action=delete", message="确认删除吗?", css_class="danger")
        return table

class ExampleHandler:

    def GET(self):
        user_name = xauth.current_name_str()
        xmanager.add_visit_log(user_name, "/test/example")
        
        name = xutils.get_argument_str("name", "")
        example_tab = get_example_tab()

        if name == "":
            return xtemplate.render("test/page/example_index.html", example_tab=example_tab)
        else:
            return xtemplate.render(f"test/page/example_{name}.html", example_tab=example_tab)

    def POST(self):
        return self.GET()


class CalendarExampleHandler(BasePlugin):
    title = "日历组件"
    rows = 0
    parent_link = LinkConfig.develop_index

    HTML = """
{% include test/component/example_nav_tab.html %}

<h3 class="card-title">贡献日历</h3>
<div class="card">
    {% raw calendar.render() %}
</div>

<h3 class="card-title">日期选择器</h3>
<div class="card">
    <div class="row">
        <div class="input-group">
            <label>年份选择器</label>
            <input type="text" class="date" data-date-type="year">
        </div>
        <div class="input-group">
            <label>月份选择器</label>
            <input type="text" class="date" data-date-type="month">
        </div>
    </div>

    <div class="row">
        <div class="input-group">
            <label>日期选择器</label>
            <input type="text" class="date" data-date-type="date">
        </div>
        <div class="input-group">
            <label>时间选择器</label>
            <input type="text" class="date" data-date-type="time">
        </div>
        <div class="input-group">
            <label>日期时间选择器</label>
            <input type="text" class="date" data-date-type="datetime">
        </div>
    </div>
</div>

{% include common/script/load_laydate.html %}
"""

    def handle(self, input=""):
        start = date(2020, 1, 1)
        end = date(2020, 12, 31)
        data = {
            "2020-01-01": 5,
            "2020-02-16": 1,
            "2020-03-11": 10,
            "2020-04-01": 20,
        }
        calendar = ContributionCalendar(start_date=start, end_date=end, data = data)
        kw = Storage()
        kw.example_tab = get_example_tab()
        kw.calendar = calendar
        self.writehtml(self.HTML, **kw)

class ListExampleHandler(BasePlugin):
    parent_link = LinkConfig.develop_index
    title = "ListView示例"
    rows = 0
    body_html = """
{% include test/component/example_nav_tab.html %}

<div class="card">
    <span class="card-title">ListView: 外层链接</span>
    {% render item_list %}
</div>

<div class="card">
    <span class="card-title">ListView: 内层链接</span>
    {% render item_list2 %}
</div>
"""
    def handle(self, input=""):
        item_list = ListView()
        item_list2 = ListView()

        action = xutils.get_argument_str("action")
        if action == "delete":
            return self.handle_delete()

        for index in range(5):
            text = f"物品-{index+1}"
            item = ListItem(text=text, href=f"javascript:xnote.alert({index+1})", badge_info=f"徽标{index+1}")
            item.show_chevron_right = True
            if index % 2 == 0:
                item.icon_class = "fa fa-file-text-o"
            else:
                item.icon_class = "fa fa-list"
                item.tags.append(TextTag(text="标签", css_class="lightblue"))
                item.tags.append(TextTag(text="标签2", css_class="orange"))
            item.action_btn = ConfirmButton(text="删除", url="?action=delete", message=f"确认删除[{text}]吗", css_class="btn danger")
            
            item_list.add_item(item)

            item2 = copy.deepcopy(item)
            item2.is_link_outside = False
            item2.show_chevron_right = False
            item_list2.add_item(item2)

        kw = Storage()
        kw.item_list = item_list
        kw.item_list2 = item_list2
        kw.example_tab = get_example_tab()

        self.writehtml(html=self.body_html, **kw)

    def handle_delete(self):
        return webutil.FailedResult(code="500", message="mock删除失败")

xurls = (
    r"/test/example", ExampleHandler,
    r"/test/example/table", TableExampleHandler,
    r"/test/example/list", ListExampleHandler,
    r"/test/example/calendar", CalendarExampleHandler,
)