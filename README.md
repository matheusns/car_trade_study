# Car Trade Study — UAE SUV Decision Dashboard

Repository-backed decision-support web app for comparing SUV purchase options in Abu Dhabi / UAE.

## Source of truth

This repository is now the **authoritative baseline** for the car trade study.

- `cars.csv` — vehicle candidates, prices, mileage, acquisition state, powertrain, evidence, per-criterion scores, normalized score and rank.
- `criteria.json` — weighted evaluation criteria and rationale.
- `app.py` — Streamlit UX that reads the repository data directly.

The previous Google Sheets trade study was used to seed the initial repository baseline and is now **obsolete**. Do not use it as an input for future vehicle additions or scoring updates.

## Updating the study

When a new vehicle/model/trim is requested:

1. Research the current UAE/GCC vehicle and market evidence.
2. Add or update the candidate in `cars.csv` with source URL, evidence, acquisition state, mileage, price and all 12 criterion scores.
3. Recalculate/validate the normalized score and rank consistently with the existing model.
4. Verify that the candidate appears correctly in the Streamlit catalogue and can be selected in the **Compare up to 3** view.
5. Commit the dataset/UI change to this repository.

See `AGENTS.md` for the repository maintenance contract.

## Current dashboard capabilities

- 37 SUV candidates in the initial repository baseline.
- UAE/GCC acquisition context, reference price, mileage and source link.
- 12-criterion weighted trade-study score with evidence notes.
- Filters for make, powertrain, acquisition state, price, mileage and minimum score.
- Price-vs-score portfolio visualization.
- Side-by-side comparison of **up to 3 vehicles**.
- Radar chart and criterion-by-criterion comparison.
- Criteria weights and scoring rationale.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python serve.py
```

Then open:

```text
http://localhost:8501
```

You can also run Streamlit directly:

```bash
streamlit run app.py
```

## Decision assumptions

The current baseline assumes:

- Abu Dhabi / UAE purchase context.
- GCC-spec vehicles.
- New or recent used vehicles within the existing age/mileage gate.
- 20,000 km/year.
- 5-year ownership horizon.
- Fuel reference: AED 3.69/L.
- Public AC EV charging: AED 0.735/kWh.
- Public DC EV charging: AED 1.26/kWh.

Prices, promotions and listing availability are time-sensitive. Reconfirm executable price, GCC/VIN status, first-registration date, service history, warranty transfer, and EV/PHEV battery/charging condition before purchase.

Financing economics are not yet included in the weighted score.
