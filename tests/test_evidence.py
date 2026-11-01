from cemetery.evidence import build_evidence_ledger


def test_evidence_ledger_has_links_for_score_signals():
    snapshot = {
        "repository": {
            "full_name": "sample/repo",
            "url": "https://github.com/sample/repo",
            "created_at": "2020-01-01T00:00:00Z",
            "language": "Python",
            "description": "A sample project",
            "archived": False,
        },
        "issues": [{"title": "A question", "state": "open", "html_url": "https://github.com/sample/repo/issues/1"}],
    }
    features = {
        "stars": 10,
        "forks": 2,
        "open_issues_count": 1,
        "days_since_last_commit": 20,
        "days_since_last_release": 60,
        "contributors_observed": 3,
    }
    ledger = build_evidence_ledger(snapshot, features)
    ids = [entry["id"] for entry in ledger]
    assert "E8" in ids
    assert len(ids) == len(set(ids))
    assert all(entry["url"].startswith("https://") for entry in ledger)
