import logging
from django.utils.deprecation import MiddlewareMixin


logger = logging.getLogger('audit')


class AuditMiddleware(MiddlewareMixin):
    """Minimal request audit middleware (stub)."""

    def process_request(self, request):
        request.audit_context = {
            'path': request.path,
            'method': request.method,
            'user_id': getattr(getattr(request, 'user', None), 'id', None),
        }

    def process_response(self, request, response):
        try:
            ctx = getattr(request, 'audit_context', {})
            logger.info('request', extra={'audit': ctx, 'status_code': response.status_code})
        finally:
            return response


