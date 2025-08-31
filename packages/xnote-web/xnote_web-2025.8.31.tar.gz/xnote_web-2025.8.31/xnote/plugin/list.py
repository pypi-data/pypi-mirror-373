import typing

from .base import BaseComponent, BaseContainer
from xnote.core import xtemplate
from .component import ConfirmButton, TextTag, escape_html
from xnote.core import xconfig

class ListItem(BaseComponent):
    # 是否展示右箭头
    show_chevron_right = False
    # 操作按钮
    action_btn : typing.Optional[ConfirmButton] = None
    # 标签列表
    tags: typing.List[TextTag]
    # 默认链接在外部
    is_link_outside = True

    _code = xtemplate.compile_template("""
{% if item.is_link_outside %}
    <a class="list-item {{item.css_class}}" href="{{ item.href }}">
{% else %}
    <div class="list-item {{item.css_class}}">
{% end %}

{% if item.icon_class %}
    <i class="{{item.icon_class}}"></i>
{% end %}
{% if item.is_link_outside %}
    <span>{{ item.text }}</span>
{% else %}
    <a href="{{item.href}}">{{ item.text }}</a>
{% end %}
{% for tag in item.tags %} {% render tag %} {% end %}
<div class="float-right">
    <span class="book-size-span">{{ item.badge_info }}</span>
    {% if item.action_btn %}
        {% render item.action_btn %}
    {% end %}
    {% if item.show_chevron_right %}
        <i class="fa fa-chevron-right"></i>
    {% end %}
</div>

{% if item.is_link_outside %}
    </a>
{% else %}
    </div>
{% end %}
""")

    def __init__(self, text="", href="#", icon_class="", badge_info="", show_chevron_right = False, css_class="") -> None:
        self.text = text
        self.css_class = css_class
        self.icon_class = icon_class
        self.href = xconfig.WebConfig.resolve_path(href)
        self.badge_info = badge_info
        self.show_chevron_right = show_chevron_right
        self.tags = []

    def render(self):
        return self._code.generate(item = self)


class ListView(BaseContainer):    
    _code = xtemplate.compile_template("""
{% if len(item_list) == 0 %}
    {% include common/text/empty_text.html %}
{% end %}

{% for item in item_list %}
    {% render item %}
{% end %}
""")

    def add_item(self, item: ListItem):
        self.add(item)

    def render(self):
        return self._code.generate(item_list = self.children)


ItemList = ListView