# Changelog

## Nostalgic archive upgrade

- Rebuilt the frontend as a responsive FOSS/CRT-inspired archive with phosphor-green styling, pixel-art memorial garden, scanline treatment, animated ticker, responsive layout, and accessible navigation labels.
- Added a persistent sidebar linking to Home, Investigate, Case File, Case Explorer, Compare, Method, Pricing Concepts, and About.
- Added the floating “How may I help you?” archivist helper with quick FAQ prompts and simple text-question routing.
- Added an explicitly synthetic sample case for demos that do not have a GitHub token or internet access.
- Added live repository inspection, evidence ledger, transparent score display, story panel, Markdown export link, and error/loading states.
- Added repository comparison for two to five repositories.
- Added a browser-local case explorer with filtering and a clear-local-archive control.
- Added clearly labelled hypothetical product pricing tiers and a separate operating-cost guide; no payment processing is implemented.
- Added benchmark evaluation CLI for manually reviewed labels, plus evidence/vitality module entry points and tests.
- Improved story narrative to include repository purpose/context, public activity traces, light FOSS humor, and a respectful next step while avoiding invented maintainer motives.
- Fixed the Markdown export newline handling and made vitality assessment tolerant of partial feature dictionaries.

## Validation performed

- Python syntax compilation passed.
- JavaScript syntax check passed.
- Automated test suite passed: 6 tests.
- FastAPI smoke check passed for `/`, `/api/health`, `/static/cemetery.css`, and `/static/cemetery.js` using TestClient.
- Live GitHub calls and live Ollama generation were not exercised as part of packaging validation.
