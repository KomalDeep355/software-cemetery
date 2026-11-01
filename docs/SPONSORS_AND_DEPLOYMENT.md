# Sponsor and deployment checklist

Verify current challenge rules before relying on any prize category.

- **Gemma / Ollama:** optional local model support is available. Record the exact model tag and show a real generation if claiming use.
- **Prior Labs / TabPFN:** optional experiment only; no trained TabPFN model or result is included. Do not claim use unless you actually run and evaluate it.
- **Render:** build command `pip install -r requirements.txt`; start command `uvicorn cemetery.web:app --host 0.0.0.0 --port $PORT`. Add `GITHUB_TOKEN` as a protected environment variable if appropriate. The service needs writable storage for its response cache; confirm that behavior on your chosen host.
- **DigitalOcean / other hosts:** configure a Python web service, the start command above, and required environment variables. Do not assume a local Ollama service is available in cloud hosting.
- **.tech domain / Entire / Sentry / Tinker:** integrate only if the offer is available, current rules permit it, and the tool is genuinely used. Tinker/fine-tuning is not implemented.
- **Cost:** the UI's product tiers are concepts only. No payments, subscriptions, or plan enforcement exist.
- Do not add unrelated sponsor tools just to name-drop them. Keep the project stable and the write-up honest.

Before submission, verify all current sponsor rules, document what was actually used, and capture screenshots/video of a real successful investigation as well as the synthetic sample case.
