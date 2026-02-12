import asyncio
from starlette.templating import Jinja2Templates
from apps.core.settings import app_settings
from weasyprint import HTML

def generate_pdf(html_content):
    HTML(string=html_content).write_pdf('note_html_to_pdf.pdf')


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

    await loop.run_in_executor(None, lambda: generate_pdf(html_content))
