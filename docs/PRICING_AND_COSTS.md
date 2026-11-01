# Pricing and operating cost categories

This is a planning document, not a price quote. Check provider pricing and free-tier limits before deployment.

## Hackathon operating budget

| Category | Initial plan | Possible future cost |
|---|---|---|
| GitHub data | Public REST API; optional token in `.env` | Higher-rate access may require authentication; respect rate limits |
| Local AI | Ollama + a locally downloaded model | Hardware, electricity, or a machine to host it |
| Frontend hosting | Free static hosting or same FastAPI service | Paid hosting for traffic or custom requirements |
| Backend hosting | Local laptop for demo | Paid compute, memory, and uptime |
| Persistent storage | Browser local storage and JSON files | Hosted database, backups, retention |
| Hosted AI | Not required | Token-based inference costs |
| Domain | Not required | Annual domain renewal |
| Monitoring | Basic logs | Paid error tracking/observability at scale |

## Hypothetical product tiers shown in the UI

These are unvalidated concept prices. No billing or subscription enforcement exists.

- **Graveyard — $0:** basic investigations, evidence links, vitality score, and story.
- **Archivist — $5/month proposed:** higher investigation allowance, saved snapshots, trends, batch exports.
- **Conservatory — $19/month proposed:** shared watchlists, maintenance alerts, scheduled scans, team reports.
- **Research — custom:** bulk analysis, API access, configurable retention, research exports.

Before charging for a product, estimate per-repository GitHub API use, model inference, storage, hosting, support, taxes, and abuse prevention. Do not present these illustrative amounts as an active offer.
