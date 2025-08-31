# -*- coding:utf-8 -*-
"""
@Author       : xupingmao
@email        : 578749341@qq.com
@Date         : 2024-05-12 13:14:25
@LastEditors  : xupingmao
@LastEditTime : 2024-05-13 00:38:36
@FilePath     : /xnote/xnote/plugin/tab.py
@Description  : tab选项卡组件
"""
from xnote.core import xtemplate
from xnote.core import xconfig

# TODO: 支持多级tab, 例如 tab=dev.text

class TabBox:
    
    TAB_HTML = """
<div class="x-tab-box {{css_class}}" data-tab-key="{{tab_key}}" data-tab-default="{{tab_default}}">
{% if title %}
    <span class="x-tab title">{{title}}</span>
{% end %}
{% for item in tab_list %}
    <a class="x-tab {{item.css_class}}" 
        {% if item.href != "" %} href="{{item.href}}" {% end %}
        {% if item.onclick != "" %} onclick="{{item.onclick}}" {% end %}
        data-tab-value="{{item.value}}">{{item.title}}</a>
{% end %}
</div>
"""
    _compiled_template = xtemplate.compile_template(TAB_HTML, "xnote.plugin.tab")

    def __init__(self, tab_key="tab", tab_default="", title = "", css_class=""):
        self.tab_key = tab_key
        self.tab_default = tab_default
        self.css_class = css_class
        self.title = title
        self.tab_list = [] # type: list[TabItem]
    
    def add_item(self, title="", value="", href="", css_class="", onclick="", item_id=""):
        item = TabItem(title=title, value=value, href=href, css_class=css_class, onclick=onclick, item_id=item_id)

        if len(item_id) > 0:
            for item in self.tab_list:
                if item.item_id == item_id:
                    # 已经存在
                    return

        self.tab_list.append(item)

    add_tab = add_item

    def render(self, tab_value=""):
        tab_default = self.tab_default
        if tab_value != "":
            tab_default = tab_value
        return self._compiled_template.generate(
            css_class=self.css_class, 
            tab_key=self.tab_key,
            tab_default=tab_default,
            title=self.title,
            tab_list=self.tab_list)


class TabItem:
    def __init__(self, title="", value="", href="", css_class="", onclick="", item_id=""):
        href = xconfig.WebConfig.resolve_path(href)
        self.title = title
        self.value = value
        self.href = href
        self.css_class = css_class
        self.onclick = onclick
        self.item_id = item_id
