from django.http import HttpRequest
from django.utils import timezone


class RateLimitError(Exception):
    pass


def get_client_ip(request: HttpRequest) -> str | None:
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def check_rate_limit(request: HttpRequest, contact_form_response) -> None:
    ip_address = get_client_ip(request)
    today = timezone.now().date()

    total_submissions_today = contact_form_response.objects.filter(
        created_at__date=today
    ).count()
    if total_submissions_today >= 100:
        raise RateLimitError

    submissions_by_ip_today = contact_form_response.objects.filter(
        created_at__date=today, ip_address=ip_address
    ).count()
    if submissions_by_ip_today >= 5:
        raise RateLimitError
