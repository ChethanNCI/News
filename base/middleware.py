# middleware.py
from django.utils.deprecation import MiddlewareMixin

CSP_HEADER = (
    "default-src 'self'; "
    "script-src 'self' https://cdn.jsdelivr.net https://kit.fontawesome.com; "
    "style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
    "img-src 'self' data: https:; "
    "font-src 'self' https://cdn.jsdelivr.net https://kit.fontawesome.com; "
    "frame-ancestors 'none';"
)

class AddCSPHeaderMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        response['Content-Security-Policy'] = CSP_HEADER
        return response
