from src.esek.Calculator.TwoIndependentMean.two_independent_control_group import (
    TwoIndependentControlGroupResults,
    TwoIndependentControlGroupTests,
)


def test_two_independent_control_group_from_score():
    assert True, "Method not implemented yet"


def test_two_independent_control_group_from_parameters():
    data = {
        "sample_mean_experimental": 5.0,
        "sample_mean_control": 4.0,
        "sample_sd_experimental": 1.0,
        "sample_sd_control": 1.0,
        "sample_size_experimental": 30,
        "sample_size_control": 30,
        "population_mean_diff": 0,
        "confidence_level": 0.95,
    }
    try:
        results = TwoIndependentControlGroupTests.from_parameters(**data)
    except Exception as e:
        assert False, f"Unexpected error: {e}"

    assert isinstance(results, TwoIndependentControlGroupResults)


def test_two_independent_control_group_from_data():
    data = {
        "columns": [[1, 2, 3, 4], [5, 6, 7, 8]],
        "population_mean_diff": 0,
        "confidence_level": 0.95,
    }
    try:
        results = TwoIndependentControlGroupTests.from_data(**data)
    except Exception as e:
        assert False, f"Unexpected error: {e}"

    assert isinstance(results, TwoIndependentControlGroupResults)
