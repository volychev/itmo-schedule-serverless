from pathlib import Path

from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).parent / "templates"

def render_index(file_info: list[dict], start_date: str, end_date: str, last_updated: str) -> str:
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template("index.html")

    return template.render(
        files=file_info,
        start_date=start_date,
        end_date=end_date,
        last_updated=last_updated,
    )
