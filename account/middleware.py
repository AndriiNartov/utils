from django.urls import reverse_lazy
from django.http import HttpResponseRedirect

from .views import LoginUserView, RegisterUserView, RegisterUserByInvitationView

allowed_views = (LoginUserView, RegisterUserByInvitationView, RegisterUserView)


class AuthRequiredMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, *view_args, **view_kwargs):
        try:
            if not request.user.is_authenticated and view_func.view_class not in allowed_views:
                return HttpResponseRedirect(reverse_lazy('login'))
        except AttributeError:  # case when view_func is a function, not a class
            return HttpResponseRedirect(reverse_lazy('login'))
