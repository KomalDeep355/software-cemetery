import re, requests
from .config import OLLAMA_URL, OLLAMA_MODEL

def story_template(s, f, assessment):
    """Write a funny, kind repository life story using only the fetched record."""
    r = s["repository"]
    age = f.get("days_since_last_commit")
    name = r["full_name"]
    stars = f.get("stars", 0)
    created = (r.get("created_at") or "")[:10] or "an unknown date"
    description = r.get("description") or "No public description was left behind."
    if r.get("archived"):
        opening = f"The file opens with a plot twist: {name} is explicitly marked archived on GitHub [E1] [E3]. The digital groundskeeper has at least labelled the plot."
    elif age is None:
        opening = f"The records for {name} are foggy; the archivist refuses to invent a last-seen date just to make the story more dramatic [E1] [E4]."
    elif age > 730:
        opening = f"Once pushed with purpose, {name} has been quiet for {age} days. Somewhere, a TODO comment has probably renewed its lease [E1] [E4]."
    elif age > 365:
        opening = f"{name} has been quiet for {age} days: not declared dead, just not exactly answering the pager [E1] [E4]."
    elif age > 180:
        opening = f"{name} may be in its legendary 'I'll refactor it this weekend' era, with {age} days since its last recorded push [E1] [E4]."
    else:
        opening = f"Plot twist: {name} still shows signs of life, with its latest recorded push only {age} days ago [E1] [E4]. The cemetery may have to return the flowers."
    lang = r.get("language") or "mystery language"
    release = f.get("days_since_last_release")
    release_line = ("No published release appeared in the fetched sample; the release manager may have gone to get snacks [E7]."
                    if release is None else f"The latest release in the fetched sample was {release} days ago [E7].")
    support = f"The public record lists {stars:,} stars and {f.get('forks', 0):,} forks, which is a respectable number of digital bookmarks [E5]."
    origin = f"The repository was created on {created} and describes itself this way: {description} [E1] [E2]."
    build_line = f"Written in {lang}, its public record preserves commits, issues, releases, and the familiar human optimism of a project folder named something more ambitious than 'weekend-test' [E2] [E6]."
    verdict = f"The current vitality estimate is {assessment.get('score', 'unknown')}/100 ({assessment.get('label', 'unknown')}). That is a transparent heuristic about visible signals, not a personality test for maintainers [E3] [E4] [E7]."
    ending = "A respectful next chapter: read the latest issues, check the contribution guide, and ask whether maintenance help is welcome. Stable software can be quiet; silence alone is not a cause of death."
    return " ".join([opening, origin, build_line, support, release_line, verdict, ending])

def write_epitaph(s,ev,use_llm=False,assessment=None,features_data=None):
    f=features_data or {}; assessment=assessment or {"score":0,"label":"Unknown"}; fallback=story_template(s,f,assessment)
    if not use_llm:return {"text":fallback,"model":"evidence-linked story template","used_local_llm":False}
    prompt = (
        "Write a nostalgic, witty, kind, lightly sarcastic 140-200 word open-source repository life story/epitaph. "
        "Give the repo a small narrative arc: what the project says it is for, the public traces it left, the current activity signal, "
        "and a possible respectful next chapter. The tone should feel like a FOSS maintainer wrote a lovingly dramatic memorial in an old terminal archive. "
        "Use only facts in the evidence below; never invent author intentions, project users, impact, dates, causes, or events. "
        "Put [E#] citations immediately after factual claims. Clearly say that inactivity is not proof of abandonment. "
        "End with a practical revival suggestion. Plain text only.\n\n"
        "REPOSITORY AND METRICS:\n" + str(s["repository"]) + "\n\n"
        "FEATURES:\n" + str(f) + "\n\n"
        "ASSESSMENT:\n" + str(assessment) + "\n\n"
        "EVIDENCE:\n" + str(ev)
    )
    try:
        resp=requests.post(OLLAMA_URL+"/api/generate",json={"model":OLLAMA_MODEL,"prompt":prompt,"stream":False,"options":{"temperature":0.65}},timeout=90); resp.raise_for_status(); txt=resp.json().get("response","").strip()
        if len(txt)<50: raise ValueError("Model returned too little text")
        return {"text":txt,"model":OLLAMA_MODEL,"used_local_llm":True}
    except (requests.RequestException,ValueError,KeyError) as e:
        return {"text":fallback,"model":"evidence-linked story template","used_local_llm":False,"note":str(e)}

def verify(text,ev):
    known={x["id"] for x in ev}; found=re.findall(r"\[(E\d+)\]",text)
    return {"citation_ids_found":found,"unknown_citation_ids":sorted(set(found)-known),"warning":"Citation markers are not semantic verification; manually check that every cited source supports the claim."}
