"""Tests for the SVI scoring engine (pure computation)."""

import pytest

from app.vulnerability.engine import (
    CategoryWeight,
    IndicatorData,
    assign_grade,
    calculate_category_score,
    calculate_composite_score,
    calculate_region_scores,
    calculate_risk_index,
    normalize_values,
)
from app.vulnerability.enums import NormalizationMethod


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


class TestCompositeScore:
    def test_equal_weights(self):
        category_scores = {"cat1": 60.0, "cat2": 80.0}
        weights = [
            CategoryWeight("cat1", 0.5),
            CategoryWeight("cat2", 0.5),
        ]
        score = calculate_composite_score(category_scores, weights)
        assert score == 70.0


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
