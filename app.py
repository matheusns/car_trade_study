
from pathlib import Path
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

BASE = Path(__file__).resolve().parent

st.set_page_config(
    page_title="UAE SUV Decision Dashboard",
    page_icon="🚙",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .block-container {padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1500px;}

      /* Theme-aware surfaces: do not hard-code light backgrounds because
         Streamlit can render the app in either light or dark mode. */
      [data-testid="stSidebar"] {
        background: var(--secondary-background-color);
        color: var(--text-color);
      }
      [data-testid="stSidebar"] label,
      [data-testid="stSidebar"] p,
      [data-testid="stSidebar"] h1,
      [data-testid="stSidebar"] h2,
      [data-testid="stSidebar"] h3 {
        color: var(--text-color) !important;
      }

      .hero {
        padding: 1.35rem 1.5rem;
        border: 1px solid rgba(148, 163, 184, .45);
        border-radius: 18px;
        background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
        color: white;
        margin-bottom: 1rem;
      }
      .hero h1 {margin: 0; font-size: 2rem; line-height: 1.2; color: white;}
      .hero p {margin: .55rem 0 0; color: #dbeafe;}
      .eyebrow {font-size: .76rem; letter-spacing: .08em; text-transform: uppercase; opacity: .85;}

      .vehicle-card {
        border: 1px solid rgba(148, 163, 184, .32);
        border-radius: 16px;
        padding: 1rem;
        background: var(--secondary-background-color);
        color: var(--text-color);
        min-height: 230px;
        margin-bottom: .8rem;
      }
      .vehicle-card h3 {
        margin: 0 0 .25rem 0;
        font-size: 1.05rem;
        color: var(--text-color);
      }
      .muted {
        color: var(--text-color);
        opacity: .68;
        font-size: .88rem;
      }
      .pill {
        display: inline-block;
        border-radius: 999px;
        padding: .2rem .55rem;
        margin: .2rem .15rem .15rem 0;
        background: color-mix(in srgb, var(--primary-color) 16%, var(--secondary-background-color));
        border: 1px solid color-mix(in srgb, var(--primary-color) 38%, transparent);
        color: var(--text-color);
        font-size: .74rem;
        font-weight: 600;
      }
      .score {
        font-size: 1.65rem;
        font-weight: 700;
        color: var(--text-color);
      }
      .small-note {
        border-left: 4px solid rgba(148, 163, 184, .55);
        padding: .55rem .8rem;
        color: var(--text-color);
        background: var(--secondary-background-color);
        border-radius: 0 10px 10px 0;
      }
      .compare-title {
        font-size: .92rem;
        color: var(--text-color);
        opacity: .68;
        margin-bottom: .15rem;
      }

      div[data-testid="stMetric"] {
        border: 1px solid rgba(148, 163, 184, .32);
        padding: .7rem .8rem;
        border-radius: 14px;
        background: var(--secondary-background-color);
        color: var(--text-color);
      }
      [data-testid="stMetricLabel"],
      [data-testid="stMetricValue"] {
        color: var(--text-color) !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data
def load_data():
    cars = pd.read_csv(BASE / "cars.csv")
    criteria = pd.DataFrame(json.loads((BASE / "criteria.json").read_text(encoding="utf-8")))
    return cars, criteria

cars, criteria = load_data()
criterion_names = criteria["name"].tolist()

def fmt_aed(v):
    return f"AED {float(v):,.0f}"

def fmt_km(v):
    return "0 km" if float(v) == 0 else f"{float(v):,.0f} km"

def safe_year(v):
    return str(v).replace(".0","")

@st.dialog("Vehicle details", width="large")
def show_vehicle_details(car_id):
    match = cars[cars["id"] == car_id]
    if match.empty:
        st.error("Vehicle not found in the current repository dataset.")
        return

    row = match.iloc[0]

    st.markdown(f"## {row['candidate']}")
    st.caption(f"{safe_year(row['model_year'])} · {row['model_trim']} · {row['acquisition']}")
    st.markdown(
        f"""
        <span class="pill">{row['powertrain']}</span>
        <span class="pill">{row['state']}</span>
        <span class="pill">{row['status']}</span>
        """,
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Reference price", fmt_aed(row["price_aed"]))
    m2.metric("Mileage", fmt_km(row["mileage_km"]))
    m3.metric("Trade-study score", f"{row['score_pct']:.1f}/100")
    m4.metric("Rank", f"#{int(row['rank'])}")

    st.markdown("### Decision evidence")
    st.write(row["evidence"])

    st.markdown("### Criterion breakdown")
    detail = criteria[["name", "weight_pct"]].copy()
    detail["score"] = [float(row[name]) for name in detail["name"]]
    detail["weighted_points"] = detail["score"] * detail["weight_pct"] / 5.0

    chart_data = detail.sort_values("score", ascending=True)
    detail_fig = px.bar(
        chart_data,
        x="score",
        y="name",
        orientation="h",
        text="score",
        range_x=[0, 5],
        labels={"score": "Score (1–5)", "name": ""},
        height=470,
    )
    detail_fig.update_traces(texttemplate="%{text:.0f}", textposition="outside")
    detail_fig.update_layout(margin=dict(l=10, r=30, t=10, b=10))
    st.plotly_chart(detail_fig, use_container_width=True)

    st.dataframe(
        detail.rename(
            columns={
                "name": "Criterion",
                "weight_pct": "Weight (%)",
                "score": "Score (1–5)",
                "weighted_points": "Weighted points",
            }
        ),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Weight (%)": st.column_config.NumberColumn(format="%.2f%%"),
            "Score (1–5)": st.column_config.ProgressColumn(
                min_value=0,
                max_value=5,
                format="%.0f",
            ),
            "Weighted points": st.column_config.NumberColumn(format="%.2f"),
        },
    )

    st.markdown("### Source & diligence")
    st.write(
        f"**Acquisition:** {row['acquisition']}  \\n"
        f"**Status:** {row['status']}  \\n"
        f"**Powertrain:** {row['powertrain']}"
    )
    st.link_button("Open source / listing", row["source_url"], use_container_width=True)

st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">Carro UAE · decision support</div>
      <h1>UAE SUV Decision Dashboard</h1>
      <p>Abu Dhabi purchase study · GCC-spec focus · new or recent used SUVs · transparent 1–5 weighted scoring</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Filter candidates")
    selected_makes = st.multiselect("Make", sorted(cars["make"].unique()))
    selected_power = st.multiselect("Powertrain", ["ICE", "HEV", "PHEV", "EV"])
    selected_state = st.multiselect("Acquisition", ["New", "Used", "Market reference"])
    max_price = int(cars["price_aed"].max())
    price_range = st.slider(
        "Price (AED)",
        min_value=int(cars["price_aed"].min() // 5000 * 5000),
        max_value=int((max_price + 4999) // 5000 * 5000),
        value=(int(cars["price_aed"].min() // 5000 * 5000), int((max_price + 4999) // 5000 * 5000)),
        step=5000,
    )
    mileage_range = st.slider("Mileage (km)", 0, 60000, (0, 60000), step=2500)
    min_score = st.slider("Minimum trade-study score", 0, 100, 0, step=1)
    sort_by = st.selectbox(
        "Sort",
        ["Trade-study score", "Price: low → high", "Mileage: low → high", "Rank"],
    )
    st.divider()
    st.caption("Repository-backed dataset. Confirm live stock, dealer quotes, registration history and warranty before committing.")

filtered = cars.copy()
if selected_makes:
    filtered = filtered[filtered["make"].isin(selected_makes)]
if selected_power:
    filtered = filtered[filtered["powertrain"].isin(selected_power)]
if selected_state:
    filtered = filtered[filtered["state"].isin(selected_state)]
filtered = filtered[
    filtered["price_aed"].between(*price_range)
    & filtered["mileage_km"].between(*mileage_range)
    & (filtered["score_pct"] >= min_score)
]
if sort_by == "Trade-study score":
    filtered = filtered.sort_values(["score_pct","price_aed"], ascending=[False, True])
elif sort_by == "Price: low → high":
    filtered = filtered.sort_values(["price_aed","score_pct"], ascending=[True, False])
elif sort_by == "Mileage: low → high":
    filtered = filtered.sort_values(["mileage_km","score_pct"], ascending=[True, False])
else:
    filtered = filtered.sort_values(["rank","price_aed"])

overview, all_options, explore, compare, methodology = st.tabs(
    ["Overview", "All options", "Explore options", "Compare up to 3", "Criteria & method"]
)

with overview:
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Candidates", len(cars))
    c2.metric("Electrified", int((cars["powertrain"] != "ICE").sum()))
    c3.metric("Price span", f"{fmt_aed(cars.price_aed.min())} – {fmt_aed(cars.price_aed.max())}")
    c4.metric("Median score", f"{cars.score_pct.median():.1f}/100")

    st.subheader("Study context")
    st.markdown(
        """
        This dashboard is the repository-backed **Abu Dhabi SUV Purchase Trade Study**. The baseline assumes a
        **5-year ownership horizon**, **20,000 km/year**, GCC-spec vehicles, and a preference for new cars or
        recent used vehicles within the existing age/mileage gates. Financing cost is not yet embedded in the weighted score.
        """
    )

    with st.container(border=True):
        st.markdown("**Current baseline conclusion from the study**")
        st.write(
            "Honda CR-V LX 2WD 2025 GCC at AED 104,900 remains the baseline recommendation, conditional on VIN, "
            "provenance, warranty-start and registration verification. Toyota RAV4 Hybrid EX remains the lower-risk "
            "hybrid alternative. BYD Song Plus DM-i used 2025 is the strongest value-oriented electrified addition in the current dataset."
        )

    st.subheader("Assumptions")
    a1,a2,a3,a4,a5 = st.columns(5)
    a1.metric("Annual distance", "20,000 km")
    a2.metric("Ownership horizon", "5 years")
    a3.metric("Fuel reference", "AED 3.69/L")
    a4.metric("Public AC charging", "AED 0.735/kWh")
    a5.metric("Public DC charging", "AED 1.26/kWh")

    st.subheader("Portfolio view")
    fig = px.scatter(
        cars,
        x="price_aed",
        y="score_pct",
        size=(60000 - cars["mileage_km"].clip(upper=60000)) / 2500 + 8,
        symbol="state",
        color="powertrain",
        hover_name="candidate",
        hover_data={
            "price_aed":":,.0f",
            "mileage_km":":,.0f",
            "score_pct":":.1f",
            "rank":True,
            "status":True,
        },
        labels={"price_aed":"Price (AED)", "score_pct":"Trade-study score / 100", "powertrain":"Powertrain"},
        height=520,
    )
    fig.update_layout(margin=dict(l=10,r=10,t=20,b=10), legend_title_text="")
    st.plotly_chart(fig, use_container_width=True)

with all_options:
    st.subheader("All vehicle options")
    st.caption(
        f"Showing {len(filtered)} of {len(cars)} candidates. "
        "Use the sidebar to filter the catalogue, then open any vehicle for its full decision record."
    )

    if filtered.empty:
        st.info("No candidates match the active filters.")
    else:
        for _, row in filtered.iterrows():
            with st.container(border=True):
                name_col, price_col, score_col, action_col = st.columns([4.5, 1.5, 1.3, 1.2])

                with name_col:
                    st.markdown(f"**{row['candidate']}**")
                    st.caption(
                        f"{safe_year(row['model_year'])} · {row['model_trim']} · "
                        f"{row['powertrain']} · {row['acquisition']}"
                    )

                with price_col:
                    st.caption("Reference price")
                    st.markdown(f"**{fmt_aed(row['price_aed'])}**")
                    st.caption(fmt_km(row["mileage_km"]))

                with score_col:
                    st.caption("Study score")
                    st.markdown(f"**{row['score_pct']:.1f}/100**")
                    st.caption(f"Rank #{int(row['rank'])}")

                with action_col:
                    if st.button(
                        "View details",
                        key=f"list_detail_{int(row['id'])}",
                        use_container_width=True,
                    ):
                        show_vehicle_details(int(row["id"]))

with explore:
    st.caption(f"Showing {len(filtered)} of {len(cars)} candidates after sidebar filters.")
    table = filtered[[
        "candidate","model_year","state","powertrain","price_aed","mileage_km","score_pct","rank","status"
    ]].rename(columns={
        "candidate":"Candidate",
        "model_year":"Year",
        "state":"Acquisition",
        "powertrain":"Powertrain",
        "price_aed":"Price (AED)",
        "mileage_km":"Mileage (km)",
        "score_pct":"Score / 100",
        "rank":"Rank",
        "status":"Status",
    })
    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Price (AED)": st.column_config.NumberColumn(format="AED %d"),
            "Mileage (km)": st.column_config.NumberColumn(format="%d km"),
            "Score / 100": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f"),
        },
    )

    st.subheader("Candidate cards")
    display = filtered.head(18)
    if display.empty:
        st.info("No candidates match the active filters.")
    else:
        cols = st.columns(3)
        for idx, (_, row) in enumerate(display.iterrows()):
            with cols[idx % 3]:
                st.markdown(
                    f"""
                    <div class="vehicle-card">
                      <h3>{row['candidate']}</h3>
                      <div class="muted">{safe_year(row['model_year'])} · {row['acquisition']}</div>
                      <span class="pill">{row['powertrain']}</span>
                      <span class="pill">{row['status']}</span>
                      <div style="display:flex; justify-content:space-between; align-items:end; margin-top:.8rem;">
                        <div><div class="muted">Reference price</div><strong>{fmt_aed(row['price_aed'])}</strong></div>
                        <div style="text-align:right"><div class="muted">Score</div><div class="score">{row['score_pct']:.1f}</div></div>
                      </div>
                      <div class="muted" style="margin-top:.45rem;">Mileage: {fmt_km(row['mileage_km'])} · Rank #{int(row['rank'])}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(
                    "View vehicle details",
                    key=f"card_detail_{int(row['id'])}",
                    use_container_width=True,
                ):
                    show_vehicle_details(int(row["id"]))
                with st.expander("Evidence & source"):
                    st.write(row["evidence"])
                    st.markdown(f"[Open source listing / reference]({row['source_url']})")

with compare:
    st.subheader("Side-by-side comparison")
    st.caption("Select one to three candidates. The control is hard-capped at 3 to keep the comparison readable.")

    default_names = [
        "Honda CR-V LX — New 2025 (0 km)",
        "Toyota RAV4 Hybrid EX — New 2026",
        "BYD Song Plus DM-i — Used 2025 (12.6k km)",
    ]
    valid_defaults = [x for x in default_names if x in cars["candidate"].tolist()]
    selected = st.multiselect(
        "Vehicles to compare",
        options=cars.sort_values(["rank","price_aed"])["candidate"].tolist(),
        default=valid_defaults,
        max_selections=3,
        placeholder="Choose up to 3 vehicles",
    )

    if not selected:
        st.info("Select at least one vehicle to start the comparison.")
    else:
        comp = cars[cars["candidate"].isin(selected)].set_index("candidate").loc[selected].reset_index()

        card_cols = st.columns(len(comp))
        cheapest = comp["price_aed"].min()
        best_score = comp["score_pct"].max()
        for col, (_, row) in zip(card_cols, comp.iterrows()):
            with col:
                with st.container(border=True):
                    st.markdown(f"### {row['candidate']}")
                    st.caption(f"{safe_year(row['model_year'])} · {row['acquisition']}")
                    st.metric("Price", fmt_aed(row["price_aed"]),
                              delta=f"{row['price_aed']-cheapest:,.0f} vs cheapest" if row["price_aed"] != cheapest else "cheapest")
                    st.metric("Trade-study score", f"{row['score_pct']:.1f}/100",
                              delta=f"{row['score_pct']-best_score:+.1f} vs selected best" if row["score_pct"] != best_score else "selected best")
                    st.metric("Mileage", fmt_km(row["mileage_km"]))
                    st.write(f"**Powertrain:** {row['powertrain']}")
                    st.write(f"**Status:** {row['status']}")

        left, right = st.columns([1,1])
        with left:
            bar = px.bar(
                comp.sort_values("score_pct"),
                x="score_pct",
                y="candidate",
                orientation="h",
                text="score_pct",
                labels={"score_pct":"Score / 100","candidate":""},
                range_x=[0,100],
                height=360,
            )
            bar.update_traces(texttemplate="%{text:.1f}", textposition="outside")
            bar.update_layout(margin=dict(l=10,r=30,t=30,b=10), title="Overall weighted score")
            st.plotly_chart(bar, use_container_width=True)

        with right:
            fig = go.Figure()
            short = {
                "Purchase Price":"Price",
                "Resale Value / Depreciation":"Resale",
                "Reliability & Maintainability":"Reliability",
                "Service Network & Parts Availability":"Service",
                "Comfort & NVH":"Comfort",
                "Safety & ADAS":"Safety",
                "UAE Climate & Road Suitability":"UAE fit",
                "Total Cost of Ownership":"TCO",
                "Practicality & Space":"Space",
                "Fuel Economy / Driving Range":"Efficiency",
                "Performance & Driveability":"Drive",
                "Technology & Convenience":"Tech",
            }
            theta=[short[x] for x in criterion_names]
            for _, row in comp.iterrows():
                vals=[row[x] for x in criterion_names]
                fig.add_trace(go.Scatterpolar(
                    r=vals + [vals[0]],
                    theta=theta + [theta[0]],
                    fill="toself",
                    name=row["candidate"],
                    opacity=0.55,
                ))
            fig.update_layout(
                title="Criteria profile (1–5)",
                polar=dict(radialaxis=dict(visible=True, range=[0,5])),
                showlegend=True,
                margin=dict(l=35,r=35,t=55,b=25),
                height=430,
            )
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Criterion-by-criterion")
        matrix = comp.set_index("candidate")[criterion_names].T
        matrix.index.name = "Criterion"
        st.dataframe(
            matrix,
            use_container_width=True,
        )

        st.subheader("Evidence and diligence")
        ev_cols = st.columns(len(comp))
        for col, (_, row) in zip(ev_cols, comp.iterrows()):
            with col:
                with st.container(border=True):
                    st.markdown(f"**{row['candidate']}**")
                    st.write(row["evidence"])
                    st.markdown(f"[Open source / listing]({row['source_url']})")

with methodology:
    st.subheader("How the score works")
    st.write(
        "Each candidate is scored from **1 to 5** against 12 criteria. The criteria weights come from the original "
        "pairwise-priority model; the weighted result is normalized to a 0–100 dashboard score. Higher means a better "
        "fit to the current study assumptions, not a guarantee that the vehicle is the right purchase after inspection and financing."
    )

    weights = criteria.sort_values("weight_pct", ascending=True)
    wfig = px.bar(
        weights,
        x="weight_pct",
        y="name",
        orientation="h",
        text="weight_pct",
        labels={"weight_pct":"Weight (%)","name":""},
        height=500,
    )
    wfig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    wfig.update_layout(margin=dict(l=10,r=30,t=20,b=10))
    st.plotly_chart(wfig, use_container_width=True)

    st.dataframe(
        criteria[["name","weight_pct","rationale"]].rename(columns={
            "name":"Criterion","weight_pct":"Weight (%)","rationale":"Why it matters"
        }),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Interpretation guardrails")
    st.markdown(
        """
        - **Prices are snapshots**, not executable quotes. Reconfirm stock, dealer fees and promotions.
        - Used vehicles must pass **VIN, accident/repair, service history, first-registration and warranty-transfer** checks.
        - EV/PHEV candidates need **battery state-of-health / charging-history** diligence and a realistic charging-access model.
        - The current weighted score does **not** include ADCB financing economics, insurance quotes or your exact home-charging cost.
        - Treat the dashboard as a traceable decision-support layer; final purchase approval should still use a vehicle-specific pre-purchase inspection and written offer.
        """
    )
