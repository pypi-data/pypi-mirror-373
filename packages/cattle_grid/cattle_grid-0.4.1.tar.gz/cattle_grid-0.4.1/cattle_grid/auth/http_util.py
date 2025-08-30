from dataclasses import dataclass
from enum import StrEnum, auto
from typing import List
import http_sf


class ContentType(StrEnum):
    """The content type of the response"""

    activity_pub = auto()
    html = auto()
    other = auto()


@dataclass
class AcceptEntry:
    content_type: str
    profile: str | None = None
    quality: float = 1.0

    @staticmethod
    def from_header(piece):
        return AcceptEntry(
            content_type=str(piece[0]),
            profile=piece[1].get("profile", None),
            quality=float(piece[1].get("q", 1.0)),
        )

    def to_content_type(self) -> ContentType:
        if self.content_type == "text/html":
            return ContentType.html
        elif self.content_type == "application/activity+json":
            return ContentType.activity_pub
        elif (
            self.content_type == "application/ld+json"
            and self.profile == "https://www.w3.org/ns/activitystreams"
        ):
            return ContentType.activity_pub
        else:
            return ContentType.other


def parse_accept_header(header):
    """
    ```pycon
    >>> header = 'application/activity+json, application/ld+json; profile="https://www.w3.org/ns/activitystreams", text/html;q=0.1'
    >>> parse_accept_header(header)
    [AcceptEntry(content_type='application/activity+json', profile=None, quality=1.0),
        AcceptEntry(content_type='application/ld+json', profile='https://www.w3.org/ns/activitystreams', quality=1.0),
        AcceptEntry(content_type='text/html', profile=None, quality=0.1)]

    ```
    """

    parsed = http_sf.parse(header.encode(), tltype="list")

    return [AcceptEntry.from_header(piece) for piece in parsed]  # type:ignore


def should_serve(header: str | None) -> List[ContentType]:
    """
    Determines what content to serve

    ```python
    >>> should_serve("application/activity+json")
    [<ContentType.activity_pub: 'activity_pub'>]

    >>> should_serve("text/html")
    [<ContentType.html: 'html'>]

    ```
    """
    if header is None:
        return [ContentType.other]

    parsed = sorted(parse_accept_header(header), key=lambda x: x.quality, reverse=True)

    return [x.to_content_type() for x in parsed if x.to_content_type() is not None]
