import re
from contextlib import suppress
from datetime import datetime

from django.conf.global_settings import LANGUAGES
from wbcore.utils.importlib import import_from_dotted_path

from .utils import EmlContentParser

languages_dict = dict(LANGUAGES)


def clean_string_with_paragraphs(string):
    return re.sub(r"  +", " ", re.sub(r"(?<!\.)\\n", " ", string.strip()))


def parse(import_source):
    parser = EmlContentParser(
        import_source.file.read(), encoding=import_source.source.import_parameters.get("email_encoding", "latin-1")
    )
    email_date = parser.date if parser.date else datetime.now()

    # Source
    html = parser.html

    # If source define a custom html parser, we import it and convert the returned html
    if html_parser_path := import_source.source.import_parameters.get("html_parser", None):
        with suppress(ModuleNotFoundError):
            html_parser = import_from_dotted_path(html_parser_path)
            html = html_parser(html)

    data = {
        "datetime": email_date.strftime("%Y-%m-%dT%H:%M:%S"),
        "title": parser.subject.replace(f"[{import_source.source.uuid}]", ""),
        "description": html,
        "source": parser.source,
    }

    return {"data": [data]}
