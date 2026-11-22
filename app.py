"""Degrees of Weird v0.1 Streamlit scenario comparison app."""
import json
import importlib
import io

try:
    st = importlib.import_module("streamlit")
except ImportError:
    raise SystemExit("Missing required dependency: streamlit. Install it with `pip install streamlit`, then restart the app.")

try:
    pd = importlib.import_module("pandas")
except ImportError:
    st.error("Missing required dependency: pandas. Install it with `pip install pandas`, then restart the app.")
    st.stop()
from scoring_engine import (
    DISTANCE_WEIGHTS, PERMISSION_WEIGHTS, DISTANCE_LABELS,
    PERMISSION_LABELS, DISTANCE_QUESTIONS, PERMISSION_QUESTIONS, calculate,
)

st.set_page_config(page_title="Degrees of Weird | Brand Stretch Simulator", page_icon="🧭", layout="wide")
st.markdown("""<style>
.block-container {max-width: 1300px; padding-top: 2rem;}
[data-testid="stMetricValue"] {font-size: 2rem;}
</style>""", unsafe_allow_html=True)
st.title("Degrees of Weird")
st.caption("Brand stretch simulator · v0.1 · Expert-input heuristic (not consumer-validated)")
st.warning("Decision-support prototype only. Scores are NOT probabilities, scientifically validated thresholds, or launch recommendations. Do not treat a high score as proof of failure.", icon="⚠️")

BRAND_DEFAULT = {"equity_strength": 8, "brand_breadth": 6, "brand_elasticity": 7, "extension_precedent": 5}
PRESETS = [
    ("Chocolate → Baking mix", [2,3,4,2,2,3]),
    ("Chocolate → Protein shake", [3,4,7,4,2,4]),
    ("Chocolate → Energy drink", [6,7,8,7,5,7]),
    ("Chocolate → Skincare", [8,8,10,9,7,9]),
]

if "permission" not in st.session_state:
    st.session_state.permission = dict(BRAND_DEFAULT)
if "scenarios" not in st.session_state:
    st.session_state.scenarios = pd.DataFrame([
        {"Scenario": name, **dict(zip(DISTANCE_WEIGHTS, scores)), "bridge_adjustment": 0}
        for name, scores in PRESETS
    ])

with st.sidebar:
    st.header("Parent-brand profile")
    st.caption("Use the SAME brand profile across all scenarios. Input ratings: 0–10, higher means more brand permission.")
    for k in PERMISSION_WEIGHTS:
        st.session_state.permission[k] = st.slider(
            f"{PERMISSION_LABELS[k]} ({round(PERMISSION_WEIGHTS[k]*100)}%)",
            0, 10, int(st.session_state.permission[k]), key=f"perm_{k}",
            help=PERMISSION_QUESTIONS[k]
        )
    st.divider()
    st.markdown("**Interpretation**")
    st.caption("Gap = effective weirdness − permission ceiling. Positive = beyond estimated boundary; negative = headroom. Boundary labels use provisional ±15-point bands.")
    st.caption("Bridge adjustment (0–20): user-assumed reduction in perceived distance from a positioning/proof/partnership intervention. Not causal evidence.")

st.subheader("01 / Score and compare extensions")
st.write("Edit each row, add a new scenario, or remove existing ones. Distance ratings range from 0 (very close) to 10 (very far).")
left, right = st.columns([1,3])
with left:
    if st.button("Restore example scenarios", use_container_width=True):
        st.session_state.scenarios = pd.DataFrame([
            {"Scenario": name, **dict(zip(DISTANCE_WEIGHTS, scores)), "bridge_adjustment": 0}
            for name, scores in PRESETS
        ])
        st.rerun()
with right:
    st.caption("Sample scenarios are fictional expert estimates, not consumer research.")
config = {"Scenario": st.column_config.TextColumn("Extension scenario", required=True, width="large")}
for k in DISTANCE_WEIGHTS:
    config[k] = st.column_config.NumberColumn(
        f"{DISTANCE_LABELS[k]} ({round(DISTANCE_WEIGHTS[k]*100)}%)",
        min_value=0, max_value=10, step=1, required=True, help=DISTANCE_QUESTIONS[k]
    )
config["bridge_adjustment"] = st.column_config.NumberColumn(
    "Assumed bridge (0–20°)", min_value=0, max_value=20, step=1, required=True,
    help="Unvalidated hypothetical improvement. Not estimated from an experiment."
)
edited = st.data_editor(st.session_state.scenarios, num_rows="dynamic", hide_index=True,
                        use_container_width=True, column_config=config, key="scenario_editor")
# Compute safely: warn about incomplete rows rather than crashing.
results = []
errors = []
for i, row in edited.iterrows():
    try:
        if pd.isna(row.get("Scenario")):
            raise ValueError("A scenario needs a name")
        dist = {k: float(row[k]) for k in DISTANCE_WEIGHTS}
        b = float(row["bridge_adjustment"])
        result = calculate(str(row["Scenario"]), dist, st.session_state.permission, b)
        results.append(result)
    except (ValueError, TypeError, KeyError) as e:
        errors.append(f"Row {i+1}: {e}")
if errors:
    st.info("Skipped incomplete or invalid rows: " + " | ".join(errors))

if results:
    frame = pd.DataFrame([{
        "Scenario": r.scenario, "Raw weirdness": r.raw_weirdness,
        "Bridge assumption": r.bridge_adjustment, "Effective weirdness": r.effective_weirdness,
        "Permission ceiling": r.permission_ceiling, "Permission gap": r.permission_gap,
        "Interpretation": r.status,
        "Top drivers": ", ".join(DISTANCE_LABELS[k] for k in r.top_distance_drivers),
    } for r in results])
    ceiling = results[0].permission_ceiling
    c1,c2,c3 = st.columns(3)
    c1.metric("Parent brand permission ceiling", f"{ceiling:.1f}°")
    c2.metric("Extensions evaluated", str(len(results)))
    c3.metric("Extensions beyond permission", str(sum(r.permission_gap > 0 for r in results)))
    st.subheader("02 / Scenario results")
    st.dataframe(frame, use_container_width=True, hide_index=True)
    chart_data = frame.set_index("Scenario")[["Effective weirdness", "Permission ceiling"]]
    st.bar_chart(chart_data, horizontal=True, stack=False)
    st.caption("All comparisons share the same manually specified parent-brand permission profile. Scores are provisional ordinal indexes.")

    st.subheader("03 / Driver diagnostics")
    selected = st.selectbox("Inspect scenario", options=range(len(results)),
                            format_func=lambda i: results[i].scenario)
    r = results[selected]
    s1,s2,s3 = st.columns(3)
    s1.metric("Raw weirdness", f"{r.raw_weirdness:.1f}°")
    s2.metric("Effective weirdness", f"{r.effective_weirdness:.1f}°")
    s3.metric("Signed permission gap", f"{r.permission_gap:+.1f}°")
    st.write(f"**Provisional interpretation:** {r.status}")
    driver_table = pd.DataFrame([
        {"Dimension": DISTANCE_LABELS[k], "Weight (%)": int(round(DISTANCE_WEIGHTS[k] * 100)),
         "Contribution (0–100 scale)": r.distance_contributions[k]}
        for k in DISTANCE_WEIGHTS
    ])
    st.dataframe(driver_table, hide_index=True, use_container_width=True,
                 column_config={"Weight (%)": st.column_config.NumberColumn(format="%d%%")})
    st.caption("Contributions = input rating × weight × 10. The 'bridge' is subtracted from the total, not from any one dimension.")

    st.subheader("04 / Export")
    st.download_button("Download comparison CSV", data=frame.to_csv(index=False).encode("utf-8"),
                       file_name="degrees_of_weird_comparison.csv", mime="text/csv")
    export_data = {"model_version":"0.1-unvalidated", "brand_permission_inputs":st.session_state.permission,
                   "scenarios":[r.to_dict() for r in results],
                   "disclaimer":"Unvalidated, expert-input, non-predictive methodology; no measured consumer probabilities."}
    st.download_button("Download full scoring JSON", data=json.dumps(export_data, indent=2),
                       file_name="degrees_of_weird_results.json", mime="application/json")
else:
    st.info("Add at least one complete scenario to calculate scores.")

with st.expander("Methodology, scoring scales, and limitations"):
    st.markdown("""**Distance (W)** = 10 × weighted mean of six 0–10 distance ratings.

**Permission (P)** = 10 × weighted mean of four 0–10 brand permission ratings.

**Effective weirdness** = max(0, W − assumed_bridge_adjustment).

**Gap (G)** = effective weirdness − P. A positive gap indicates greater modeled distance than modeled permission.

**Warning:** These ratings and weights are judgmental. The similarity of the two 0–100 scales is a design convenience, not empirical commensurability. Do not infer a probability of commercial success, sales forecast, or causal effect from these outputs. Before commercialization, run consumer research, estimate weights, examine construct validity, validate against holdout concepts/brands, and quantify uncertainty. Real-world demand, price, distribution, and execution are outside this model.""")
