
import xutils

from xnote.core import xauth
from xutils import webutil
from xutils import textutil

class EncodeHandler:

    def GET(self):
        return self.POST()

    @xauth.login_required()
    def POST(self):
        type = xutils.get_argument_str("type")
        input_text = xutils.get_argument_str("input")

        if type == "sha1":
            result = textutil.sha1_hex(input_text)
            return webutil.SuccessResult(result)
        if type == "md5":
            result = textutil.md5_hex(input_text)
            return webutil.SuccessResult(result)
        if type == "sha256":
            result = textutil.sha256_hex(input_text)
            return webutil.SuccessResult(result)
        if type == "sha512":
            result = textutil.sha512_hex(input_text)
            return webutil.SuccessResult(result)
        if type == "base64":
            result = textutil.encode_base64(input_text, strip=False)
            return webutil.SuccessResult(result)
        if type == "base32":
            result = textutil.encode_base32(input_text, strip=False)
            return webutil.SuccessResult(result)

        return webutil.FailedResult(code="404", message=f"不支持的类型:{type}")
    
class DecodeHandler:

    def POST(self):
        type = xutils.get_argument_str("type")
        input_text = xutils.get_argument_str("input")

        try:
            if type == "base64":
                result = textutil.decode_base64(input_text)
                return webutil.SuccessResult(result)
            
            if type == "base32":
                result = textutil.decode_base32(input_text)
                return webutil.SuccessResult(result)
        except Exception as e:
            return webutil.FailedResult(message=str(e))

        return webutil.FailedResult(code="404", message=f"不支持的类型:{type}")



xurls = (
    r"/api/encode", EncodeHandler,
    r"/api/decode", DecodeHandler,
)