from django.views.generic.base import RedirectView, TemplateView, View
from django.http import JsonResponse

import uuid


class OtherOriginRedirectView(RedirectView):
    url = 'http://localhost:8000/target/'


class TargetView(TemplateView):
    template_name = 'target.html'

    def get_context_data(self, *args, **kwargs):
        if 'obj' not in self.request.session:
            self.request.session['obj'] = uuid.uuid4().hex

        return {
            'CSRF_COOKIE': self.request.META.get('CSRF_COOKIE', ''),
            'obj': self.request.session['obj']
        }

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class AjaxView(View):

    def get(self, request, *args, **kwargs):
        return JsonResponse({'hello': 'world'})
