from __future__ import annotations

from datetime import datetime
from enum import Enum, StrEnum

from pydantic import BaseModel, ConfigDict, HttpUrl
from pydantic.alias_generators import to_camel


class OutputFormat(Enum):
    TABLE = "table"
    JSON = "json"
    TEXT = "text"


class MergeStateStatus(StrEnum):
    CONFLICTING = "CONFLICTING"
    MERGEABLE = "MERGEABLE"
    UNKNOWN = "UNKNOWN"


class MinimizedReason(StrEnum):
    ABUSE = "abuse"
    OFF_TOPIC = "off-topic"
    OUTDATED = "outdated"
    RESOLVED = "resolved"
    DUPLICATE = "duplicate"
    SPAM = "spam"


class AuthorKind(StrEnum):
    USER = "User"
    BOT = "Bot"


class PageInfo(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    has_next_page: bool
    end_cursor: str | None


class Author(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    login: str
    avatar_url: str
    database_id: int
    kind: AuthorKind

    @property
    def is_bot(self) -> bool:
        return self.kind == AuthorKind.BOT


class Commit(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    abbreviated_oid: str


class ParsedComment(BaseModel):
    url: HttpUrl
    body: str
    body_text: str

    is_outdated: bool

    is_minimized: bool
    minimized_reason: MinimizedReason | None = None

    is_resolved: bool
    resolved_by: str | None = None

    path: str | None = None
    line: int | None = None

    commit: str | None = None
    author: str | None = None
    is_bot: bool = False

    created_at: datetime
    updated_at: datetime


class Comment(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    url: HttpUrl
    body: str
    body_text: str
    outdated: bool
    is_minimized: bool
    minimized_reason: MinimizedReason | None
    path: str | None = None
    line: int | None = None
    commit: Commit | None = None
    author: Author | None = None
    created_at: datetime
    updated_at: datetime


class CommentsConnection(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    nodes: list[Comment]
    page_info: PageInfo


class ReviewThread(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    is_collapsed: bool
    is_outdated: bool
    is_resolved: bool
    resolved_by: Author | None
    comments: CommentsConnection


class ReviewThreadsConnection(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    page_info: PageInfo
    nodes: list[ReviewThread]


class PullRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    url: HttpUrl
    body: str | None
    body_text: str | None
    closed: bool
    merged: bool
    author: Author | None
    mergeable: MergeStateStatus | None = None
    review_threads: ReviewThreadsConnection
    created_at: datetime
    updated_at: datetime


class Repository(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    pull_request: PullRequest


class GitHubRepoResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    repository: Repository
