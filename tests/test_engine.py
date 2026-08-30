"""Behavioral tests for the evidence-first assessment engine."""

# ruff: noqa: I001

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path
from unittest import TestCase

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aria_core import (
    AssessmentRequest,
    AssessmentStatus,
    CriterionStatus,
    EvidenceRecord,
    assess_pollinator_habitat,
)


TODAY = date(2026, 8, 29)


def evidence(
    indicator: str, value: object, *, observed_on: date = TODAY
) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=f"E-{indicator.upper()}",
        indicator=indicator,
        value=value,
        unit="prototype unit",
        source="Test fixture",
        observed_on=observed_on,
        location="Test site",
        method="Controlled test",
        quality="Verified",
    )


def request(
    *,
    overrides: dict[str, object] | None = None,
    omit: set[str] | None = None,
) -> AssessmentRequest:
    values: dict[str, object] = {
        "soil_ph": 6.5,
        "water_availability": "reliable",
        "slope_percent": 3.0,
        "ecological_sensitivity": "low",
        "regulatory_status": "cleared",
    }
    values.update(overrides or {})
    omissions = omit or set()
    return AssessmentRequest(
        activity="Native pollinator habitat",
        location="Test site",
        jurisdiction="Test jurisdiction",
        evidence=tuple(
            evidence(key, value)
            for key, value in values.items()
            if key not in omissions
        ),
    )


class AssessmentEngineTests(TestCase):
    def test_balanced_evidence_advances_only_to_review(self) -> None:
        result = assess_pollinator_habitat(request(), today=TODAY)
        self.assertEqual(result.status, AssessmentStatus.SUPPORTED)
        self.assertIn("human", result.human_review[0].lower())

    def test_missing_evidence_fails_gracefully(self) -> None:
        result = assess_pollinator_habitat(
            request(omit={"water_availability"}), today=TODAY
        )
        self.assertEqual(result.status, AssessmentStatus.INSUFFICIENT)
        self.assertIn("water availability", result.missing_evidence)

    def test_regulatory_restriction_stops_scenario(self) -> None:
        result = assess_pollinator_habitat(
            request(overrides={"regulatory_status": "restricted"}), today=TODAY
        )
        self.assertEqual(result.status, AssessmentStatus.NOT_SUPPORTED)

    def test_pending_regulation_is_conditional(self) -> None:
        result = assess_pollinator_habitat(
            request(overrides={"regulatory_status": "pending"}), today=TODAY
        )
        self.assertEqual(result.status, AssessmentStatus.CONDITIONAL)

    def test_seasonal_water_is_conditional(self) -> None:
        result = assess_pollinator_habitat(
            request(overrides={"water_availability": "seasonal"}), today=TODAY
        )
        self.assertEqual(result.status, AssessmentStatus.CONDITIONAL)

    def test_high_sensitivity_creates_constraint_and_review(self) -> None:
        result = assess_pollinator_habitat(
            request(overrides={"ecological_sensitivity": "high"}), today=TODAY
        )
        ecology = next(item for item in result.criteria if item.domain == "Ecology")
        self.assertEqual(ecology.status, CriterionStatus.CONSTRAINT)
        self.assertTrue(
            any("Ecological review" in item for item in result.human_review)
        )

    def test_out_of_range_ph_is_invalid(self) -> None:
        result = assess_pollinator_habitat(
            request(overrides={"soil_ph": 15.0}), today=TODAY
        )
        self.assertEqual(result.status, AssessmentStatus.INSUFFICIENT)
        self.assertTrue(
            any("between 0 and 14" in item for item in result.validation_errors)
        )

    def test_future_evidence_is_invalid(self) -> None:
        records = list(request().evidence)
        records[0] = evidence("soil_ph", 6.5, observed_on=TODAY + timedelta(days=1))
        result = assess_pollinator_habitat(
            AssessmentRequest(
                "Native pollinator habitat",
                "Test site",
                "Test jurisdiction",
                tuple(records),
            ),
            today=TODAY,
        )
        self.assertEqual(result.status, AssessmentStatus.INSUFFICIENT)
        self.assertTrue(any("future" in item for item in result.validation_errors))

    def test_every_successful_domain_finding_is_traceable(self) -> None:
        result = assess_pollinator_habitat(request(), today=TODAY)
        self.assertTrue(all(item.evidence_ids for item in result.criteria))

    def test_uncertainty_rises_when_evidence_is_missing(self) -> None:
        result = assess_pollinator_habitat(
            request(omit={"water_availability"}), today=TODAY
        )
        self.assertEqual(result.uncertainty, "High")

    def test_unverified_evidence_prevents_low_uncertainty(self) -> None:
        records = list(request().evidence)
        original = records[0]
        records[0] = EvidenceRecord(
            evidence_id=original.evidence_id,
            indicator=original.indicator,
            value=original.value,
            unit=original.unit,
            source=original.source,
            observed_on=original.observed_on,
            location=original.location,
            method=original.method,
            quality="User supplied, unverified",
        )
        result = assess_pollinator_habitat(
            AssessmentRequest(
                "Native pollinator habitat",
                "Test site",
                "Test jurisdiction",
                tuple(records),
            ),
            today=TODAY,
        )
        self.assertEqual(result.uncertainty, "Moderate")

    def test_missing_jurisdiction_is_insufficient(self) -> None:
        base = request()
        result = assess_pollinator_habitat(
            AssessmentRequest(
                base.activity,
                base.location,
                "",
                base.evidence,
            ),
            today=TODAY,
        )
        self.assertEqual(result.status, AssessmentStatus.INSUFFICIENT)
        self.assertIn("regulatory status", result.missing_evidence)

    def test_duplicate_indicator_records_are_rejected(self) -> None:
        base = request()
        duplicate = EvidenceRecord(
            evidence_id="E-SOIL-DUPLICATE",
            indicator="soil_ph",
            value=7.0,
            unit="pH",
            source="Second test fixture",
            observed_on=TODAY,
            location="Test site",
            quality="Verified",
        )
        result = assess_pollinator_habitat(
            AssessmentRequest(
                base.activity,
                base.location,
                base.jurisdiction,
                base.evidence + (duplicate,),
            ),
            today=TODAY,
        )
        self.assertEqual(result.status, AssessmentStatus.INSUFFICIENT)
        self.assertTrue(
            any("duplicate indicator" in item for item in result.validation_errors)
        )
