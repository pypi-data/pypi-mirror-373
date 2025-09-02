import re
from email import message, parser
from email.utils import parseaddr, parsedate_to_datetime


class EmlContentParser:
    def __init__(self, email: bytes, encoding: str = "latin-1"):
        self.message = parser.BytesParser().parsebytes(email)
        self.encoding = encoding

    @property
    def date(self):
        if date_str := self.message.get("date"):
            return parsedate_to_datetime(date_str)

    @property
    def subject(self) -> str:
        return self.message.get("subject", "")

    @property
    def html(self):
        html = self.get_html(self.message)
        return html.decode(self.encoding) if html else None

    def get_html(cls, parsed: message.Message) -> bytes | None:
        if parsed.is_multipart():
            for item in parsed.get_payload():  # type:message.Message
                if html := cls.get_html(item):
                    return html
        elif parsed.get_content_type() == "text/html":
            return parsed.get_payload(decode=True)
        return None

    @property
    def text(self):
        text = self.get_text(self.message)
        return text.decode(self.encoding) if text else None

    @classmethod
    def get_text(cls, parsed: message.Message) -> bytes | None:
        if parsed.is_multipart():
            for item in parsed.get_payload():
                if text := cls.get_text(item):
                    return text
        elif parsed.get_content_type() == "text/plain":
            return parsed.get_payload(decode=True)
        return None

    @property
    def source(self) -> dict[str, any]:
        match = re.search(r"From:(.*)<([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})>", self.text)
        # we search first for forwarding info
        if match:
            name = match.group(1)
            email = match.group(2)
        else:
            # otherwise we default to the From attribute
            name, email = parseaddr(self.message["From"])

        if not email:
            raise ValueError("Couldn't find valid source data")
        if not name:
            name = email
        source = {"title": name.split("@")[-1].strip().title(), "endpoint": email, "type": "EMAIL"}
        return source
