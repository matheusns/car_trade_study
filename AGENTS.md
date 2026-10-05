# Repository Maintenance Contract

## Authoritative artifacts

This GitHub repository is the source of truth for the UAE car trade study.

The legacy Google Sheet is retired and must not be treated as authoritative, synchronized, or updated as part of normal maintenance.

## Vehicle addition / update workflow

For every request to add or revise a vehicle:

1. Update `cars.csv` in this repository.
2. Preserve the existing schema and 1–5 scoring semantics for all criteria.
3. Ground price, mileage, GCC status/specification, warranty/service context and market assertions in current UAE sources.
4. Store the primary source in `source_url` and concise decision evidence in `evidence`.
5. Set `powertrain` consistently (`ICE`, `HEV`, `PHEV`, or `EV`).
6. Set acquisition state consistently (`New`, `Used`, or `Market reference`).
7. Recompute normalized score/rank when candidate scores change or candidates are added.
8. Verify the Streamlit app loads the row and that the candidate is selectable in the comparison workflow.
9. Keep the comparison hard-capped at three vehicles unless the user explicitly changes that product requirement.
10. Commit the repository changes; do not update the obsolete spreadsheet.

## Scoring model

`criteria.json` defines the evaluation weights and rationale. Change it only when the user requests a scoring/criteria change. A vehicle-only addition normally requires changes to `cars.csv`, not `criteria.json`.

## UX contract

The web dashboard is the primary interface. New candidates must automatically appear in:

- filtering/exploration,
- the **All options** catalogue,
- candidate cards,
- the reusable per-vehicle detail modal,
- portfolio visualization,
- the up-to-3 comparison selector,
- criterion-by-criterion comparison,
- evidence/source display.

Avoid hardcoded candidate lists except for optional default selections.
