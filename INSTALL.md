# VSQ Studio Organization Profile

## Deploy
This package is designed for the special GitHub organization profile repository:

`https://github.com/VSQ-Studio/.github`

1. Create or open the public `.github` repository under the VSQ-Studio organization.
2. Copy `README.md`, `README.en.md`, `CONTRIBUTING.md`, and the `assets/` directory into the repository root / matching paths.
3. Ensure the banner URL in both READMEs points to `https://raw.githubusercontent.com/VSQ-Studio/.github/main/profile/assets/vsq-pixel-banner.svg`. If you store assets at repository root instead, update that URL accordingly.
4. Put the Chinese `README.md` at `.github/profile/README.md` (create `profile/` if needed). GitHub displays this file as the organization profile.
5. Keep `README.en.md` beside it as the English alternative. The language switch links assume both files are in the same directory.
6. Put `CONTRIBUTING.md` at the repository root, or adjust the link in the README if you store it elsewhere.

## Important: assets path
For the special organization profile, the recommended structure is:

```text
.github/
├── profile/
│   ├── README.md
│   └── README.en.md
├── assets/
│   ├── vsq-pixel-banner.svg
│   ├── vsq-logo-black.png
│   └── vsq-logo-white.png
└── CONTRIBUTING.md
```

The banner in this package references `profile/assets/` in the raw URL. For the recommended structure above, change the two README banner image URLs to:

`https://raw.githubusercontent.com/VSQ-Studio/.github/main/assets/vsq-pixel-banner.svg`

Alternatively, put the assets directory inside `profile/` to keep the README image URL unchanged.

## Customization
- Edit the Chinese and English copy independently; keep section anchors and language links aligned.
- Contributor image panels currently cover the six public repositories visible on the organization page. Add or remove panels as repositories change.
- Activity graph and contributor images are third-party dynamic embeds. Their availability, cache, rate limits, and support for organization accounts are controlled by those services.
- The GitHub activity page link is a reliable fallback if an external chart is unavailable.
- Uploaded logos are preserved as supplied: black mark (`vsq-logo-black.png`) and white mark (`vsq-logo-white.png`).
