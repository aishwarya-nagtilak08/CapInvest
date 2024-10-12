import warnings
import logging

from custapp import settings
from custapp import models

from django.conf import settings as SETTINGS

STATIC_BASE_URL = SETTINGS.STATIC_BASE_URL

from django.utils.functional import Promise

logger = logging.getLogger(__name__)

STATIC_URL = SETTINGS.STATIC_URL
print(STATIC_URL)

try:
    from django.urls import NoReverseMatch, reverse
except:
    from django.urls import NoReverseMatch, reverse

from allauth.account.adapter import DefaultAccountAdapter  # , email_address_exists
from django.forms import ValidationError

def resolve_url(to, *args, **kwargs):
    """
    Return a URL appropriate for the arguments passed.

    The arguments could be:

        * A model: the model's `get_absolute_url()` function will be called.

        * A view name, possibly with arguments: `urls.reverse()` will be used
            to reverse-resolve the name.

        * A URL, which will be returned as-is.
    """
    # If it's a model, use get_absolute_url()
    if hasattr(to, 'get_absolute_url'):
        return to.get_absolute_url()

    if isinstance(to, Promise):
        to = str(to)

    if isinstance(to, str):
        if to.startswith(('./', '../')):
            return to

    try:
        return reverse(to, args=args, kwargs=kwargs)
    except NoReverseMatch:
        if callable(to):
            raise
        if '/' not in to and '.' not in to:
            raise

    return to

class custappAdapter(DefaultAccountAdapter):
    
    def get_login_redirect_url(self, request):
        assert request.user.is_authenticated
        url = getattr(settings, "LOGIN_REDIRECT_URLNAME", None)
        if url:
            warnings.warn("LOGIN_REDIRECT_URLNAME is deprecated, simply"
                          " use LOGIN_REDIRECT_URL with a URL name",
                          DeprecationWarning)
        else:
            url = SETTINGS.LOGIN_REDIRECT_URL
        return resolve_url(url)

    def validate_unique_email(self, email):
        if models.Customer.objects.filter(email=email).exists():
            raise ValidationError("This email address is taken.")
        return email
        # def clean_password(self, password1):
        #     if re.match(r'^(?=.*?\d)(?=.*?[A-Z])(?=.*?[a-z])[A-Za-z\d]{8,}$', password1):
        #         return password1
        #     else:
        #         raise ValidationError("Use strong password - atleast one UPPERCASE letter, one digit and one special character.")


