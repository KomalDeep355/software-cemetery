import pytest

from cemetery.github_client import GitHubClient, GitHubError, parse_repo


@pytest.mark.parametrize(
    "value",
    [
        "pallets/flask",
        "https://github.com/pallets/flask",
        "http://www.github.com/pallets/flask/",
        "https://github.com/pallets/flask.git",
        "https://github.com/pallets/flask/issues?q=is%3Aopen",
        "git@github.com:pallets/flask.git",
        "  pallets/flask  ",
    ],
)
def test_parse_repo_accepts_common_forms(value):
    assert parse_repo(value) == ("pallets", "flask")


@pytest.mark.parametrize("value", ["", "flask", "pallets/", "a b/c", "///"])
def test_parse_repo_rejects_bad_input(value):
    with pytest.raises(ValueError):
        parse_repo(value)


class OfflineClient(GitHubClient):
    """GitHubClient whose HTTP layer is replaced by canned data."""

    def __init__(self, responses):
        super().__init__(token="")
        self.responses = responses

    def request(self, path, params=None, use_cache=True):
        for suffix, data in self.responses.items():
            if path.endswith(suffix):
                return data, ""
        return None, ""


def test_snapshot_has_the_shape_the_pipeline_needs():
    client = OfflineClient({
        "/repos/o/r": {
            "full_name": "o/r", "name": "r", "owner": {"login": "o"},
            "html_url": "https://github.com/o/r", "description": "d",
            "language": None, "archived": True, "stargazers_count": 5,
            "forks_count": 2, "open_issues_count": 1,
            "created_at": "2020-01-01T00:00:00Z", "pushed_at": "2021-01-01T00:00:00Z",
            "license": {"spdx_id": "MIT"},
        },
        "/commits": [{"commit": {"author": {"date": "2021-01-01T00:00:00Z"}}}],
        "/issues": [],
        "/releases": [],
        "/contributors": [],
    })
    snap = client.snapshot("https://github.com/o/r")
    assert snap["repository"]["stars"] == 5
    assert snap["repository"]["archived"] is True
    assert snap["repository"]["license"] == "MIT"
    assert len(snap["commits"]) == 1
    for key in ("issues", "releases", "contributors"):
        assert snap[key] == []


def test_snapshot_raises_friendly_error_for_missing_repo():
    with pytest.raises(GitHubError):
        OfflineClient({}).snapshot("nobody/nothing")