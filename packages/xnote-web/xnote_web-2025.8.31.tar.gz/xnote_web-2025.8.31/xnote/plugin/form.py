# -*- coding:utf-8 -*-
"""
@Author       : xupingmao
@email        : 578749341@qq.com
@Date         : 2024-03-10 16:20:05
@LastEditors  : xupingmao
@LastEditTime : 2024-03-31 14:17:08
@FilePath     : /xnote/xnote/plugin/form.py
@Description  : 描述
"""

import typing
from xnote.core import xtemplate

FormValueType = typing.Union[int, str, list]

class FormRowType:
    """表单行的类型"""
    input = "input"
    select = "select"
    textarea = "textarea"
    date = "date"
    heading = "heading"
    html = "html"

class FormRowOption:
    """表单行的选项"""
    def __init__(self):
        self.title = ""
        self.value = ""

class FormRowDateType:
    """日期的类型"""
    year = "year"
    month = "month"
    date = "date"
    time = "time"
    datetime = "datetime"
    default = date

class FormRow:

    date_type = FormRowDateType.date # 用于日期组件
    readonly = False
    multiple = False
    html : typing.Union[str, bytes] = ""


    """数据行"""
    def __init__(self):
        self.id = ""
        self.title = ""
        self.field = ""
        self.placeholder = ""
        self.value = ""
        self.type = FormRowType.input
        self.css_class = ""
        self.options = []

    def add_option(self, title="", value=""):
        option = FormRowOption()
        option.title = title
        option.value = value
        self.options.append(option)
        return self
    
    @property
    def html_attr(self):
        result = ""
        if self.readonly:
            result += " readonly"
        
        if self.multiple:
            result += f" multiple=\"multiple\""
        
        return result
    
class DataForm:
    """数据表格"""

    form_type = "edit"
    form_type_css = ""
    form_method = "POST"
    footer_btn_group_css = "float-right"
    footer_html:typing.Union[str, bytes] = ""
    
    def __init__(self):
        self.id = "0"
        self.row_id = 0
        self.rows = [] # type: list[FormRow]
        self.save_action = "save"
        self.save_btn_css = ""
        self.close_btn_css = ""
        self.model_name = "default"
        self.path = ""
        self.headings = []

    def _create_row_id(self):
        self.row_id += 1
        return f"row_{self.id}_{self.row_id}"

    def add_row(self, title="", field="", placeholder="", value="", 
                type=FormRowType.input, css_class="", readonly=False,
                date_type = FormRowDateType.date):
        row = FormRow()
        row.id = self._create_row_id()
        row.title = title
        row.field = field
        row.placeholder = placeholder
        row.value = value
        row.type = type
        row.css_class = css_class
        row.readonly = readonly
        row.date_type = date_type
        
        self.rows.append(row)
        return row
    
    def _format_value(self, value: FormValueType) -> str:
        if isinstance(value, list):
            values = []
            for item in value:
                values.append(str(item))
            return ",".join(values)
        return str(value)
    
    def add_date_input(self, title = "", field = "", value = "", css_class = "", date_type = FormRowDateType.date):
        row = FormRow()
        row.id = self._create_row_id()
        row.title = title
        row.field = field
        row.value = value
        row.type = FormRowType.date
        row.css_class = css_class
        row.date_type = date_type
        
        self.rows.append(row)
        return row
    
    def add_select(self, title = "", field = "", placeholder = "", value: FormValueType = "", 
                   css_class = "", readonly = False, multiple = False):
        row = FormRow()
        row.id = self._create_row_id()
        row.type = FormRowType.select
        row.title = title
        row.field = field
        row.placeholder = placeholder
        row.value = self._format_value(value)
        row.css_class = css_class
        row.readonly = readonly
        row.multiple = multiple
        
        self.rows.append(row)
        return row

    def add_heading(self, name=""):
        """添加子标题"""
        row = FormRow()
        row.id = self._create_row_id()
        row.title = name
        row.css_class = "form-heading"
        row.type = FormRowType.heading
        self.rows.append(row)

    def add_html(self, html : typing.Union[str, bytes] = ""):
        row = FormRow()
        row.id = self._create_row_id()
        row.html = html
        row.type = FormRowType.html
        self.rows.append(row)
    

    def count_type(self, type=""):
        count = 0
        for item in self.rows:
            if item.type == type:
                count+=1
        return count
    
    def render(self):
        return xtemplate.render("common/form/form.html", form = self)
    
    @property
    def is_edit_form(self):
        return self.form_type == "edit"
    
    @property
    def is_query_form(self):
        return self.form_type == "query"

class QueryForm(DataForm):
    form_type = "query"
    form_type_css = "query-form"
    form_method = "GET"
    footer_btn_group_css = ""
