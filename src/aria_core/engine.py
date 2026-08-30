"""Deterministic, inspectable assessment logic for the hackathon slice."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime, timezone

from .models import (
    AssessmentRequest,
    AssessmentResult,
    AssessmentStatus,
    CriterionResult,
    CriterionStatus,
    EvidenceRecord,
)

EXPECTED_INDICATORS = (
    "soil_ph",
    "water_availability",
    "slope_percent",
    "ecological_sensitivity",
    "regulatory_status",
)

ALLOWED_VALUES = {
    "water_availability": {"reliable", "seasonal", "limited", "unknown"},
    "ecological_sensitivity": {"low", "moderate", "high", "unknown"},
    "regulatory_status": {"cleared", "pending", "unknown", "restricted"},
}


def _validate(record: EvidenceRecord, today: date) -> tuple[str, ...]:
    errors: list[str] = []
    label = record.indicator.replace("_", " ")

    if not record.evidence_id.strip():
        errors.append(f"{label}: evidence ID is required")
    if not record.source.strip():
        errors.append(f"{label}: source is required")
    if not record.location.strip():
        errors.append(f"{label}: location is required")
    if record.observed_on > today:
        errors.append(f"{label}: observation date cannot be in the future")

    if record.indicator == "soil_ph":
        if not isinstance(record.value, (int, float)) or isinstance(record.value, bool):
            errors.append("soil pH: value must be numeric")
        elif not 0 <= float(record.value) <= 14:
            errors.append("soil pH: value must be between 0 and 14")
    elif record.indicator == "slope_percent":
        if not isinstance(record.value, (int, float)) or isinstance(record.value, bool):
            errors.append("slope percent: value must be numeric")
        elif not 0 <= float(record.value) <= 100:
            errors.append("slope percent: value must be between 0 and 100")
    elif record.indicator in ALLOWED_VALUES:
        normalized = str(record.value).strip().lower()
        if normalized not in ALLOWED_VALUES[record.indicator]:
            allowed = ", ".join(sorted(ALLOWED_VALUES[record.indicator]))
            errors.append(f"{label}: expected one of {allowed}")

    return tuple(errors)


def _missing(domain: str, indicator: str) -> CriterionResult:
    label = indicator.replace("_", " ")
    return CriterionResult(
        domain=domain,
        status=CriterionStatus.MISSING,
        finding=f"No usable {label} evidence was provided.",
        uncertainty="This domain cannot be assessed.",
        next_action=f"Provide a dated, located, and sourced {label} record.",
    )


def _invalid(
    domain: str, record: EvidenceRecord, errors: tuple[str, ...]
) -> CriterionResult:
    return CriterionResult(
        domain=domain,
        status=CriterionStatus.INVALID,
        finding="The supplied evidence failed validation.",
        evidence_ids=(record.evidence_id,),
        uncertainty="; ".join(errors),
        next_action="Correct or replace this evidence before drawing a conclusion.",
    )


def _soil(record: EvidenceRecord) -> CriterionResult:
    value = float(record.value)
    if 5.5 <= value <= 7.5:
        return CriterionResult(
            domain="Soil",
            status=CriterionStatus.SUPPORTS,
            finding=f"The supplied soil pH of {value:.1f} is within the prototype reference range.",
            evidence_ids=(record.evidence_id,),
            uncertainty="Plant-specific requirements are not evaluated.",
            next_action="Confirm against the selected native plant community and local soil guidance.",
        )
    return CriterionResult(
        domain="Soil",
        status=CriterionStatus.CONDITIONAL,
        finding=f"The supplied soil pH of {value:.1f} is outside the prototype reference range.",
        evidence_ids=(record.evidence_id,),
        uncertainty="A value outside this range is not automatically unsuitable.",
        next_action="Use plant-specific requirements and a qualified soil assessment.",
    )


def _water(record: EvidenceRecord) -> CriterionResult:
    value = str(record.value).lower()
    if value == "reliable":
        return CriterionResult(
            domain="Water",
            status=CriterionStatus.SUPPORTS,
            finding="The supplied evidence describes water availability as reliable.",
            evidence_ids=(record.evidence_id,),
            next_action="Verify seasonal demand and the proposed establishment plan.",
        )
    if value == "seasonal":
        return CriterionResult(
            domain="Water",
            status=CriterionStatus.CONDITIONAL,
            finding="Water availability is seasonal.",
            evidence_ids=(record.evidence_id,),
            uncertainty="Availability during establishment and drought periods is unresolved.",
            next_action="Document seasonal demand, storage, and drought response.",
        )
    if value == "limited":
        return CriterionResult(
            domain="Water",
            status=CriterionStatus.CONSTRAINT,
            finding="Water availability is limited.",
            evidence_ids=(record.evidence_id,),
            uncertainty="The effect depends on species, establishment method, and climate.",
            next_action="Obtain a water plan or select a demonstrably compatible planting strategy.",
        )
    return CriterionResult(
        domain="Water",
        status=CriterionStatus.MISSING,
        finding="Water availability is recorded as unknown.",
        evidence_ids=(record.evidence_id,),
        uncertainty="Water capacity cannot be assessed.",
        next_action="Collect seasonal water availability evidence.",
    )


def _terrain(record: EvidenceRecord) -> CriterionResult:
    value = float(record.value)
    if value < 5:
        return CriterionResult(
            domain="Terrain",
            status=CriterionStatus.SUPPORTS,
            finding=f"The supplied slope of {value:.1f}% creates no prototype terrain flag.",
            evidence_ids=(record.evidence_id,),
            next_action="Confirm drainage and erosion conditions on site.",
        )
    if value <= 12:
        return CriterionResult(
            domain="Terrain",
            status=CriterionStatus.CONDITIONAL,
            finding=f"The supplied slope of {value:.1f}% may require erosion controls.",
            evidence_ids=(record.evidence_id,),
            uncertainty="Soil texture, vegetation, drainage, and disturbance are not represented.",
            next_action="Request a site-specific erosion and drainage review.",
        )
    return CriterionResult(
        domain="Terrain",
        status=CriterionStatus.CONSTRAINT,
        finding=f"The supplied slope of {value:.1f}% is a material prototype constraint.",
        evidence_ids=(record.evidence_id,),
        uncertainty="This prototype cannot determine safe site preparation.",
        next_action="Require qualified terrain, drainage, and erosion review before proceeding.",
    )


def _ecology(record: EvidenceRecord) -> CriterionResult:
    value = str(record.value).lower()
    if value == "low":
        return CriterionResult(
            domain="Ecology",
            status=CriterionStatus.SUPPORTS,
            finding="The supplied evidence identifies low ecological sensitivity.",
            evidence_ids=(record.evidence_id,),
            uncertainty="A formal ecological survey has not been inferred.",
            next_action="Confirm species selection and local habitat priorities.",
        )
    if value == "moderate":
        return CriterionResult(
            domain="Ecology",
            status=CriterionStatus.CONDITIONAL,
            finding="The supplied evidence identifies moderate ecological sensitivity.",
            evidence_ids=(record.evidence_id,),
            uncertainty="Potential habitat interactions need specialist interpretation.",
            next_action="Request ecological review before altering the site.",
        )
    if value == "high":
        return CriterionResult(
            domain="Ecology",
            status=CriterionStatus.CONSTRAINT,
            finding="The supplied evidence identifies high ecological sensitivity.",
            evidence_ids=(record.evidence_id,),
            uncertainty="The prototype cannot determine whether intervention would help or harm.",
            next_action="Require ecological specialist and authority review before any intervention.",
        )
    return CriterionResult(
        domain="Ecology",
        status=CriterionStatus.MISSING,
        finding="Ecological sensitivity is recorded as unknown.",
        evidence_ids=(record.evidence_id,),
        uncertainty="Potential ecological conflicts cannot be evaluated.",
        next_action="Obtain ecological context or a site survey.",
    )


def _regulation(record: EvidenceRecord, jurisdiction: str) -> CriterionResult:
    value = str(record.value).lower()
    if not jurisdiction.strip():
        return CriterionResult(
            domain="Regulation",
            status=CriterionStatus.MISSING,
            finding="No regulatory jurisdiction was supplied.",
            evidence_ids=(record.evidence_id,),
            uncertainty="Regulatory applicability cannot be assessed without jurisdiction.",
            next_action="Identify the relevant jurisdiction and responsible authority.",
        )
    scope = jurisdiction
    if value == "cleared":
        return CriterionResult(
            domain="Regulation",
            status=CriterionStatus.SUPPORTS,
            finding=f"The supplied record marks preliminary regulatory review as cleared for {scope}.",
            evidence_ids=(record.evidence_id,),
            uncertainty="ARIA has not independently retrieved or interpreted legal authority.",
            next_action="Verify the cited authority, provision, effective date, and applicability.",
        )
    if value == "restricted":
        return CriterionResult(
            domain="Regulation",
            status=CriterionStatus.CONSTRAINT,
            finding=f"The supplied record identifies a regulatory restriction in {scope}.",
            evidence_ids=(record.evidence_id,),
            uncertainty="The prototype does not interpret exceptions or legal remedies.",
            next_action="Stop and obtain review from the responsible authority or qualified professional.",
        )
    if value == "pending":
        return CriterionResult(
            domain="Regulation",
            status=CriterionStatus.CONDITIONAL,
            finding=f"Regulatory review is pending for {scope}.",
            evidence_ids=(record.evidence_id,),
            uncertainty="Authorization has not been established.",
            next_action="Resolve applicable requirements before implementation.",
        )
    return CriterionResult(
        domain="Regulation",
        status=CriterionStatus.MISSING,
        finding=f"Regulatory applicability is unknown for {scope}.",
        evidence_ids=(record.evidence_id,),
        uncertainty="The activity cannot be treated as authorized.",
        next_action="Identify the authority, jurisdiction, provision, effective date, and applicability.",
    )


def _criterion(
    domain: str,
    indicator: str,
    records: dict[str, EvidenceRecord],
    errors: dict[str, tuple[str, ...]],
    request: AssessmentRequest,
) -> CriterionResult:
    record = records.get(indicator)
    if record is None:
        return _missing(domain, indicator)
    if errors.get(indicator):
        return _invalid(domain, record, errors[indicator])
    if indicator == "regulatory_status":
        return _regulation(record, request.jurisdiction)
    evaluators: dict[str, Callable[[EvidenceRecord], CriterionResult]] = {
        "soil_ph": _soil,
        "water_availability": _water,
        "slope_percent": _terrain,
        "ecological_sensitivity": _ecology,
    }
    return evaluators[indicator](record)


def assess_pollinator_habitat(
    request: AssessmentRequest,
    *,
    today: date | None = None,
) -> AssessmentResult:
    """Assess one transparent prototype scenario without claiming authorization."""

    current_date = today or datetime.now(timezone.utc).date()
    records = {record.indicator: record for record in request.evidence}
    duplicate_errors: list[str] = []
    indicators = [record.indicator for record in request.evidence]
    evidence_ids = [record.evidence_id for record in request.evidence]
    for indicator in sorted(set(indicators)):
        if indicators.count(indicator) > 1:
            duplicate_errors.append(
                f"{indicator.replace('_', ' ')}: duplicate indicator records require resolution"
            )
    for evidence_id in sorted(set(evidence_ids)):
        if evidence_ids.count(evidence_id) > 1:
            duplicate_errors.append(
                f"{evidence_id or 'blank evidence ID'}: duplicate evidence ID"
            )
    errors_by_indicator = {
        indicator: _validate(record, current_date)
        for indicator, record in records.items()
    }
    validation_errors = tuple(duplicate_errors) + tuple(
        error for errors in errors_by_indicator.values() for error in errors
    )

    domains = ("Soil", "Water", "Terrain", "Ecology", "Regulation")
    criteria = tuple(
        _criterion(domain, indicator, records, errors_by_indicator, request)
        for domain, indicator in zip(domains, EXPECTED_INDICATORS)
    )
    missing_evidence = tuple(
        indicator.replace("_", " ")
        for indicator, result in zip(EXPECTED_INDICATORS, criteria)
        if result.status in {CriterionStatus.MISSING, CriterionStatus.INVALID}
    )

    regulatory_constraint = any(
        result.domain == "Regulation" and result.status is CriterionStatus.CONSTRAINT
        for result in criteria
    )
    has_constraint = any(
        result.status is CriterionStatus.CONSTRAINT for result in criteria
    )
    has_conditional = any(
        result.status is CriterionStatus.CONDITIONAL for result in criteria
    )

    if regulatory_constraint:
        status = AssessmentStatus.NOT_SUPPORTED
        summary = "A supplied regulatory restriction prevents this scenario from advancing through the prototype."
    elif validation_errors or missing_evidence:
        status = AssessmentStatus.INSUFFICIENT
        summary = "The available evidence is not sufficient for a complete prototype assessment."
    elif has_constraint or has_conditional:
        status = AssessmentStatus.CONDITIONAL
        summary = "The scenario may advance only after the identified constraints and review actions are resolved."
    else:
        status = AssessmentStatus.SUPPORTED
        summary = "The supplied evidence supports advancing this scenario to qualified human review."

    review = [
        "A qualified human must review the evidence and conclusion before any consequential action."
    ]
    if any(
        item.domain == "Ecology" and item.status is not CriterionStatus.SUPPORTS
        for item in criteria
    ):
        review.append(
            "Ecological review is required because sensitivity is unresolved or material."
        )
    if any(
        item.domain == "Regulation" and item.status is not CriterionStatus.SUPPORTS
        for item in criteria
    ):
        review.append(
            "Regulatory review is required because applicability is unresolved or constrained."
        )
    if any(
        item.domain == "Terrain" and item.status is not CriterionStatus.SUPPORTS
        for item in criteria
    ):
        review.append(
            "Site review is required for terrain, drainage, and erosion implications."
        )

    return AssessmentResult(
        status=status,
        summary=summary,
        criteria=criteria,
        evidence=request.evidence,
        missing_evidence=missing_evidence,
        validation_errors=validation_errors,
        human_review=tuple(review),
        assumptions=(
            "Reference rules are illustrative prototype logic, not validated scientific thresholds.",
            "Evidence is treated as user supplied and unverified unless separately established.",
            "The assessment addresses decision support, not approval or authorization.",
        ),
    )
