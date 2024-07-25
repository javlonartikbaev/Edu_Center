from django.utils.deprecation import MiddlewareMixin

from Educational_Center import settings
class DisableCSRF(MiddlewareMixin):
   def process_request(self, request):
      if settings.DEBUG:
         setattr(request, '_dont_enforce_csrf_checks', True)