"""Degrees of Weird v0.1: transparent, *unvalidated* extension-scoring heuristic.

All distance items: 0=identical/near parent brand, 10=far away.
All brand permission items: 0=low, 10=high. Scores are ordinal heuristics.
The shared 0-100 scale is NOT empirically calibrated; do not interpret as
probabilities, literal angles, or statistically established launch thresholds.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Mapping

DISTANCE_WEIGHTS = {
    "brand_meaning": 0.25,
    "consumer_need": 0.20,
    "category": 0.15,
    "credibility": 0.20,
    "audience": 0.10,
    "occasion": 0.10,
}
PERMISSION_WEIGHTS = {
    "equity_strength": 0.30,
    "brand_breadth": 0.25,
    "brand_elasticity": 0.25,
    "extension_precedent": 0.20,
}
DISTANCE_LABELS = {
    "brand_meaning": "Brand meaning distance",
    "consumer_need": "Consumer need distance",
    "category": "Category distance",
    "credibility": "Credibility distance",
    "audience": "Audience distance",
    "occasion": "Occasion distance",
}
PERMISSION_LABELS = {
    "equity_strength": "Equity strength",
    "brand_breadth": "Brand breadth",
    "brand_elasticity": "Brand elasticity",
    "extension_precedent": "Extension precedent",
}
DISTANCE_QUESTIONS = {
    "brand_meaning": "How inconsistent is the extension with what this brand stands for?",
    "consumer_need": "How different is the consumer problem or motivation?",
    "category": "How distant is the category from the brand's current offering?",
    "credibility": "How hard is it to believe the brand can competently deliver?",
    "audience": "How different is the target consumer?",
    "occasion": "How different is the usage/consumption occasion?",
}
PERMISSION_QUESTIONS = {
    "equity_strength": "How strong are trust, quality perceptions, and associations?",
    "brand_breadth": "How broadly do consumers define the brand's expertise?",
    "brand_elasticity": "How receptive are consumers to unfamiliar brand offerings?",
    "extension_precedent": "How credible is the brand's past cross-category track record?",
}

@dataclass(frozen=True)
class ScoreResult:
    scenario: str
    raw_weirdness: float
    bridge_adjustment: float
    effective_weirdness: float
    permission_ceiling: float
    permission_gap: float
    status: str
    top_distance_drivers: tuple[str, ...]
    distance_contributions: dict[str, float]
    permission_contributions: dict[str, float]
    model_version: str = "0.1-unvalidated"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["top_distance_drivers"] = list(self.top_distance_drivers)
        return d


def _check_items(values: Mapping[str, float], weights: Mapping[str, float], field: str) -> None:
    if set(values) != set(weights):
        raise ValueError(f"{field} keys must be {sorted(weights)}; got {sorted(values)}")
    for k, v in values.items():
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not 0 <= v <= 10:
            raise ValueError(f"{field}.{k} must be a number between 0 and 10")


def calculate(
    scenario: str,
    distance: Mapping[str, float],
    permission: Mapping[str, float],
    bridge_adjustment: float = 0,
) -> ScoreResult:
    """Compute raw distance, brand permission, and signed gap on provisional scales.

    Gap > 0 means extension exceeds modeled permission; gap < 0 is headroom.
    Bridge is a clearly labeled *user-specified scenario assumption*, never an
    empirically estimated causal impact.
    """
    if not isinstance(scenario, str) or not scenario.strip():
        raise ValueError("scenario must be a nonempty string")
    _check_items(distance, DISTANCE_WEIGHTS, "distance")
    _check_items(permission, PERMISSION_WEIGHTS, "permission")
    if isinstance(bridge_adjustment, bool) or not isinstance(bridge_adjustment, (int, float)) or not 0 <= bridge_adjustment <= 20:
        raise ValueError("bridge_adjustment must be 0–20")

    distance_contributions = {k: round(10 * distance[k] * w, 2) for k, w in DISTANCE_WEIGHTS.items()}
    permission_contributions = {k: round(10 * permission[k] * w, 2) for k, w in PERMISSION_WEIGHTS.items()}
    raw = round(sum(distance_contributions.values()), 2)
    ceiling = round(sum(permission_contributions.values()), 2)
    effective = round(max(0.0, raw - bridge_adjustment), 2)
    gap = round(effective - ceiling, 2)
    if gap > 15:
        status = "Outside modeled permission"
    elif gap > 0:
        status = "Beyond modeled permission"
    elif gap >= -15:
        status = "Near modeled boundary"
    else:
        status = "Within modeled permission"
    drivers = tuple(sorted(DISTANCE_WEIGHTS, key=lambda k: (-distance_contributions[k], k))[:3])
    return ScoreResult(
        scenario=scenario.strip(), raw_weirdness=raw,
        bridge_adjustment=round(float(bridge_adjustment), 2),
        effective_weirdness=effective, permission_ceiling=ceiling,
        permission_gap=gap, status=status, top_distance_drivers=drivers,
        distance_contributions=distance_contributions,
        permission_contributions=permission_contributions,
    )
