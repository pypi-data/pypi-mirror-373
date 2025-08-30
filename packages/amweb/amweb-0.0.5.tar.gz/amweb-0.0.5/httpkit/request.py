# request.py
import urllib.parse

class Request:
    def __init__(self, raw_request):
        # حاول تحليل الطلب الخام
        try:
            # فصل خط الطلب الأول عن الباقي
            first_line = raw_request.split('\n')[0]
            if not first_line:
                self.method, self.path, self.protocol = None, None, None
                self.headers, self.body, self.query_params = {}, {}, {}
                return

            # تحليل أول سطر للحصول على الطريقة والمسار
            parts = first_line.split(' ')
            if len(parts) >= 3:
                self.method, self.path, self.protocol = parts[0], parts[1], parts[2]
            else:
                self.method, self.path, self.protocol = None, None, None

            # استدعاء الدوال الأخرى لتحليل باقي الطلب
            self.headers = self._parse_headers(raw_request)
            self.body = self._parse_body(raw_request)
            self.query_params = self._parse_query_params()
        
        except Exception as e:
            # في حالة وجود أي خطأ في تحليل الطلب
            print(f"Error parsing request: {e}")
            self.method, self.path, self.protocol = None, None, None
            self.headers, self.body, self.query_params = {}, {}, {}

    def _parse_headers(self, raw_request):
        headers = {}
        header_lines = raw_request.split('\n')[1:]
        for line in header_lines:
            if ': ' in line:
                key, value = line.split(': ', 1)
                headers[key.strip()] = value.strip()
        return headers

    def _parse_body(self, raw_request):
        body_start = raw_request.find('\r\n\r\n')
        if body_start != -1:
            body_content = raw_request[body_start + 4:]
            return self._parse_form_data(body_content)
        return {}

    def _parse_form_data(self, body_content):
        # فك ترميز (decode) بيانات النموذج
        decoded_content = urllib.parse.unquote(body_content)
        data = {}
        pairs = decoded_content.split('&')
        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                data[key] = [value]
        return data

    def _parse_query_params(self):
        query_params = {}
        if '?' in self.path:
            _, params_string = self.path.split('?', 1)
            # فك ترميز (decode) المعلمات في الرابط
            decoded_params = urllib.parse.unquote(params_string)
            params = decoded_params.split('&')
            for param in params:
                if '=' in param:
                    key, value = param.split('=', 1)
                    query_params[key] = [value]
        return query_params
