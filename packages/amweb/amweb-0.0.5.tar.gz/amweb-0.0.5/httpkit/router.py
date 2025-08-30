# httpkit/router.py
class Router:
    def __init__(self):
        self.routes = {}

    def add_route(self, path, method, handler):
        if path not in self.routes:
            self.routes[path] = {}
        self.routes[path][method.upper()] = handler

    def get(self, path):
        def decorator(handler):
            self.add_route(path, "GET", handler)
            return handler
        return decorator

    def post(self, path):
        def decorator(handler):
            self.add_route(path, "POST", handler)
            return handler
        return decorator
        
    def find_handler(self, path, method):
        if path in self.routes and method.upper() in self.routes[path]:
            return self.routes[path][method.upper()]
        return None
