from datetime import datetime, timezone
from .github_client import GitHubClient
from .features import features
from .vitality import assess_vitality
from .evidence import build_evidence_ledger
from .epitaph import write_epitaph, verify

def inspect(repo,use_llm=False,client=None):
    snapshot=(client or GitHubClient()).snapshot(repo); f=features(snapshot); a=assess_vitality(f); ev=build_evidence_ledger(snapshot,f)
    story=write_epitaph(snapshot,ev,use_llm=use_llm,assessment=a,features_data=f)
    return {"repository":snapshot["repository"],"features":f,"assessment":a,"evidence":ev,"story":story,"citation_check":verify(story["text"],ev),"generated_at":datetime.now(timezone.utc).isoformat(),"data_scope":"Public GitHub REST API snapshot; recent returned samples, not a complete repository history."}
