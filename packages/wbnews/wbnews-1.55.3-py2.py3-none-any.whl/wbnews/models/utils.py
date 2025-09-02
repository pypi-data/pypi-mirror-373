from contextlib import suppress
from urllib.parse import urlparse


def endpoint_to_author(endpoint: str) -> str:
    author = endpoint
    if "@" in endpoint:  # simplist way to check if the endpoint is an email address
        author = author.replace("\\", "").split("@")[-1].split(".")
        if len(author) > 1:
            author = ".".join(author[:-1])
    else:  # otherwise we consider it's a valid url and we extract only the domain part
        with suppress(ValueError, IndexError):
            author = urlparse(author).netloc.split(".")[-2]

    return author.replace("_", " ").title()
