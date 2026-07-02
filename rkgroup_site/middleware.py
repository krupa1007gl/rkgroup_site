import re
import logging
from django.utils.deprecation import MiddlewareMixin
from services.visit_tracker import visit_tracker

logger = logging.getLogger(__name__)


class VisitTrackingMiddleware(MiddlewareMixin):
    IGNORE_PATTERNS = [
        r'^/admin/', r'^/static/', r'^/media/', r'\.css$', r'\.js$',
        r'\.jpg$', r'\.jpeg$', r'\.png$', r'\.gif$', r'\.svg$', r'\.ico$'
    ]

    def process_request(self, request):
        referer = request.META.get('HTTP_REFERER', '')
        request.referer = referer

    def process_response(self, request, response):
        if request.method != 'GET':
            return response

        for pattern in self.IGNORE_PATTERNS:
            if re.match(pattern, request.path):
                return response

        ip = self._get_client_ip(request)
        if response.status_code in [200, 404]:
            visit_tracker.add_visit(ip, request.path, request.referer, request.META.get('HTTP_USER_AGENT', ''), response.status_code)

        return response

    def _get_client_ip(self, request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        return xff.split(',')[0] if xff else request.META.get('REMOTE_ADDR', '')
