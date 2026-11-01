from datetime import datetime, timezone
from collections import Counter
from statistics import median

def dt(s):
    try: return datetime.fromisoformat(s.replace("Z","+00:00")) if s else None
    except (ValueError,AttributeError): return None

def days_ago(s,now=None):
    d=dt(s)
    if not d:return None
    now=now or datetime.now(timezone.utc)
    if d.tzinfo is None:d=d.replace(tzinfo=timezone.utc)
    return max(0,(now-d).days)

def features(s,now=None):
    now=now or datetime.now(timezone.utc); r=s["repository"]; commits=s.get("commits",[]); dates=[]; authors=[]
    for c in commits:
        ci=c.get("commit") or {}; a=ci.get("author") or ci.get("committer") or {}; d=dt(a.get("date"))
        if d: dates.append(d)
        who=(c.get("author") or {}).get("login") or a.get("email") or a.get("name")
        if who: authors.append(who)
    issues=[i for i in s.get("issues",[]) if "pull_request" not in i]; prs=[i for i in s.get("issues",[]) if "pull_request" in i]
    closed=[i for i in issues if i.get("state")=="closed"]; durations=[]
    for i in closed:
        a,b=dt(i.get("created_at")),dt(i.get("closed_at"))
        if a and b: durations.append(max(0,(b-a).total_seconds()/86400))
    releases=[x for x in s.get("releases",[]) if x.get("published_at") and not x.get("draft")]
    last_commit=max(dates) if dates else dt(r.get("pushed_at"))
    last_release=max((dt(x["published_at"]) for x in releases),default=None)
    author_counts=Counter(authors)
    return {"stars":int(r.get("stars",0)),"forks":int(r.get("forks",0)),"archived":bool(r.get("archived",False)),"open_issues_count":int(r.get("open_issues_count",0)),"commits_returned":len(commits),"days_since_last_commit":days_ago(last_commit.isoformat() if last_commit else None,now),"contributors_observed":len(set(authors)) or len(s.get("contributors",[])),"top_author_share":max(author_counts.values())/len(authors) if authors else 0,"issues_returned":len(issues),"issues_closed_returned":len(closed),"median_issue_close_days":round(median(durations),1) if durations else None,"prs_returned":len(prs),"prs_merged_returned":sum(bool((p.get("pull_request") or {}).get("merged_at")) for p in prs),"releases_returned":len(releases),"days_since_last_release":days_ago(last_release.isoformat() if last_release else None,now)}

def assess(f):
    age=f.get("days_since_last_commit")
    if f["archived"]: label="Archived"
    elif age is None: label="Unknown activity"
    elif age>730: label="Very quiet"
    elif age>365: label="Quiet"
    elif age>180: label="Cooling down"
    else: label="Recently active"
    # Transparent heuristic; archived status is not treated as proof of abandonment.
    score=100
    if age is None: score-=25
    elif age>730: score-=48
    elif age>365: score-=35
    elif age>180: score-=20
    elif age>90: score-=10
    release_age=f.get("days_since_last_release")
    contributors=f.get("contributors_observed", 0)
    top_author_share=f.get("top_author_share", 0)
    if release_age is None: score-=8
    elif release_age>730: score-=12
    elif release_age>365: score-=6
    if contributors<=1: score-=12
    if top_author_share>=.85 and contributors>1: score-=8
    if f.get("archived", False): score=min(score,35)
    score=max(0,min(100,score))
    reasons=[]
    reasons.append(f"Last known push/commit: {age} days ago." if age is not None else "No commit timestamp was available in the fetched sample.")
    reasons.append("Repository is explicitly archived on GitHub." if f.get("archived", False) else "GitHub does not mark this repository as archived.")
    reasons.append(f"{contributors} contributors observed in the available sample.")
    reasons.append("No published release was found in the fetched release sample." if release_age is None else f"Last published release: {release_age} days ago.")
    return {"label":label,"score":score,"reasons":reasons,"disclaimer":"Heuristic vitality estimate, not a prediction of maintainer intent and not proof of abandonment. GitHub's returned samples may be incomplete."}
