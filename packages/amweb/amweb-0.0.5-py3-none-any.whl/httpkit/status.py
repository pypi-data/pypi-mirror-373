# httpkit/status.py

HTTP_STATUS_MESSAGES = {
    100: "Continue",
    101: "Switching Protocols",
    200: "OK",
    201: "Created",
    202: "Accepted",
    204: "No Content",
    301: "Moved Permanently",
    302: "Found",
    304: "Not Modified",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
}

def get_status_message(status_code):
    """
    تعيد رسالة الحالة القياسية لرمز معين.
    """
    return HTTP_STATUS_MESSAGES.get(status_code, "Unknown Status")
