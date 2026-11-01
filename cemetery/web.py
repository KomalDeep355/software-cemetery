import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from .github_client import GitHubError
from .pipeline import inspect

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(
    title="The Software Cemetery",
    version="2.1.0",
    description="An evidence-backed, nostalgic FOSS repository archive.",
)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


class InspectRequest(BaseModel):
    repo: str = Field(min_length=3, max_length=300)
    use_llm: bool = False


class CompareRequest(BaseModel):
    repos: list[str] = Field(min_length=2, max_length=5)
    use_llm: bool = False


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@app.get("/api/health")
def health():
    return {"status": "ok", "app": "The Software Cemetery", "version": "2.1.0"}


@app.post("/api/inspect")
def inspect_api(payload: InspectRequest):
    try:
        return inspect(payload.repo, payload.use_llm)
    except (GitHubError, ValueError) as exc:
        logger.exception("Repository inspection failed: %s", payload.repo)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception(
            "Unexpected inspection failure for repository: %s",
            payload.repo,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Inspection failed: {type(exc).__name__}: {exc}",
        ) from exc


@app.post("/api/compare")
def compare_api(payload: CompareRequest):
    results = []
    for repo in payload.repos:
        try:
            item = inspect(repo, payload.use_llm)
            results.append({
                "ok": True,
                "repo": item["repository"]["full_name"],
                "url": item["repository"]["url"],
                "score": item["assessment"]["score"],
                "label": item["assessment"]["label"],
                "days_since_last_commit": item["features"]["days_since_last_commit"],
                "archived": item["features"]["archived"],
            })
        except Exception as exc:
            results.append({"ok": False, "repo": repo, "error": str(exc)})
    return {"results": results}


@app.get("/api/export/{owner}/{repo}")
def export_api(owner: str, repo: str):
    try:
        item = inspect(f"{owner}/{repo}", False)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    repository = item["repository"]
    assessment = item["assessment"]
    lines = [
        f"# The Software Cemetery: {repository['full_name']}",
        "",
        f"- Repository: {repository['url']}",
        f"- Generated: {item['generated_at']}",
        f"- Vitality score: {assessment['score']}/100 ({assessment['label']})",
        "",
        "## Life story",
        item["story"]["text"],
        "",
        "## Signals",
        *[f"- {reason}" for reason in assessment["reasons"]],
        "",
        "## Evidence",
        *[f"- **{evidence['id']}** {evidence['claim']} — {evidence['url']}" for evidence in item["evidence"]],
        "",
        "## Caveat",
        assessment["disclaimer"],
        "",
    ]
    safe_owner = "".join(c for c in owner if c.isalnum() or c in "-_")
    safe_repo = "".join(c for c in repo if c.isalnum() or c in "-_.")
    return Response(
        "\n".join(lines),
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{safe_owner}-{safe_repo}-cemetery.md"'},
    )
