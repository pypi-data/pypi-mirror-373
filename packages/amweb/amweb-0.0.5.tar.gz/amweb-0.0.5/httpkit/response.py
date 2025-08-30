# httpkit/response.py

from .headers import HeaderBuilder

class Response:
    def __init__(self, status_code, content_type, content):
        self.status_code = status_code
        self.content_type = content_type
        self.content = content

    def build(self):
        header_builder = HeaderBuilder()
        full_response = header_builder.build_response(
            self.status_code, self.content_type, self.content
        )
        return full_response
