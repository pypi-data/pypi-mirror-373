from src.esek.Calculator.TwoIndependentMean.two_independent_unequal_var import (
    TwoIndependentUnequalVarResults,
    TwoIndependentUnequalVarTests,
)


def test_two_independent_unequal_var_from_score():
    assert True, "Method not implemented yet"


def test_two_independent_unequal_var_from_parameters():
    data = {
        "sample_mean_1": 5.0,
        "sample_mean_2": 4.0,
        "sample_sd_1": 1.0,
        "sample_sd_2": 1.0,
        "sample_size_1": 30,
        "sample_size_2": 30,
        "population_mean_diff": 0,
        "confidence_level": 0.95,
    }
    try:
        results = TwoIndependentUnequalVarTests.from_parameters(**data)
    except Exception as e:
        assert False, f"Unexpected error: {e}"

    assert isinstance(results, TwoIndependentUnequalVarResults)


def test_two_independent_unequal_var_from_data():
    data = {
        "columns": [[1, 2, 3], [4, 5, 6]],
        "population_mean_diff": 0,
        "confidence_level": 0.95,
    }
    try:
        results = TwoIndependentUnequalVarTests.from_data(**data)
    except Exception as e:
        assert False, f"Unexpected error: {e}"

    assert isinstance(results, TwoIndependentUnequalVarResults)
