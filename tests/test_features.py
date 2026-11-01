from datetime import datetime,timezone
from cemetery.features import features,assess

def test_features_recent_commit():
    now=datetime(2026,10,29,tzinfo=timezone.utc)
    s={"repository":{"stars":4,"forks":1,"archived":False,"open_issues_count":0},
       "commits":[{"commit":{"author":{"date":"2026-10-20T00:00:00Z","name":"A"}},"author":{"login":"a"}}],
       "issues":[],"releases":[]}
    f=features(s,now)
    assert f["days_since_last_commit"]==9
    assert assess(f)["label"]=="Recently active"

def test_archived():
    assert assess({"archived":1,"days_since_last_commit":2})["label"]=="Archived"
