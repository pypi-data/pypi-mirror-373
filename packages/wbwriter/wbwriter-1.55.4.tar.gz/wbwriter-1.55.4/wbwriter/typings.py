from dataclasses import asdict, dataclass
from datetime import datetime
from io import BytesIO
from typing import Any


@dataclass(frozen=True)
class ArticleDTO:
    name: str
    slug: str
    title: str
    teaser_image: BytesIO | None
    created: datetime
    modified: datetime
    content: dict[str, str]
    is_private: bool
    article_structure: dict[str, str]
    status: str
    meta_information: list[dict[str, Any]]
    tags: list[int]

    def to_dict(self):
        return asdict(self)
