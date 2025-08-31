# encoding=utf-8
from xnote.plugin import TextLink
from xnote.plugin import TabBox

class LinkConfig:
    app_index = TextLink(text="应用", href="/system/index")
    develop_index = TextLink(text="开发", href="/plugin_list?category=develop")
    system_index = TextLink(text="系统", href="/plugin_list?category=system")
    plugin_index = TextLink(text="插件中心", href="/plugin_list")


class TabConfig:

    # 编解码工具
    encode_tab = TabBox(tab_key="tab", tab_default="base64", css_class="btn-style")
    encode_tab.add_item(title="BASE64", value="BASE64", href="/tools/encode?tab=BASE64&type=base64")
    encode_tab.add_item(title="BASE32", value="BASE32", href="/tools/encode?tab=BASE32&type=base32")
    encode_tab.add_item(title="16进制转换", value="hex", href="/tools/hex?tab=hex")
    encode_tab.add_item(title="URL编解码", value="urlcoder", href="/tools/urlcoder?tab=urlcoder")
    encode_tab.add_item(title="MD5", value="MD5", href="/tools/hash?tab=MD5&type=md5")
    encode_tab.add_item(title="SHA-1", value="SHA-1", href="/tools/hash?tab=SHA-1&type=sha1")
    encode_tab.add_item(title="SHA-256", value="SHA-256", href="/tools/hash?tab=SHA-256&type=sha256")
    encode_tab.add_item(title="SHA-512", value="SHA-512", href="/tools/hash?tab=SHA-512&type=sha512")
    encode_tab.add_item(title="条形码", value="barcode", href="/tools/barcode?tab=barcode")
    encode_tab.add_item(title="二维码", value="qrcode", href="/tools/qrcode?tab=qrcode")


    # 图片工具
    img_tab = TabBox(tab_key="tab", tab_default="img_split", css_class="btn-style")