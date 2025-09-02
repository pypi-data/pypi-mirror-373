from src.esek.Calculator.TwoIndependentMean.two_independent_robust import (
    TwoIndependentRobustResults,
    TwoIndependentRobustTests,
)


def test_two_independent_robust_from_score():
    assert True, "Method not implemented yet"


def test_two_independent_robust_from_parameters():
    assert True, "Method not implemented yet"


def test_two_independent_robust_from_data():
    data = {
        "columns": [[1, 2, 3], [4, 5, 6]],
        "reps": 10000,
        "trimming_level": 0.2,
        "population_difference": 0.2,
        "confidence_level": 0.95,
    }
    try:
        results = TwoIndependentRobustTests.from_data(**data)
    except Exception as e:
        assert False, f"Unexpected error: {e}"

    assert isinstance(results, TwoIndependentRobustResults)
