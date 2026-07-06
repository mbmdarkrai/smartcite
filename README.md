# SmartCite — Evidence Audit System for Scientific Writing

Not a reference manager. SmartCite checks whether a citation actually supports the claim it's attached to — flagging overclaiming, missing caveats, and weak evidence before a reviewer does.

> **Core promise:** Turn a manuscript from "well cited" into "well supported."

## What's in this folder

| File | Purpose |
|---|---|
| `smartcite.html` | Landing page (navy theme, matches the rest of the site) |
| `smartcite_app.py` | The actual Streamlit app — v1, claim–citation alignment checker |
| `requirements.txt` | Python dependencies (rename from `smartcite_app_requirements.txt` if needed) |

## What v1 does

1. Upload a manuscript (`.docx`)
2. It finds sentences containing a citation — `(Author, Year)` or `[1]` style
3. You pick one and paste the abstract of the paper it cites
4. Claude checks and returns:
   - **Alignment**: Supported / Partially Supported / Not Supported / Cannot Assess
   - **Overclaiming**: yes/no + why
   - **Missing caveats**: yes/no + what's missing (sample size, species, model system)
   - **Justification note**: ready to paste into a response-to-reviewers letter

## Not yet built (see roadmap)

- Automatic PDF parsing — right now you paste the abstract manually
- Comparative evidence matrix (methods/cohort/endpoints/limitations table across multiple papers)
- Zotero / BibTeX / CSL JSON import-export
- Versioned citation snapshots for coauthor reproducibility
- PRISMA-style screening for systematic reviews

## Running it locally

```bash
pip install -r requirements.txt
streamlit run smartcite_app.py
```

You'll need an Anthropic API key (console.anthropic.com) — paste it into the sidebar when the app opens. It's used only for that session and never saved.

## Deploying it properly

1. Push `smartcite_app.py` and `requirements.txt` to a GitHub repo.
2. Go to [share.streamlit.io](https://share.streamlit.io) → sign in with GitHub → **New app** → select the repo, branch, and `smartcite_app.py`.
3. Once deployed, add your API key under **App settings → Secrets**:
   ```toml
   ANTHROPIC_API_KEY = "sk-..."
   ```
4. You'll get a live URL like `https://smartcite-yourname.streamlit.app` — paste that into `smartcite.html`'s "Open SmartCite App" button, replacing the current placeholder `href="#"`.

## Git — from zero to pushed

```bash
git init
git add smartcite_app.py requirements.txt
git commit -m "Add SmartCite v1"
git branch -M main
git remote add origin https://github.com/yourusername/smartcite.git
git push -u origin main
```

## Scope note

SmartCite flags potential evidence-alignment issues for the author's own review. It does not replace peer review, editorial judgment, or the author's responsibility for the accuracy of their claims.
