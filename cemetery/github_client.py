"""Small GitHub REST client with caching, retries and a one-call `snapshot()`.

`snapshot(repo)` is what the rest of the app (pipeline.inspect) depends on:
it returns the repository facts plus recent commits, issues/PRs, releases and
contributors in the exact shape that features.py and evidence.py expect.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from . import config

API = "https://api.github.com"
_NAME_RE = re.compile(r"^[A-Za-z0-9_.-]+$")


class GitHubError(RuntimeError):
    pass


class RateLimited(GitHubError):
    pass


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today_utc() -> datetime:
    """Midnight UTC today."""
    return datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )


def parse_repo(value: str) -> tuple[str, str]:
    """Turn 'owner/repo', a github.com URL, or git@github.com:owner/repo.git
    into (owner, repo). Raises ValueError with a friendly message."""
    text = (value or "").strip()
    text = text.replace("git@github.com:", "")
    text = re.sub(r"^(https?://)?(www\.)?github\.com/", "", text, flags=re.I)
    text = text.split("?")[0].split("#")[0].rstrip("/")
    text = re.sub(r"\.git$", "", text, flags=re.I)
    parts = [p for p in text.split("/") if p]
    if len(parts) < 2 or not _NAME_RE.match(parts[0]) or not _NAME_RE.match(parts[1]):
        raise ValueError(
            "Enter a repository as owner/repo (for example pallets/flask) "
            "or paste a public GitHub URL."
        )
    return parts[0], parts[1]


class GitHubClient:
    def __init__(
        self,
        token: str | None = None,
        cache_ttl_hours: float | None = None,
        max_wait: int = 90,
    ):
        self.token = config.GITHUB_TOKEN if token is None else token
        if cache_ttl_hours is None:
            self.cache_ttl = config.CACHE_TTL_SECONDS
        else:
            self.cache_ttl = cache_ttl_hours * 3600
        self.max_wait = max_wait
        self.calls = 0
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.github+json",
            "User-Agent": "software-cemetery",
            "X-GitHub-Api-Version": "2022-11-28",
        })
        if self.token:
            self.session.headers["Authorization"] = f"Bearer {self.token}"

    # ------------------------------------------------------------------ cache
    def _cache_path(self, path: str, params: dict | None) -> Path:
        raw = path + json.dumps(params or {}, sort_keys=True)
        digest = hashlib.sha1(raw.encode()).hexdigest()
        config.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        return config.CACHE_DIR / f"{digest}.json"

    def _read_cache(self, cache_path: Path):
        if not cache_path.exists():
            return None
        age = time.time() - cache_path.stat().st_mtime
        if age > self.cache_ttl:
            return None
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            return cached["data"], cached.get("link", "")
        except (OSError, ValueError, KeyError):
            return None

    def _write_cache(self, cache_path: Path, data: Any, link: str) -> None:
        try:
            cache_path.write_text(
                json.dumps({"data": data, "link": link}), encoding="utf-8"
            )
        except OSError:
            pass  # a read-only disk must never break an investigation

    # ----------------------------------------------------------- rate limits
    def _handle_limit(self, response: requests.Response) -> None:
        retry_after = response.headers.get("retry-after")
        remaining = response.headers.get("x-ratelimit-remaining")

        if retry_after:
            wait = int(retry_after) + 1
        elif remaining == "0":
            reset = int(response.headers.get("x-ratelimit-reset", "0"))
            wait = max(reset - time.time(), 0) + 2
        else:
            raise GitHubError(
                "GitHub denied the request. "
                f"HTTP {response.status_code}: {response.text[:200]}"
            )

        if wait > self.max_wait:
            raise RateLimited(
                "GitHub rate limit reached. "
                f"Try again in approximately {int(wait)} seconds, "
                "or configure a valid GITHUB_TOKEN in your .env file."
            )
        time.sleep(wait)

    def _send_request(self, url: str, params: dict | None, public_only: bool = False):
        headers = None
        if public_only and self.token:
            # Drop the session-level Authorization header for this request only.
            headers = {"Authorization": None}
        response = self.session.get(url, params=params, headers=headers, timeout=30)
        self.calls += 1
        return response

    def request(self, path: str, params: dict | None = None, use_cache: bool = True):
        """Return (data, link_header). Returns (None, "") for missing resources.
        Retries without auth when a configured token is rejected."""
        cache_path = self._cache_path(path, params)
        if use_cache:
            cached = self._read_cache(cache_path)
            if cached is not None:
                return cached

        url = path if path.startswith("http") else API + path
        last_error = None
        retried_without_auth = False

        for attempt in range(5):
            try:
                response = self._send_request(
                    url, params, public_only=retried_without_auth
                )
            except requests.RequestException as exc:
                last_error = exc
                time.sleep(2 ** attempt)
                continue

            if response.status_code == 401 and self.token and not retried_without_auth:
                retried_without_auth = True
                continue

            if response.status_code == 401:
                raise GitHubError(
                    "GitHub rejected authentication. Check GITHUB_TOKEN in your "
                    ".env file. Public access without a token also failed."
                )

            if response.status_code in (404, 451):
                return None, ""

            # 409 = empty repository, 204 = no content (e.g. contributors of an empty repo)
            if response.status_code in (409, 204):
                return [], ""

            if response.status_code in (403, 429):
                self._handle_limit(response)
                continue

            if response.status_code >= 500:
                last_error = f"GitHub server error: HTTP {response.status_code}"
                time.sleep(2 ** attempt)
                continue

            try:
                response.raise_for_status()
            except requests.HTTPError as exc:
                raise GitHubError(f"GitHub request failed: {exc}") from exc

            try:
                data = response.json()
            except ValueError as exc:
                raise GitHubError("GitHub returned an invalid JSON response.") from exc

            link = response.headers.get("Link", "")
            if use_cache:
                self._write_cache(cache_path, data, link)
            return data, link

        raise GitHubError(
            f"GitHub request failed after retries. Last error: {last_error or 'unknown error'}"
        )

    # --------------------------------------------------------------- helpers
    def get(self, path: str, params: dict | None = None):
        return self.request(path, params)[0]

    def paged(
        self,
        path: str,
        params: dict | None = None,
        max_pages: int = 3,
        per_page: int = 100,
    ) -> list:
        output: list = []
        for page in range(1, max_pages + 1):
            page_params = dict(params or {})
            page_params.update({"per_page": per_page, "page": page})
            data, _ = self.request(path, page_params)
            if not data:
                break
            if isinstance(data, dict):
                data = data.get("items", [])
            output.extend(data)
            if len(data) < per_page:
                break
        return output

    def count_via_link(self, path: str, params: dict | None = None) -> int:
        data, link = self.request(path, {**(params or {}), "per_page": 1})
        if data is None:
            return 0
        for part in link.split(","):
            if 'rel="last"' in part:
                match = re.search(r"[?&]page=(\d+)", part)
                if match:
                    return int(match.group(1))
        return len(data)

    def nth_item(self, path: str, n: int, params: dict | None = None):
        if n < 1:
            raise ValueError("n must be at least 1")
        data, _ = self.request(path, {**(params or {}), "per_page": 1, "page": n})
        return data[0] if data else None

    def _optional(self, path: str, params: dict | None = None, per_page: int = 100) -> list:
        """Fetch one page of a secondary endpoint. A failure here (for example
        GitHub refusing a contributors list for a huge repo) must not kill the
        whole investigation, but a real rate limit still has to surface."""
        try:
            return self.paged(path, params, max_pages=1, per_page=per_page)
        except RateLimited:
            raise
        except GitHubError:
            return []

    # -------------------------------------------------------------- snapshot
    def snapshot(self, repo: str) -> dict:
        """Collect everything one investigation needs (about 5 API calls)."""
        owner, name = parse_repo(repo)
        base = f"/repos/{owner}/{name}"

        info = self.get(base)
        if not info or not isinstance(info, dict):
            raise GitHubError(
                f"Repository '{owner}/{name}' was not found, is private, "
                "or is unavailable."
            )

        license_info = info.get("license") or {}
        repository = {
            "full_name": info.get("full_name") or f"{owner}/{name}",
            "name": info.get("name") or name,
            "owner": (info.get("owner") or {}).get("login") or owner,
            "url": info.get("html_url") or f"https://github.com/{owner}/{name}",
            "description": info.get("description"),
            "language": info.get("language"),
            "archived": bool(info.get("archived")),
            "stars": info.get("stargazers_count", 0) or 0,
            "forks": info.get("forks_count", 0) or 0,
            "open_issues_count": info.get("open_issues_count", 0) or 0,
            "created_at": info.get("created_at"),
            "pushed_at": info.get("pushed_at"),
            "default_branch": info.get("default_branch"),
            "license": license_info.get("spdx_id") or license_info.get("name"),
        }

        commits = self._optional(f"{base}/commits")
        issues = self._optional(
            f"{base}/issues",
            {"state": "all", "sort": "updated", "direction": "desc"},
            per_page=50,
        )
        releases = self._optional(f"{base}/releases", per_page=30)
        contributors = self._optional(f"{base}/contributors", per_page=30)

        return {
            "repository": repository,
            "commits": commits,
            "issues": issues,
            "releases": releases,
            "contributors": contributors,
        }