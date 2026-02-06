"""Generate realistic synthetic indicator values for Alberta Census Divisions.

Produces 48 indicators x 19 regions x 3 years (2022-2024) = 2,736 records
with plausible regional variation. Regional profiles ensure at least one
region per KPMG grade (A-E).

Usage:
    python -m scripts.generate_test_data          # prints JSON to stdout
    python -m scripts.generate_test_data --json    # same
    python -m scripts.generate_test_data --sql     # prints SQL INSERT statements

Can also be imported: from scripts.generate_test_data import generate_all_values
"""

import argparse
import json
import random
import uuid
from collections import defaultdict

from app.vulnerability.catalog import (
    CATEGORIES,
    CENSUS_DIVISIONS,
    DATA_SOURCES,
    INDICATORS,
    SVI_NAMESPACE,
)

# Seed for reproducibility
SEED = 42
YEARS = [2022, 2023, 2024]

# ---------------------------------------------------------------------------
# Regional Profiles
# Each Census Division gets a profile that shifts indicator base values up/down.
# Higher multiplier = higher vulnerability.
# ---------------------------------------------------------------------------
REGIONAL_PROFILES: dict[str, dict] = {
    # South Zone
    "CD-01": {"type": "rural_remote", "vulnerability_multiplier": 1.25, "label": "Rural remote (Cardston)"},
    "CD-02": {"type": "mid_urban", "vulnerability_multiplier": 0.80, "label": "Mid-size urban (Lethbridge)"},
    "CD-03": {"type": "rural_agricultural", "vulnerability_multiplier": 1.10, "label": "Rural agricultural (Taber)"},
    "CD-04": {"type": "mid_urban", "vulnerability_multiplier": 0.85, "label": "Mid-size urban (Medicine Hat)"},
    # Calgary Zone
    "CD-05": {"type": "rural_agricultural", "vulnerability_multiplier": 1.15, "label": "Rural (Drumheller)"},
    "CD-06": {"type": "major_urban", "vulnerability_multiplier": 0.55, "label": "Major urban (Calgary)"},
    "CD-15": {"type": "mountain_rural", "vulnerability_multiplier": 0.95, "label": "Mountain rural (Banff-RMH)"},
    # Central Zone
    "CD-07": {"type": "rural_agricultural", "vulnerability_multiplier": 1.05, "label": "Rural (Stettler-Ponoka)"},
    "CD-08": {"type": "mid_urban", "vulnerability_multiplier": 0.75, "label": "Mid-size urban (Red Deer)"},
    "CD-09": {"type": "rural_remote", "vulnerability_multiplier": 1.20, "label": "Rural remote (Wainwright)"},
    # Edmonton Zone
    "CD-10": {"type": "rural_agricultural", "vulnerability_multiplier": 1.00, "label": "Rural (Camrose)"},
    "CD-11": {"type": "major_urban", "vulnerability_multiplier": 0.60, "label": "Major urban (Edmonton)"},
    # North Zone
    "CD-12": {"type": "rural_northern", "vulnerability_multiplier": 1.10, "label": "Rural northern (Barrhead)"},
    "CD-13": {"type": "rural_agricultural", "vulnerability_multiplier": 1.05, "label": "Rural (Lloydminster)"},
    "CD-14": {"type": "rural_remote", "vulnerability_multiplier": 1.30, "label": "Rural remote (Edson-Hinton)"},
    "CD-16": {"type": "northern_remote", "vulnerability_multiplier": 1.45, "label": "Northern remote (Athabasca)"},
    "CD-17": {"type": "northern_resource", "vulnerability_multiplier": 1.35, "label": "Northern resource (Wood Buffalo)"},
    "CD-18": {"type": "northern_urban_rural", "vulnerability_multiplier": 1.15, "label": "Northern mixed (Grande Prairie)"},
    "CD-19": {"type": "northern_remote", "vulnerability_multiplier": 1.60, "label": "Northern remote (High Level)"},
}

# ---------------------------------------------------------------------------
# Base values per indicator (provincial averages / typical Alberta values)
# For inverse indicators, the base represents the "good" value (e.g., high income).
# ---------------------------------------------------------------------------
INDICATOR_BASES: dict[str, dict] = {
    # Socioeconomic
    "unemployment_rate":          {"base": 7.5,  "std": 2.5,  "trend": -0.3},
    "low_income_rate":            {"base": 10.0, "std": 3.5,  "trend": 0.2},
    "no_high_school_diploma":     {"base": 12.0, "std": 5.0,  "trend": -0.5},
    "median_household_income":    {"base": 100.0,"std": 15.0, "trend": 1.0},  # inverse: % of provincial median
    "government_transfer_rate":   {"base": 12.0, "std": 4.0,  "trend": 0.3},
    "income_assistance_rate":     {"base": 4.5,  "std": 2.0,  "trend": 0.1},
    "gini_coefficient":           {"base": 33.0, "std": 3.0,  "trend": 0.2},
    "food_insecurity_rate":       {"base": 14.0, "std": 4.0,  "trend": 0.5},
    # Demographic
    "seniors_65_plus":            {"base": 16.5, "std": 4.0,  "trend": 0.5},
    "children_under_5":           {"base": 5.5,  "std": 1.2,  "trend": -0.1},
    "indigenous_identity":        {"base": 6.5,  "std": 8.0,  "trend": 0.1},
    "recent_immigrants":          {"base": 4.0,  "std": 3.5,  "trend": 0.3},
    "lone_parent_families":       {"base": 16.0, "std": 3.0,  "trend": 0.1},
    "visible_minority":           {"base": 20.0, "std": 15.0, "trend": 1.0},
    "no_official_language":       {"base": 1.5,  "std": 1.5,  "trend": 0.1},
    "living_alone_65_plus":       {"base": 26.0, "std": 5.0,  "trend": 0.3},
    # Health
    "life_expectancy":            {"base": 100.0,"std": 4.0,  "trend": -0.2},  # inverse: % of provincial avg
    "self_rated_health_poor":     {"base": 12.0, "std": 3.0,  "trend": 0.3},
    "mental_health_hospitalizations": {"base": 5.0, "std": 2.0, "trend": 0.2},
    "substance_use_hospitalizations": {"base": 4.0, "std": 2.5, "trend": 0.4},
    "opioid_poisoning_rate":      {"base": 20.0, "std": 12.0, "trend": 2.0},
    "no_family_doctor":           {"base": 22.0, "std": 8.0,  "trend": 1.0},
    "disability_rate":            {"base": 22.0, "std": 4.0,  "trend": 0.2},
    "premature_mortality_rate":   {"base": 280.0,"std": 60.0, "trend": 5.0},
    # Housing
    "core_housing_need":          {"base": 10.0, "std": 3.0,  "trend": 0.5},
    "housing_cost_burden":        {"base": 22.0, "std": 5.0,  "trend": 0.8},
    "homelessness_rate":          {"base": 8.0,  "std": 5.0,  "trend": 0.5},
    "crowded_housing":            {"base": 5.0,  "std": 3.0,  "trend": 0.2},
    "shelter_bed_capacity":       {"base": 5.0,  "std": 3.0,  "trend": 0.1},  # inverse
    "rental_vacancy_rate":        {"base": 4.0,  "std": 2.0,  "trend": -0.3}, # inverse
    "housing_condition_major_repair": {"base": 7.0, "std": 3.0, "trend": 0.1},
    "shelter_occupancy_rate":     {"base": 75.0, "std": 12.0, "trend": 2.0},
    # Infrastructure
    "no_vehicle":                 {"base": 8.0,  "std": 5.0,  "trend": -0.2},
    "commute_over_60min":         {"base": 8.0,  "std": 4.0,  "trend": 0.2},
    "no_internet":                {"base": 6.0,  "std": 5.0,  "trend": -0.5},
    "public_transit_access":      {"base": 50.0, "std": 30.0, "trend": 1.0},  # inverse
    "distance_to_hospital":       {"base": 50.0, "std": 25.0, "trend": 0.0},
    "rural_population_pct":       {"base": 30.0, "std": 25.0, "trend": -0.5},
    "childcare_availability":     {"base": 35.0, "std": 12.0, "trend": 1.0},  # inverse
    "social_services_proximity":  {"base": 70.0, "std": 20.0, "trend": 0.5},  # inverse
    # Environmental
    "violent_crime_rate":         {"base": 120.0,"std": 60.0, "trend": 3.0},
    "property_crime_rate":        {"base": 450.0,"std": 150.0,"trend": -5.0},
    "domestic_violence_rate":     {"base": 50.0, "std": 25.0, "trend": 1.0},
    "flood_risk_area":            {"base": 8.0,  "std": 6.0,  "trend": 0.2},
    "wildfire_risk":              {"base": 12.0, "std": 15.0, "trend": 1.0},
    "emergency_shelter_calls":    {"base": 12.0, "std": 8.0,  "trend": 0.5},
    "child_intervention_rate":    {"base": 10.0, "std": 5.0,  "trend": 0.3},
    "extreme_weather_events":     {"base": 3.0,  "std": 2.0,  "trend": 0.3},
}

# Category-specific adjustments by regional type
# Multiplier applied on top of the base vulnerability_multiplier
TYPE_CATEGORY_ADJUSTMENTS: dict[str, dict[str, float]] = {
    "major_urban": {
        "socioeconomic": 0.85, "demographic": 1.1, "health": 0.9,
        "housing": 1.3, "infrastructure": 0.5, "environmental": 0.9,
    },
    "mid_urban": {
        "socioeconomic": 0.9, "demographic": 0.95, "health": 0.95,
        "housing": 1.0, "infrastructure": 0.7, "environmental": 0.9,
    },
    "rural_agricultural": {
        "socioeconomic": 1.05, "demographic": 1.1, "health": 1.05,
        "housing": 0.85, "infrastructure": 1.3, "environmental": 0.9,
    },
    "rural_remote": {
        "socioeconomic": 1.15, "demographic": 1.15, "health": 1.15,
        "housing": 0.9, "infrastructure": 1.5, "environmental": 1.1,
    },
    "mountain_rural": {
        "socioeconomic": 0.9, "demographic": 0.85, "health": 0.9,
        "housing": 1.1, "infrastructure": 1.2, "environmental": 1.3,
    },
    "rural_northern": {
        "socioeconomic": 1.1, "demographic": 1.15, "health": 1.1,
        "housing": 0.95, "infrastructure": 1.4, "environmental": 1.1,
    },
    "northern_remote": {
        "socioeconomic": 1.3, "demographic": 1.3, "health": 1.3,
        "housing": 1.0, "infrastructure": 1.6, "environmental": 1.3,
    },
    "northern_resource": {
        "socioeconomic": 0.95, "demographic": 1.2, "health": 1.25,
        "housing": 1.2, "infrastructure": 1.3, "environmental": 1.2,
    },
    "northern_urban_rural": {
        "socioeconomic": 1.0, "demographic": 1.1, "health": 1.1,
        "housing": 1.0, "infrastructure": 1.2, "environmental": 1.1,
    },
}

# Build indicator -> category name lookup
_IND_TO_CAT: dict[str, str] = {}
_CAT_ID_TO_NAME: dict[str, str] = {c["id"]: c["name"] for c in CATEGORIES}
for ind in INDICATORS:
    _IND_TO_CAT[ind["name"]] = _CAT_ID_TO_NAME[ind["category_id"]]


def _value_id(indicator_name: str, region_code: str, year: int) -> str:
    """Deterministic UUID for an indicator value."""
    return str(uuid.uuid5(SVI_NAMESPACE, f"val:{indicator_name}:{region_code}:{year}"))


def _score_id(region_code: str, year: int) -> str:
    """Deterministic UUID for an SVI score."""
    return str(uuid.uuid5(SVI_NAMESPACE, f"score:{region_code}:{year}"))


def generate_indicator_value(
    indicator_name: str,
    region_code: str,
    year: int,
    rng: random.Random,
) -> float:
    """Generate a single indicator value for a region/year."""
    base_info = INDICATOR_BASES[indicator_name]
    profile = REGIONAL_PROFILES[region_code]

    base = base_info["base"]
    std = base_info["std"]
    trend = base_info["trend"]
    vuln_mult = profile["vulnerability_multiplier"]
    region_type = profile["type"]

    # Category-specific adjustment
    category = _IND_TO_CAT[indicator_name]
    cat_adj = TYPE_CATEGORY_ADJUSTMENTS.get(region_type, {}).get(category, 1.0)

    # Check if this indicator is inverse
    ind_meta = next(i for i in INDICATORS if i["name"] == indicator_name)
    is_inverse = ind_meta.get("is_inverse", False)

    # For inverse indicators, higher vulnerability = LOWER values
    if is_inverse:
        effective_mult = 1.0 / (vuln_mult * cat_adj)
    else:
        effective_mult = vuln_mult * cat_adj

    # Year trend (relative to 2023 baseline)
    year_offset = (year - 2023) * trend

    # Generate value with noise
    noise = rng.gauss(0, std * 0.3)
    value = (base * effective_mult) + year_offset + noise

    # Clamp to reasonable range (non-negative; percentages capped at 100)
    value = max(0.0, value)
    unit = ind_meta.get("unit", "")
    if unit == "%" or "% of" in unit:
        value = min(100.0, value)

    return round(value, 2)


def generate_all_values(seed: int = SEED) -> list[dict]:
    """Generate all indicator values for all regions/years."""
    rng = random.Random(seed)
    values = []

    for year in YEARS:
        for cd in CENSUS_DIVISIONS:
            for ind in INDICATORS:
                val = generate_indicator_value(ind["name"], cd["code"], year, rng)
                # Find the data source record for this indicator
                data_source_id = ind.get("data_source")

                values.append({
                    "id": _value_id(ind["name"], cd["code"], year),
                    "indicator_id": ind["id"],
                    "region_id": cd["id"],
                    "data_source_id": data_source_id,
                    "value": val,
                    "year": year,
                    "metadata_json": {"synthetic": True, "seed": seed},
                })

    return values


def compute_svi_scores(values: list[dict], seed: int = SEED) -> list[dict]:
    """Compute SVI scores from indicator values using the engine logic.

    Reimplements the scoring inline to avoid DB dependency.
    """
    from app.vulnerability.engine import (
        CategoryWeight,
        IndicatorData,
        calculate_region_scores,
        normalize_values,
    )
    from app.vulnerability.enums import NormalizationMethod

    # Build lookups
    ind_lookup = {i["id"]: i for i in INDICATORS}
    cat_lookup = {c["id"]: c for c in CATEGORIES}
    cd_lookup = {cd["id"]: cd for cd in CENSUS_DIVISIONS}
    category_weights = [
        CategoryWeight(name=c["name"], weight=float(c["weight"])) for c in CATEGORIES
    ]

    scores = []

    for year in YEARS:
        # Filter values for this year
        year_values = [v for v in values if v["year"] == year]

        # Group by indicator for normalization
        by_indicator: dict[str, list[dict]] = defaultdict(list)
        for v in year_values:
            by_indicator[v["indicator_id"]].append(v)

        # Normalize each indicator across regions
        normalized: dict[str, dict[str, float]] = defaultdict(dict)  # region_id -> {ind_id: norm}

        for ind_id, vals in by_indicator.items():
            ind = ind_lookup.get(ind_id)
            if not ind:
                continue
            raw = [v["value"] for v in vals]
            norm = normalize_values(raw, NormalizationMethod.MIN_MAX, ind.get("is_inverse", False))

            for v, n in zip(vals, norm):
                normalized[v["region_id"]][ind_id] = n

        # Calculate scores per region
        for region_id, norm_vals in normalized.items():
            cd = cd_lookup.get(region_id)
            if not cd:
                continue

            # Build IndicatorData grouped by category
            ind_by_cat: dict[str, list[IndicatorData]] = defaultdict(list)
            for ind in INDICATORS:
                if ind["id"] in norm_vals:
                    cat_name = cat_lookup[ind["category_id"]]["name"]
                    ind_by_cat[cat_name].append(
                        IndicatorData(
                            indicator_id=ind["id"],
                            indicator_name=ind["name"],
                            category=cat_name,
                            value=norm_vals[ind["id"]],
                            weight=1.0,  # equal weight within category
                            is_inverse=ind.get("is_inverse", False),
                        )
                    )

            region_score = calculate_region_scores(
                region_id, ind_by_cat, norm_vals, category_weights
            )

            scores.append({
                "id": _score_id(cd["code"], year),
                "region_id": region_id,
                "year": year,
                "composite_score": region_score.composite_score,
                "grade": region_score.grade,
                "category_scores": region_score.category_scores,
                "normalization_method": "min_max",
                "calculation_metadata": {
                    "synthetic": True,
                    "seed": seed,
                    "indicators_count": len(norm_vals),
                },
            })

    return scores


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic SVI test data")
    parser.add_argument("--sql", action="store_true", help="Output SQL INSERT statements")
    parser.add_argument("--json", action="store_true", default=True, help="Output JSON (default)")
    parser.add_argument("--seed", type=int, default=SEED, help="Random seed")
    args = parser.parse_args()

    values = generate_all_values(args.seed)
    scores = compute_svi_scores(values, args.seed)

    if args.sql:
        for v in values:
            meta = json.dumps(v["metadata_json"]).replace("'", "''")
            print(
                f"INSERT INTO indicator_values (id, indicator_id, region_id, data_source_id, value, year, metadata_json) "
                f"VALUES ('{v['id']}', '{v['indicator_id']}', '{v['region_id']}', "
                f"'{v['data_source_id']}', {v['value']}, {v['year']}, '{meta}');"
            )
        for s in scores:
            cat_json = json.dumps(s["category_scores"]).replace("'", "''")
            meta = json.dumps(s["calculation_metadata"]).replace("'", "''")
            print(
                f"INSERT INTO svi_scores (id, region_id, year, composite_score, grade, "
                f"category_scores, normalization_method, calculation_metadata) "
                f"VALUES ('{s['id']}', '{s['region_id']}', {s['year']}, "
                f"{s['composite_score']}, '{s['grade']}', '{cat_json}', "
                f"'{s['normalization_method']}', '{meta}');"
            )
    else:
        output = {
            "indicator_values": values,
            "svi_scores": scores,
            "summary": {
                "total_values": len(values),
                "total_scores": len(scores),
                "years": YEARS,
                "regions": len(CENSUS_DIVISIONS),
                "indicators": len(INDICATORS),
            },
        }
        print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
