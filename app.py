"""ARIA Streamlit demonstration interface."""

# ruff: noqa: I001

from __future__ import annotations

import sys
from datetime import date, datetime, timezone
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from aria_core import AssessmentRequest, EvidenceRecord, assess_pollinator_habitat


PRESETS = {
    "Balanced evidence": {
        "location": "Milwaukee County demonstration site",
        "jurisdiction": "Milwaukee County, Wisconsin",
        "soil_ph": 6.5,
        "water": "Reliable",
        "slope": 3.0,
        "ecology": "Low",
        "regulation": "Cleared",
        "include_water": True,
    },
    "Missing water evidence": {
        "location": "Milwaukee County demonstration site",
        "jurisdiction": "Milwaukee County, Wisconsin",
        "soil_ph": 6.5,
        "water": "Unknown",
        "slope": 3.0,
        "ecology": "Low",
        "regulation": "Cleared",
        "include_water": False,
    },
    "Ecologically sensitive slope": {
        "location": "Illustrative restoration parcel",
        "jurisdiction": "Example jurisdiction",
        "soil_ph": 5.2,
        "water": "Seasonal",
        "slope": 14.0,
        "ecology": "High",
        "regulation": "Pending",
        "include_water": True,
    },
    "Regulatory restriction": {
        "location": "Illustrative protected parcel",
        "jurisdiction": "Example jurisdiction",
        "soil_ph": 6.8,
        "water": "Reliable",
        "slope": 2.0,
        "ecology": "Moderate",
        "regulation": "Restricted",
        "include_water": True,
    },
}


def _record(
    evidence_id: str,
    indicator: str,
    value: object,
    unit: str,
    source: str,
    observed_on: date,
    location: str,
    method: str,
) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=evidence_id,
        indicator=indicator,
        value=value,
        unit=unit,
        source=source,
        observed_on=observed_on,
        location=location,
        method=method,
        quality="User supplied, unverified",
    )


st.set_page_config(
    page_title="ARIA | Environmental Decision Intelligence",
    page_icon="🌱",
    layout="wide",
)
st.markdown(
    """
    <style>
    :root { --aria-green:#36d399; --aria-muted:#92a39c; }
    .block-container { max-width:1180px; padding-top:2rem; }
    [data-testid="stAppViewContainer"] { background:linear-gradient(145deg,#07110e 0%,#0d1b17 55%,#10241d 100%); }
    [data-testid="stSidebar"] { background:#091511; }
    h1,h2,h3 { letter-spacing:-0.025em; }
    .aria-kicker { color:var(--aria-green); font-weight:700; letter-spacing:.14em; text-transform:uppercase; font-size:.78rem; }
    .aria-subtitle { color:var(--aria-muted); font-size:1.1rem; margin-top:-.7rem; max-width:760px; }
    .aria-note { border-left:3px solid var(--aria-green); background:rgba(54,211,153,.08); padding:.8rem 1rem; border-radius:0 .5rem .5rem 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="aria-kicker">Nature · Science · Regulation · Industry · AI</div>',
    unsafe_allow_html=True,
)
st.title("ARIA")
st.markdown(
    '<div class="aria-subtitle">Environmental decision intelligence that keeps evidence, uncertainty, and human responsibility visible.</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Demonstration")
    preset_name = st.selectbox("Scenario", tuple(PRESETS))
    preset = PRESETS[preset_name]
    st.caption("Changing scenarios resets the form defaults for a clear comparison.")
    st.divider()
    st.markdown("**Prototype question**")
    st.write(
        "Does the supplied evidence support advancing a native pollinator habitat proposal for qualified review?"
    )
    st.info(
        "This prototype provides decision support, not scientific, legal, regulatory, or engineering approval."
    )

st.markdown("### Evidence intake")
st.caption(
    "Every input remains connected to source, time, location, method, and quality metadata."
)

with st.form("assessment"):
    context_left, context_right = st.columns(2)
    location = context_left.text_input(
        "Location", value=preset["location"], key=f"location-{preset_name}"
    )
    jurisdiction = context_right.text_input(
        "Regulatory jurisdiction",
        value=preset["jurisdiction"],
        key=f"jurisdiction-{preset_name}",
    )

    metadata_left, metadata_middle, metadata_right = st.columns(3)
    source = metadata_left.text_input(
        "Evidence source",
        value="Hackathon demonstration record",
        key=f"source-{preset_name}",
    )
    observed_on = metadata_middle.date_input(
        "Observed on",
        value=datetime.now(timezone.utc).date(),
        key=f"date-{preset_name}",
    )
    method = metadata_right.text_input(
        "Method", value="User supplied", key=f"method-{preset_name}"
    )

    st.divider()
    soil_col, water_col, terrain_col = st.columns(3)
    soil_ph = soil_col.number_input(
        "Soil pH",
        min_value=0.0,
        max_value=14.0,
        value=preset["soil_ph"],
        step=0.1,
        key=f"soil-{preset_name}",
    )
    include_water = water_col.checkbox(
        "Water evidence available",
        value=preset["include_water"],
        key=f"include-water-{preset_name}",
    )
    water_options = ("Reliable", "Seasonal", "Limited", "Unknown")
    water = water_col.selectbox(
        "Water availability",
        water_options,
        index=water_options.index(preset["water"]),
        key=f"water-{preset_name}",
    )
    slope = terrain_col.number_input(
        "Slope (%)",
        min_value=0.0,
        max_value=100.0,
        value=preset["slope"],
        step=0.5,
        key=f"slope-{preset_name}",
    )

    ecology_col, regulation_col = st.columns(2)
    ecology_options = ("Low", "Moderate", "High", "Unknown")
    ecology = ecology_col.selectbox(
        "Ecological sensitivity",
        ecology_options,
        index=ecology_options.index(preset["ecology"]),
        key=f"ecology-{preset_name}",
    )
    regulation_options = ("Cleared", "Pending", "Unknown", "Restricted")
    regulation = regulation_col.selectbox(
        "Preliminary regulatory status",
        regulation_options,
        index=regulation_options.index(preset["regulation"]),
        key=f"regulation-{preset_name}",
    )

    submitted = st.form_submit_button(
        "Assess environmental capacity", width="stretch", type="primary"
    )

if submitted:
    records = [
        _record(
            "E-SOIL-001",
            "soil_ph",
            soil_ph,
            "pH",
            source,
            observed_on,
            location,
            method,
        ),
        _record(
            "E-TERRAIN-001",
            "slope_percent",
            slope,
            "%",
            source,
            observed_on,
            location,
            method,
        ),
        _record(
            "E-ECOLOGY-001",
            "ecological_sensitivity",
            ecology.lower(),
            "category",
            source,
            observed_on,
            location,
            method,
        ),
        _record(
            "E-REG-001",
            "regulatory_status",
            regulation.lower(),
            "status",
            source,
            observed_on,
            location,
            method,
        ),
    ]
    if include_water:
        records.append(
            _record(
                "E-WATER-001",
                "water_availability",
                water.lower(),
                "category",
                source,
                observed_on,
                location,
                method,
            )
        )

    result = assess_pollinator_habitat(
        AssessmentRequest(
            activity="Native pollinator habitat",
            location=location,
            jurisdiction=jurisdiction,
            evidence=tuple(records),
        )
    )

    st.divider()
    st.markdown("### Assessment")
    status_col, uncertainty_col, evidence_col = st.columns(3)
    status_col.metric("Decision-support status", result.status.value)
    uncertainty_col.metric("Uncertainty", result.uncertainty)
    evidence_col.metric("Evidence records", len(result.evidence))
    st.markdown(
        f'<div class="aria-note">{result.summary}</div>', unsafe_allow_html=True
    )

    st.markdown("#### Domain findings")
    st.dataframe(
        [
            {
                "Domain": item.domain,
                "Status": item.status.value,
                "Finding": item.finding,
                "Evidence": ", ".join(item.evidence_ids) or "None",
                "Uncertainty": item.uncertainty,
                "Next action": item.next_action,
            }
            for item in result.criteria
        ],
        width="stretch",
        hide_index=True,
    )

    if result.missing_evidence:
        st.warning(
            "Missing or unusable evidence: " + ", ".join(result.missing_evidence)
        )
    if result.validation_errors:
        st.error("Validation failed: " + " | ".join(result.validation_errors))

    review_col, assumption_col = st.columns(2)
    with review_col:
        st.markdown("#### Human review gates")
        for item in result.human_review:
            st.write(f"• {item}")
    with assumption_col:
        st.markdown("#### Assumptions and limits")
        for item in result.assumptions:
            st.write(f"• {item}")

    with st.expander("Evidence ledger"):
        st.dataframe(
            [
                {
                    "ID": item.evidence_id,
                    "Indicator": item.indicator,
                    "Value": str(item.value),
                    "Unit": item.unit,
                    "Source": item.source,
                    "Observed": item.observed_on.isoformat(),
                    "Location": item.location,
                    "Method": item.method,
                    "Quality": item.quality,
                }
                for item in result.evidence
            ],
            width="stretch",
            hide_index=True,
        )

with st.expander("What this prototype does not claim"):
    st.write(
        "ARIA does not claim that the evidence is independently verified, that the illustrative reference rules are scientifically validated, "
        "that regulatory requirements were retrieved or interpreted, or that the displayed status authorizes action."
    )
