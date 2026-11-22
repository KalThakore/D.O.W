# Degrees of Weird — prototype v0.1

An **unvalidated, expert-input decision-support tool**, not a predictive model. It scores potential brand extensions and compares them to a common hypothetical brand-permission profile. All brands and scenarios supplied in the app are fictional examples.

## Run locally

Requires Python 3.10+.

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

Open the local URL Streamlit prints (typically `http://localhost:8501`).

## Files

- `scoring_engine.py` — pure-Python formulas, dimension metadata, validation.
- `app.py` — Streamlit parent-brand input, editable scenario table, comparisons, diagnostics, CSV/JSON exports.
- `test_scoring_engine.py` — deterministic unit tests (`python -m unittest discover -v`).

## Core math

- Raw weirdness `W = 10 × sum(distance_i × weight_i)`; distance inputs 0–10.
- Permission `P = 10 × sum(permission_j × weight_j)`; permission inputs 0–10.
- Effective weirdness `W_eff = max(0, W − bridge)`; optional bridge 0–20 is an assumed, **unvalidated** scenario lever.
- Permission gap `G = W_eff − P`; positive implies beyond modeled permission.
- Qualitative bands are provisional: G > 15 = outside; 0 < G <= 15 = beyond; -15 <= G <= 0 = near; G < -15 = within.

Both scales are heuristic indexes and have **not** been empirically calibrated as commensurable. Output numbers are not actual degrees, success likelihoods, purchase probabilities, or forecasts. No data leaves your computer by default (assuming a local Streamlit process). Do not upload confidential client material into third-party hosting without authorization/security review.

## Next steps before using commercially

1. Define an anchored item-rating rubric with examples for each response level.
2. Measure parent brand associations separately from extension fit, with relevant respondents.
3. Randomize concepts and test brand-labeled vs brand-masked or control alternatives.
4. Fit coefficients and boundary criteria on training data, assess inter-rater reliability, and validate on holdout brands/concepts.
5. Add uncertainty intervals and separate demand/commercial attractiveness from stretch.
6. Resolve trademark availability, methodological IP ownership, and client research-data reuse rights.
