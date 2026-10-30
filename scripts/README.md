# Organization contribution calendar generator

This script builds two GitHub-style SVG contribution heatmaps for the `VSQ-Studio` organization.

## Data source

- Lists public repositories owned by `VSQ-Studio`.
- Excludes Fork repositories and the `.github` meta repository (the latter receives automated calendar asset commits).
- Reads commit history from each repository's default branch for the previous 365 UTC dates.
- Counts one commit per repository commit record and renders separate dark/light SVG themes.
- Does not use any maintainer's personal contribution calendar.

## Run locally

```bash
python3 scripts/generate_org_contributions.py
```

By default, output is written to `profile/assets/`. Override with `OUTPUT_DIR` when needed.

A fine-grained GitHub token with public repository metadata read access may be supplied through `ORG_READ_TOKEN` to avoid unauthenticated API rate limits. The generator intentionally fails on API rate-limit or permission errors rather than publishing incomplete data.
