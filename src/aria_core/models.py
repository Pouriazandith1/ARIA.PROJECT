"""Typed contracts for ARIA's evidence-first prototype."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Any


class AssessmentStatus(str, Enum):
    """Decision-support states, ordered by consequence rather than score."""

    SUPPORTED = "Supported for review"
    CONDITIONAL = "Conditional"
    INSUFFICIENT = "Insufficient evidence"
    NOT_SUPPORTED = "Not supported"


class CriterionStatus(str, Enum):
    """Status of one bounded domain finding."""

    SUPPORTS = "Supports"
    CONDITIONAL = "Conditional"
    CONSTRAINT = "Constraint"
    MISSING = "Missing"
    INVALID = "Invalid"


@dataclass(frozen=True)
class EvidenceRecord:
    """A value plus the metadata required to trace and review it."""

    evidence_id: str
    indicator: str
    value: Any
    unit: str
    source: str
    observed_on: date
    location: str
    method: str = "User supplied"
    quality: str = "Unverified"
    notes: str = ""


@dataclass(frozen=True)
class AssessmentRequest:
    """A bounded question and the evidence offered to answer it."""

    activity: str
    location: str
    jurisdiction: str
    evidence: tuple[EvidenceRecord, ...]


@dataclass(frozen=True)
class CriterionResult:
    """One explainable domain finding."""

    domain: str
    status: CriterionStatus
    finding: str
    evidence_ids: tuple[str, ...] = ()
    uncertainty: str = ""
    next_action: str = ""


@dataclass(frozen=True)
class AssessmentResult:
    """An assessment that keeps evidence, gaps, and review visible."""

    status: AssessmentStatus
    summary: str
    criteria: tuple[CriterionResult, ...]
    evidence: tuple[EvidenceRecord, ...]
    missing_evidence: tuple[str, ...] = ()
    validation_errors: tuple[str, ...] = ()
    human_review: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = field(default_factory=tuple)

    @property
    def uncertainty(self) -> str:
        if self.validation_errors or self.missing_evidence:
            return "High"
        if any(item.status is not CriterionStatus.SUPPORTS for item in self.criteria):
            return "Moderate"
        if any(
            item.quality.strip().lower() not in {"verified", "validated"}
            for item in self.evidence
        ):
            return "Moderate"
        return "Low"
