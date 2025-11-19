# accounts/adapter.py
from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse

class MyAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated and user.is_staff:
            # send staff users to Django admin
            return reverse("admin:index")
        # otherwise fall back to default behavior (LOGIN_REDIRECT_URL)
        return super().get_login_redirect_url(request)
