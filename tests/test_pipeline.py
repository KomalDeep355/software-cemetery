from cemetery.pipeline import inspect


class FakeGitHubClient:
    def snapshot(self, _repo):
        return {
            "repository": {
                "full_name": "example/quiet-project",
                "url": "https://github.com/example/quiet-project",
                "description": "A tiny example package.",
                "archived": False,
                "stars": 23,
                "forks": 4,
                "open_issues_count": 1,
                "pushed_at": "2020-01-01T00:00:00Z",
                "created_at": "2019-01-01T00:00:00Z",
                "language": "Python",
                "license": "MIT",
            },
            "commits": [{"commit": {"author": {"date": "2020-01-01T00:00:00Z", "name": "A"}}, "author": {"login": "a"}}],
            "issues": [{"title": "Question", "state": "open", "html_url": "https://github.com/example/quiet-project/issues/1"}],
            "releases": [],
            "contributors": [],
        }


def test_pipeline_returns_story_and_linked_evidence_without_network():
    result = inspect("example/quiet-project", client=FakeGitHubClient())
    assert result["repository"]["full_name"] == "example/quiet-project"
    assert result["assessment"]["score"] >= 0
    assert result["story"]["text"]
    assert result["evidence"]
    assert result["citation_check"]["unknown_citation_ids"] == []
    assert result["data_scope"].startswith("Public GitHub REST API snapshot")
