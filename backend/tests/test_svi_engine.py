"""Tests for the SVI scoring engine (pure computation)."""

from collections import defaultdict

import pytest

from app.vulnerability.engine import (
    CategoryWeight,
    IndicatorData,
    ValidationResult,
    ValidationWarning,
    assign_grade,
    calculate_category_score,
    calculate_composite_score,
    calculate_region_scores,
    calculate_risk_index,
    normalize_values,
    validate_indicator_values,
)
from app.vulnerability.enums import IndicatorCategoryName, NormalizationMethod


class TestNormalization:
    def test_min_max_basic(self):
        values = [10.0, 20.0, 30.0, 40.0, 50.0]
        result = normalize_values(values, NormalizationMethod.MIN_MAX)
        assert result[0] == 0.0
        assert result[-1] == 100.0

    def test_min_max_inverse(self):
        values = [10.0, 20.0, 30.0]
        result = normalize_values(values, NormalizationMethod.MIN_MAX, is_inverse=True)
        assert result[0] == 100.0
        assert result[-1] == 0.0

    def test_min_max_identical_values(self):
        values = [5.0, 5.0, 5.0]
        result = normalize_values(values, NormalizationMethod.MIN_MAX)
        assert all(v == 50.0 for v in result)

    def test_z_score(self):
        values = [10.0, 20.0, 30.0, 40.0, 50.0]
        result = normalize_values(values, NormalizationMethod.Z_SCORE)
        assert len(result) == 5
        assert all(0 <= v <= 100 for v in result)

    def test_percentile(self):
        values = [10.0, 20.0, 30.0, 40.0, 50.0]
        result = normalize_values(values, NormalizationMethod.PERCENTILE)
        assert result[0] == 0.0
        assert result[-1] == 100.0

    def test_empty_values(self):
        assert normalize_values([]) == []

    def test_min_max_two_values(self):
        values = [25.0, 75.0]
        result = normalize_values(values, NormalizationMethod.MIN_MAX)
        assert result[0] == 0.0
        assert result[1] == 100.0

    def test_min_max_preserves_order(self):
        values = [50.0, 10.0, 90.0, 30.0, 70.0]
        result = normalize_values(values, NormalizationMethod.MIN_MAX)
        # Relative ordering should be preserved
        assert result[2] == 100.0  # 90 is max
        assert result[1] == 0.0    # 10 is min


class TestCategoryScore:
    def test_equal_weights(self):
        indicators = [
            IndicatorData("i1", "ind1", "cat1", 80.0, 1.0, False),
            IndicatorData("i2", "ind2", "cat1", 60.0, 1.0, False),
        ]
        normalized = {"i1": 80.0, "i2": 60.0}
        score = calculate_category_score(indicators, normalized)
        assert score == 70.0

    def test_weighted(self):
        indicators = [
            IndicatorData("i1", "ind1", "cat1", 100.0, 3.0, False),
            IndicatorData("i2", "ind2", "cat1", 0.0, 1.0, False),
        ]
        normalized = {"i1": 100.0, "i2": 0.0}
        score = calculate_category_score(indicators, normalized)
        assert score == 75.0

    def test_eight_indicators_equal_weight(self):
        """Test with 8 equally-weighted indicators (matching our catalog structure)."""
        indicators = [
            IndicatorData(f"i{i}", f"ind{i}", "socioeconomic", float(i * 10), 1.0, False)
            for i in range(1, 9)
        ]
        normalized = {f"i{i}": float(i * 10) for i in range(1, 9)}
        score = calculate_category_score(indicators, normalized)
        # Mean of 10,20,30,40,50,60,70,80 = 45.0
        assert score == 45.0

    def test_missing_normalized_value_treated_as_zero(self):
        indicators = [
            IndicatorData("i1", "ind1", "cat1", 80.0, 1.0, False),
            IndicatorData("i2", "ind2", "cat1", 60.0, 1.0, False),
        ]
        normalized = {"i1": 80.0}  # i2 is missing
        score = calculate_category_score(indicators, normalized)
        assert score == 40.0  # (80 + 0) / 2


class TestCompositeScore:
    def test_equal_weights(self):
        category_scores = {"cat1": 60.0, "cat2": 80.0}
        weights = [
            CategoryWeight("cat1", 0.5),
            CategoryWeight("cat2", 0.5),
        ]
        score = calculate_composite_score(category_scores, weights)
        assert score == 70.0

    def test_six_categories_equal_weight(self):
        """Test with 6 categories at 1/6 weight each (matching our SVI structure)."""
        category_scores = {
            "socioeconomic": 30.0,
            "demographic": 40.0,
            "health": 50.0,
            "housing": 60.0,
            "infrastructure": 70.0,
            "environmental": 80.0,
        }
        weight = 1.0 / 6.0
        weights = [
            CategoryWeight(name, weight) for name in category_scores
        ]
        score = calculate_composite_score(category_scores, weights)
        expected = sum(category_scores.values()) / 6.0  # 55.0
        assert abs(score - expected) < 0.01

    def test_zero_weights(self):
        weights = [CategoryWeight("cat1", 0.0)]
        score = calculate_composite_score({"cat1": 50.0}, weights)
        assert score == 0.0


class TestGrading:
    def test_grade_a(self):
        assert assign_grade(15.0) == "A"

    def test_grade_b(self):
        assert assign_grade(35.0) == "B"

    def test_grade_c(self):
        assert assign_grade(55.0) == "C"

    def test_grade_d(self):
        assert assign_grade(75.0) == "D"

    def test_grade_e(self):
        assert assign_grade(90.0) == "E"

    def test_grade_boundaries(self):
        """Test exact boundary values."""
        assert assign_grade(0.0) == "A"
        assert assign_grade(19.99) == "A"
        assert assign_grade(20.0) == "B"
        assert assign_grade(39.99) == "B"
        assert assign_grade(40.0) == "C"
        assert assign_grade(59.99) == "C"
        assert assign_grade(60.0) == "D"
        assert assign_grade(79.99) == "D"
        assert assign_grade(80.0) == "E"
        assert assign_grade(100.0) == "E"


class TestRiskIndex:
    def test_calculation(self):
        risk = calculate_risk_index(
            vulnerability_index=80.0,
            resources_score=60.0,
            pressure_score=70.0,
            funding_score=50.0,
        )
        expected = 0.4 * 80 + 0.2 * 60 + 0.2 * 70 + 0.2 * 50
        assert risk == expected

    def test_all_zeros(self):
        risk = calculate_risk_index(0.0, 0.0, 0.0, 0.0)
        assert risk == 0.0

    def test_all_maximum(self):
        risk = calculate_risk_index(100.0, 100.0, 100.0, 100.0)
        assert risk == 100.0


class TestValidation:
    def test_valid_percentage_indicators(self):
        indicators = [
            IndicatorData("i1", "unemployment_rate", "socioeconomic", 7.5, 1.0, False),
            IndicatorData("i2", "low_income_rate", "socioeconomic", 12.0, 1.0, False),
        ]
        result = validate_indicator_values(indicators)
        assert result.is_valid
        assert len(result.warnings) == 0
        assert len(result.errors) == 0

    def test_negative_value_error(self):
        indicators = [
            IndicatorData("i1", "unemployment_rate", "socioeconomic", -5.0, 1.0, False),
        ]
        result = validate_indicator_values(indicators)
        assert not result.is_valid
        assert len(result.errors) == 1
        assert "Negative" in result.errors[0].message

    def test_over_100_warning(self):
        indicators = [
            IndicatorData("i1", "unemployment_rate", "socioeconomic", 105.0, 1.0, False),
        ]
        result = validate_indicator_values(indicators)
        assert result.is_valid  # warnings don't invalidate
        assert len(result.warnings) == 1
        assert "exceeds 100" in result.warnings[0].message

    def test_rate_indicators_can_exceed_100(self):
        """Per-capita rate indicators (per 100,000) can legitimately exceed 100."""
        indicators = [
            IndicatorData("i1", "violent_crime_rate", "environmental", 250.0, 1.0, False),
        ]
        # Only check named percentage indicators, not all
        pct_indicators = {"unemployment_rate", "low_income_rate"}
        result = validate_indicator_values(indicators, percentage_indicators=pct_indicators)
        assert result.is_valid
        assert len(result.warnings) == 0

    def test_mixed_valid_and_invalid(self):
        indicators = [
            IndicatorData("i1", "unemployment_rate", "socioeconomic", 7.5, 1.0, False),
            IndicatorData("i2", "low_income_rate", "socioeconomic", -3.0, 1.0, False),
            IndicatorData("i3", "no_high_school_diploma", "socioeconomic", 150.0, 1.0, False),
        ]
        result = validate_indicator_values(indicators)
        assert not result.is_valid
        assert len(result.errors) == 1
        assert len(result.warnings) == 1


class TestFullScoringPipeline:
    """Test the complete scoring flow with 48 indicators across 6 categories."""

    def _build_indicators_by_category(
        self, scores_per_category: dict[str, list[float]]
    ) -> tuple[dict[str, list[IndicatorData]], dict[str, float], list[CategoryWeight]]:
        """Helper to build test data for full pipeline."""
        indicators_by_category: dict[str, list[IndicatorData]] = {}
        normalized_values: dict[str, float] = {}

        for cat_name, values in scores_per_category.items():
            indicators = []
            for i, val in enumerate(values):
                ind_id = f"{cat_name}_{i}"
                indicators.append(
                    IndicatorData(
                        indicator_id=ind_id,
                        indicator_name=f"{cat_name}_indicator_{i}",
                        category=cat_name,
                        value=val,
                        weight=1.0,
                        is_inverse=False,
                    )
                )
                normalized_values[ind_id] = val
            indicators_by_category[cat_name] = indicators

        weight = 1.0 / 6.0
        category_weights = [
            CategoryWeight(name, weight)
            for name in IndicatorCategoryName
        ]

        return indicators_by_category, normalized_values, category_weights

    def test_48_indicators_low_vulnerability(self):
        """Region with all low indicator values -> Grade A."""
        scores = {cat.value: [10.0] * 8 for cat in IndicatorCategoryName}
        ind_by_cat, norm_vals, weights = self._build_indicators_by_category(scores)

        result = calculate_region_scores("region_low", ind_by_cat, norm_vals, weights)
        assert result.grade == "A"
        assert result.composite_score == 10.0

    def test_48_indicators_high_vulnerability(self):
        """Region with all high indicator values -> Grade E."""
        scores = {cat.value: [90.0] * 8 for cat in IndicatorCategoryName}
        ind_by_cat, norm_vals, weights = self._build_indicators_by_category(scores)

        result = calculate_region_scores("region_high", ind_by_cat, norm_vals, weights)
        assert result.grade == "E"
        assert result.composite_score == 90.0

    def test_48_indicators_mixed(self):
        """Region with mixed values across categories."""
        scores = {
            "socioeconomic": [20.0] * 8,    # low
            "demographic": [35.0] * 8,       # below avg
            "health": [55.0] * 8,            # average
            "housing": [65.0] * 8,           # above avg
            "infrastructure": [75.0] * 8,    # above avg
            "environmental": [45.0] * 8,     # average
        }
        ind_by_cat, norm_vals, weights = self._build_indicators_by_category(scores)

        result = calculate_region_scores("region_mixed", ind_by_cat, norm_vals, weights)
        # Expected: mean of 20,35,55,65,75,45 = 49.17
        assert 49.0 <= result.composite_score <= 50.0
        assert result.grade == "C"

        # Verify individual category scores
        assert result.category_scores["socioeconomic"] == 20.0
        assert result.category_scores["housing"] == 65.0

    def test_48_indicators_grade_distribution(self):
        """Verify we can produce all 5 grades A-E."""
        grade_inputs = {
            "A": 10.0,
            "B": 30.0,
            "C": 50.0,
            "D": 70.0,
            "E": 90.0,
        }
        for expected_grade, value in grade_inputs.items():
            scores = {cat.value: [value] * 8 for cat in IndicatorCategoryName}
            ind_by_cat, norm_vals, weights = self._build_indicators_by_category(scores)
            result = calculate_region_scores(
                f"region_{expected_grade}", ind_by_cat, norm_vals, weights
            )
            assert result.grade == expected_grade, (
                f"Expected grade {expected_grade} for value {value}, got {result.grade}"
            )

    def test_inverse_indicator_handling(self):
        """Inverse indicators: higher raw value -> lower vulnerability after normalization."""
        # Simulate 19 regions with income data (inverse indicator)
        raw_incomes = [
            60.0, 65.0, 70.0, 75.0, 80.0, 85.0, 90.0, 95.0, 100.0, 105.0,
            110.0, 115.0, 120.0, 125.0, 130.0, 135.0, 140.0, 145.0, 150.0,
        ]

        # Normalize with is_inverse=True: highest income -> lowest score
        normalized = normalize_values(raw_incomes, NormalizationMethod.MIN_MAX, is_inverse=True)

        # Highest income (150) should get lowest normalized score (0)
        assert normalized[-1] == 0.0
        # Lowest income (60) should get highest normalized score (100)
        assert normalized[0] == 100.0
        # Monotonically decreasing
        for i in range(len(normalized) - 1):
            assert normalized[i] >= normalized[i + 1]


class TestSyntheticDataScoring:
    """Test scoring with data generated by the test data generator."""

    def test_generated_data_produces_valid_scores(self):
        """Verify synthetic data from the generator produces valid SVI scores."""
        from scripts.generate_test_data import compute_svi_scores, generate_all_values

        values = generate_all_values()
        scores = compute_svi_scores(values)

        # Should have 19 regions x 3 years = 57 scores
        assert len(scores) == 57

        # All scores should be in valid range
        for s in scores:
            assert 0 <= s["composite_score"] <= 100, (
                f"Score {s['composite_score']} out of range for region {s['region_id']}"
            )
            assert s["grade"] in {"A", "B", "C", "D", "E"}
            assert len(s["category_scores"]) == 6

        # Verify grade distribution: should have at least 3 different grades
        grades_2024 = {s["grade"] for s in scores if s["year"] == 2024}
        assert len(grades_2024) >= 3, (
            f"Expected at least 3 distinct grades, got {grades_2024}"
        )

    def test_generated_values_count(self):
        """Verify correct number of generated indicator values."""
        from scripts.generate_test_data import generate_all_values

        values = generate_all_values()
        # 48 indicators x 19 regions x 3 years = 2,736
        assert len(values) == 2736

    def test_generated_data_reproducible(self):
        """Verify same seed produces identical data."""
        from scripts.generate_test_data import generate_all_values

        values1 = generate_all_values(seed=42)
        values2 = generate_all_values(seed=42)

        for v1, v2 in zip(values1, values2):
            assert v1["id"] == v2["id"]
            assert v1["value"] == v2["value"]

    def test_urban_vs_remote_vulnerability(self):
        """Major urban centres should generally score lower than remote areas."""
        from scripts.generate_test_data import compute_svi_scores, generate_all_values
        from app.vulnerability.catalog import _id

        values = generate_all_values()
        scores = compute_svi_scores(values)

        # Get 2024 scores
        scores_2024 = {s["region_id"]: s for s in scores if s["year"] == 2024}

        calgary_id = _id("cd:06")
        high_level_id = _id("cd:19")

        calgary_score = scores_2024[calgary_id]["composite_score"]
        high_level_score = scores_2024[high_level_id]["composite_score"]

        # High Level (remote northern) should be more vulnerable than Calgary
        assert high_level_score > calgary_score, (
            f"Expected High Level ({high_level_score}) > Calgary ({calgary_score})"
        )
