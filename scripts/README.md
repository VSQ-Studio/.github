# Organization contribution calendar generator

`generate_org_contributions.py` enumerates the VSQ-Studio organization's public, non-fork repositories and aggregates commits visible on each repository's default branch. It writes light and dark SVG heatmaps into `OUTPUT_DIR`.

Environment variables: `ORG_NAME` (default `VSQ-Studio`), optional `ORG_READ_TOKEN`, `CALENDAR_DAYS` (default `365`), `OUTPUT_DIR` (default `dist`), and optional `GITHUB_API_URL` for GitHub Enterprise.

The generator does not require a maintainer username and does not read a personal contribution calendar. It counts commits only; it does not currently include Issues, Pull Requests, reviews, releases, or private repositories.
