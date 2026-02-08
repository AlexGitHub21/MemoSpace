import smtplib
from celery import shared_task
from apps.core.settings import email_settings, app_settings
from email.message import EmailMessage
from starlette.templating import Jinja2Templates


@shared_task
def send_confirmation_email(to_email: str, token: str) -> None:
    confirmation_url = f"{app_settings.frontend_url}/auth/register_confirm?token={token}"

    templates = Jinja2Templates(directory=app_settings.templates_dir)
    template = templates.get_template(name="confirmation_email.html")
    html_content = template.render(confirmation_url=confirmation_url)

    message = EmailMessage()
    message.add_alternative(html_content, subtype="html")
    message["From"] = email_settings.email_username
    message["To"] = to_email
    message["Subject"] = "Подтверждение регистрации"

    with smtplib.SMTP_SSL(host=email_settings.email_host, port=email_settings.email_port) as smtp:
        smtp.login(user=email_settings.email_username,
                   password=email_settings.email_password,
                   )
        smtp.send_message(msg=message)