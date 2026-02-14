import asyncio
from starlette.templating import Jinja2Templates
from apps.core.settings import app_settings
from weasyprint import HTML
from email.message import EmailMessage
from apps.core.settings import email_settings
import smtplib

def generate_pdf(html_content: str) -> bytes:
    return HTML(string=html_content).write_pdf()



async def generate_html(note: dict, author_login: str) -> None:
    templates = Jinja2Templates(directory=app_settings.templates_dir)
    template = templates.get_template(name="note_page.html")

    content_with_breaks = note["content"].replace(";", "<br>")
    html_content = template.render(title_note=note["title"],
                                   content_note=content_with_breaks,
                                   tags_note=note["tags"],
                                   created_at_note=note["created_at"],
                                   updated_at_note=note["updated_at"],
                                   author_login=author_login)

    loop = asyncio.get_running_loop()

    await loop.run_in_executor(None, lambda: send_pdf_to_email(author_login, html_content))


def send_pdf_to_email(author_login: str, html_content: str) -> None:
    pdf_bytes = generate_pdf(html_content)

    message = EmailMessage()
    message["From"] = email_settings.email_username
    message["To"] = author_login
    message["Subject"] = "PDF версия вашей заметки"

    message.add_alternative(html_content, subtype="html")

    message.add_attachment(pdf_bytes, maintype="application", subtype="pdf", filename="note.pdf")
    with smtplib.SMTP_SSL(host=email_settings.email_host,
                          port=email_settings.email_port) as smtp:
        smtp.login(user=email_settings.email_username,
                   password=email_settings.email_password,
                   )
        smtp.send_message(msg=message)
