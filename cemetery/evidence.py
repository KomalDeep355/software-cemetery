"""Build a small evidence ledger from a fetched public GitHub snapshot."""


def build_evidence_ledger(snapshot, features):
    repository = snapshot["repository"]
    base_url = repository["url"].rstrip("/")
    entries = [
        ("E1", f"Repository: {repository['full_name']}", base_url),
        (
            "E2",
            f"Created: {repository.get('created_at') or 'unknown'}; language: {repository.get('language') or 'Unknown'}; description: {repository.get('description') or 'No description'}",
            base_url,
        ),
        ("E3", f"GitHub archived flag: {repository['archived']}", base_url),
        (
            "E4",
            "Days since last commit/push: "
            + str(features["days_since_last_commit"] if features["days_since_last_commit"] is not None else "unknown"),
            f"{base_url}/commits",
        ),
        ("E5", f"Stars: {features['stars']}; forks: {features['forks']}", base_url),
        ("E6", f"Open issue count: {features['open_issues_count']}", f"{base_url}/issues"),
        ("E8", f"Contributors observed in returned sample: {features.get('contributors_observed', 0)}", f"{base_url}/graphs/contributors"),
        (
            "E7",
            "Days since last published release: "
            + str(features["days_since_last_release"] if features["days_since_last_release"] is not None else "no release found"),
            f"{base_url}/releases",
        ),
    ]
    for number, issue in enumerate(snapshot.get("issues", [])[:6], 9):
        if issue.get("html_url"):
            entries.append((f"E{number}", f"Issue/PR title: {issue.get('title', 'untitled')} (state {issue.get('state', 'unknown')})", issue["html_url"]))
    return [{"id": evidence_id, "claim": claim, "url": url} for evidence_id, claim, url in entries]


# Compatibility alias for any code that used the original helper name.
evidence = build_evidence_ledger