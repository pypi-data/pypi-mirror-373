import os
import re
from typing import Self

from gql import Client, GraphQLRequest
from gql.transport.aiohttp import AIOHTTPTransport
from pydantic import BaseModel
from rich.console import Console

from . import GH_COMMENT_READER_BASE_DIR
from .models import GitHubRepoResponse, ParsedComment

console = Console()

GITHUB_PR_URL_PATTERN = re.compile(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)")
GITHUB_GRAPHQL_API_URL = "https://api.github.com/graphql"


class GitHubPRComments(BaseModel):
    comments: list[ParsedComment]

    @classmethod
    def from_github_pr(cls, pr_url: str) -> Self:
        if not (pr_url_match := GITHUB_PR_URL_PATTERN.search(pr_url)):
            raise ValueError(f"Invalid GitHub PR URL: {pr_url}")

        owner, repo, pr_number = pr_url_match.groups()

        with (GH_COMMENT_READER_BASE_DIR / "pr_comments.gql").open() as f:
            query = f.read()

        with console.status(f"[bold green]Fetching comments from PR #{pr_number}..."):
            auth_token = os.getenv("GITHUB_TOKEN")
            if not auth_token:
                console.print(
                    "[yellow]Warning: No GitHub token provided. API calls will "
                    "be rate limited.[/yellow]"
                )

            headers = {}
            if auth_token:
                headers["Authorization"] = f"Bearer {auth_token}"

            transport = AIOHTTPTransport(url=GITHUB_GRAPHQL_API_URL, headers=headers)
            client = Client(transport=transport, fetch_schema_from_transport=False)

            request = GraphQLRequest(
                query,
                variable_values={
                    "owner": owner,
                    "repo": repo,
                    "prNumber": int(pr_number),
                },
            )

            cursor = None
            all_review_threads = []
            while True:
                request.variable_values["cursor"] = cursor
                repository = GitHubRepoResponse(**client.execute(request)).repository
                review_threads = repository.pull_request.review_threads
                all_review_threads.extend(review_threads.nodes)

                if not review_threads.page_info.has_next_page:
                    break

                cursor = review_threads.page_info.end_cursor

            repository.pull_request.review_threads.nodes = all_review_threads

            parsed_comments = []
            for thread in repository.pull_request.review_threads.nodes:
                for comment in thread.comments.nodes:
                    parsed_comments.append(
                        ParsedComment(
                            url=comment.url,
                            body=comment.body,
                            body_text=comment.body_text,
                            is_outdated=comment.outdated,
                            is_minimized=comment.is_minimized,
                            minimized_reason=comment.minimized_reason,
                            is_resolved=thread.is_resolved,
                            resolved_by=thread.resolved_by.login if thread.resolved_by else None,
                            path=comment.path,
                            line=comment.line,
                            commit=comment.commit.abbreviated_oid if comment.commit else None,
                            author=comment.author.login if comment.author else None,
                            is_bot=comment.author.is_bot if comment.author else False,
                            created_at=comment.created_at,
                            updated_at=comment.updated_at,
                        )
                    )

            parsed_comments.sort(key=lambda c: c.created_at)
            return cls(comments=parsed_comments)
