import sendgrid
from django.conf import settings
from django.contrib.auth.models import User
from sendgrid.helpers.mail import Mail

EMAIL_SENDER = settings.SENDGRID_EMAIL_SENDER
EMAIL_COPY = settings.SENDGRID_EMAIL_COPY


class SendEmailError(Exception):
    pass


def send_email_with_sendgrid(
    *,
    to_emails: list,
    data: dict,
    template_id: str,
    with_copy: bool | None = None,
    bcc: str | None = None,
) -> None:
    if not settings.SENDGRID_EMAIL_SENDER:
        raise ValueError("Missing SENDGRID_SENDGRID_EMAIL_SENDERAPI_KEY in settings.")
    if not settings.SENDGRID_EMAIL_COPY:
        raise ValueError("Missing SENDGRID_EMAIL_COPY in settings.")
    if not settings.SENDGRID_API_KEY:
        raise ValueError("Missing SENDGRID_API_KEY in settings.")

    sendgrid_api_key = settings.SENDGRID_API_KEY
    sendgrid_client = sendgrid.SendGridAPIClient(sendgrid_api_key)
    message = Mail(
        from_email=EMAIL_SENDER,
        to_emails=to_emails,
    )
    message.dynamic_template_data = data
    message.template_id = template_id
    if with_copy:
        message.add_bcc(EMAIL_COPY)
    if bcc:
        message.add_bcc(bcc)
    response = sendgrid_client.send(message)
    if response.status_code != 202:
        raise SendEmailError


def send_email(
    users: User | str | list[User | str],
    *,
    email_template,
    data: dict | None = None,
    with_copy: bool = True,
    bcc: str | None = None,
) -> None:
    if data is None:
        data = {}
    if isinstance(users, list):
        to_emails = [user if isinstance(user, str) else user.email for user in users]
    else:
        to_emails = [users if isinstance(users, str) else users.email]
    send_email_with_sendgrid(
        to_emails=to_emails,
        data=data,
        template_id=email_template.value,
        with_copy=with_copy,
        bcc=bcc,
    )
