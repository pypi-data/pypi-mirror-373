# -*- coding:utf-8 -*-
# Created by xupingmao on 2016/??/??
# @modified 2021/05/01 13:41:51

"""显示代码原文"""
import os
import web
import logging
import xutils

from xnote.core import xauth
from xnote.core import xtemplate
from xnote.core import xconfig
from xnote.core import xmanager
from xnote.core import xnote_event
from xutils import Storage, fsutil
from xutils import textutil
from xutils import webutil
from xutils import netutil
from xnote.plugin import TextLink

def can_preview(path):
    name, ext = os.path.splitext(path)
    return ext.lower() in (".md", ".csv")


def handle_embed(kw):
    """处理嵌入式常见"""
    embed = xutils.get_argument_bool("embed")

    kw.show_aside = False
    kw.embed = embed
    if embed:
        kw.show_aside = False
        kw.show_left = False
        kw.show_menu = False
        kw.show_search = False
        kw.show_path = False
        kw.show_nav = False


def handle_args(kw: Storage):
    show_path = xutils.get_argument_bool("show_path", True)
    kw.show_path = show_path


def resolve_path(path: str, type=''):
    is_b64 = xutils.get_argument_bool("b64")
    if is_b64:
        path = textutil.decode_base64(path)

    if type == "script":
        path = os.path.join(xconfig.SCRIPTS_DIR, path)
    path = os.path.abspath(path)
    if is_b64:
        return path
    return xutils.get_real_path(path)


class ViewSourceHandler:

    def get_default_kw(self):
        kw = Storage()
        kw._show_footer = False
        return kw

    @xauth.login_required("admin")
    def GET(self, path=""):
        template_name = "code/page/code_edit.html"
        path = xutils.get_argument_str("path", "")
        type = xutils.get_argument_str("type", "")
        offset = xutils.get_argument_int("offset")
        readonly = False

        kw = self.get_default_kw()
        # 处理嵌入页面
        handle_embed(kw)
        # 处理参数
        handle_args(kw)

        if path == "":
            return xtemplate.render(template_name,
                                    content="",
                                    error="path is empty")

        path = resolve_path(path, type)
        kw.path = path

        if not os.path.exists(path):
            kw = Storage()
            kw.content = ""
            kw.warn = "文件不存在"
            return xtemplate.render(template_name, **kw)

        error = ""
        warn = ""
        file_too_large = False
        part_links = []

        try:
            max_file_size = xconfig.MAX_TEXT_SIZE
            file_size = xutils.get_file_size_int(path, raise_exception=True)
            if file_size >= max_file_size:
                readonly = True
                file_too_large = True

            if file_too_large:
                part_links = self.build_part_links(file_size, max_file_size, offset)
            
            content = self.read_part(path, offset, max_file_size)

            plugin_name = fsutil.get_relative_path(path, xconfig.PLUGINS_DIR)
            # 使用JavaScript来处理搜索关键字高亮问题
            # if key != "":
            #     content = xutils.html_escape(content)
            #     key     = xhtml_escape(key)
            #     content = textutil.replace(content, key, htmlutil.span("?", "search-key"), ignore_case=True, use_template=True)
            
            kw.show_preview = can_preview(path)
            kw.readonly = readonly
            kw.error = error
            kw.warn = warn
            kw.pathlist = xutils.splitpath(path)
            kw.name = os.path.basename(path)
            kw.content = content
            kw.plugin_name = plugin_name
            kw.lines = content.count("\n")+1
            kw.file_too_large = file_too_large
            kw.part_links = part_links
            return xtemplate.render(template_name, **kw)
        except Exception as e:
            xutils.print_exc()
            error = e
        
        # 异常逻辑
        kw.name = ""
        kw.readonly = readonly
        kw.error = error
        kw.lines = 0
        kw.content = ""
        return xtemplate.render(template_name, **kw)
    
    def build_part_links(self, file_size: int, max_file_size: int, request_offset: int):
        part_links = []
        offset = 0
        webpath = webutil.get_request_url()
        index = 1
        while offset < file_size:
            href = webutil.replace_url_param(webpath, "offset", str(offset))
            css_class = ""
            if offset == request_offset:
                css_class = "red"
            part_links.append(TextLink(text=f"[{index}]", href=href, css_class=css_class))
            index += 1
            offset += max_file_size
        return part_links

    def read_part(self, path: str, offset: int, max_file_size: int):
        if offset < 0:
            offset = 0
        with open(path, "rb") as fp:
            fp.seek(offset)
            content_bytes = fp.read(max_file_size)
            return content_bytes.decode("utf-8", errors="ignore")

class UpdateHandler(object):

    @xauth.login_required("admin")
    def POST(self):
        path = xutils.get_argument_str("path", "")
        content = xutils.get_argument_str("content", "")
        user_name = xauth.current_name_str()

        if content == "" or path == "":
            # raise web.seeother("/fs/")
            return webutil.FailedResult(code="400", message="path不能为空")
        else:
            content = content.replace("\r\n", "\n")
            xutils.savetofile(path, content)

            event = xnote_event.FileUploadEvent()
            event.fpath = path
            event.user_name = user_name

            # 发送通知刷新文件索引
            xmanager.fire("fs.update", event)
            # raise web.seeother("/code/edit?path=" + xutils.quote(path))
            return webutil.SuccessResult()


xurls = (
    r"/code/view_source", ViewSourceHandler,
    r"/code/view_source/update", UpdateHandler,
    r"/code/update", UpdateHandler,
    r"/code/edit", ViewSourceHandler
)
