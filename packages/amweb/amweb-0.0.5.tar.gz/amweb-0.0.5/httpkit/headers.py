# httpkit/headers.py
from .status import get_status_message

class HeaderBuilder:
    """
    فئة لبناء رؤوس HTTP بسهولة.
    """
    def __init__(self, is_response=True):
        self.is_response = is_response
        self.status_line = ""
        self.headers = {}
    
    def set_status(self, status_code, message=None):
        if not self.is_response:
            raise ValueError("Status line is only for responses.")
        
        status_message = message or get_status_message(status_code)
        self.status_line = f"HTTP/1.1 {status_code} {status_message}\r\n"
        return self

    def add_header(self, key, value):
        self.headers[key] = value
        return self

    def add_content_type(self, mime_type):
        return self.add_header("Content-Type", mime_type)

    def add_cookie(self, key, value, **kwargs):
        cookie_string = f"{key}={value}"
        options = {
            'expires': kwargs.get('expires'), 'max-age': kwargs.get('max_age'),
            'domain': kwargs.get('domain'), 'path': kwargs.get('path', '/'),
            'secure': kwargs.get('secure', False), 'httponly': kwargs.get('httponly', False)
        }
        for opt, val in options.items():
            if val is not None:
                if isinstance(val, bool) and val:
                    cookie_string += f"; {opt}"
                elif not isinstance(val, bool):
                    cookie_string += f"; {opt}={val}"
        return self.add_header("Set-Cookie", cookie_string)

    def add_cache_control(self, directives):
        return self.add_header("Cache-Control", directives)
        
    def build_response(self, status_code, content_type, content):
        self.set_status(status_code)
        self.add_content_type(content_type)
        return self.build(content=content)

    def build(self, content=None):
        if content is not None:
            # يجب أن يكون طول المحتوى بالبايت
            content_bytes = content.encode("utf-8")
            self.add_header("Content-Length", len(content_bytes))
        else:
            content_bytes = b""

        header_string = self.status_line if self.is_response else ""
        for key, value in self.headers.items():
            header_string += f"{key}: {value}\r\n"
        header_string += "\r\n"
        
        # هذا هو السطر الذي أضفناه: جمع الرؤوس مع المحتوى
        return header_string.encode("utf-8") + content_bytes
