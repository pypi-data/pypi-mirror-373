from django.http import HttpRequest

from prune_captcha.utils import verify_captcha
from prune_lib.website.contact import (
    RateLimitError,
    check_rate_limit,
)


def verify_form_with_captcha_and_rate_limit(
    request: HttpRequest, contact_form_response
) -> bool:
    captcha_ok = verify_captcha(request)
    if captcha_ok:
        try:
            check_rate_limit(request, contact_form_response)
        except RateLimitError:
            return False
        else:
            return True
    else:
        return False
