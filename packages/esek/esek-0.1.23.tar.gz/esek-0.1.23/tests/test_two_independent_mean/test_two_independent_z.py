from src.esek.Calculator.TwoIndependentMean.two_independent_z import (
    TwoIndependentZResults,
    TwoIndependentZTests,
)


def test_two_independent_z_from_score():
    data = {
        "z_score": 2.5,
        "sample_size_1": 30,
        "sample_size_2": 30,
        "confidence_level": 0.95,
    }
    try:
        results = TwoIndependentZTests.from_score(**data)
    except Exception as e:
        assert False, f"Unexpected error: {e}"

    assert isinstance(results, TwoIndependentZResults)


def test_two_independent_z_from_parameters():
    data = {
        "sample_mean_1": 5.0,
        "sample_mean_2": 4.0,
        "population_sd_1": 1.0,
        "population_sd_2": 1.0,
        "sample_size_1": 30,
        "sample_size_2": 30,
        "population_diff": 0,
        "confidence_level": 0.95,
    }
    try:
        results = TwoIndependentZTests.from_parameters(**data)
    except Exception as e:
        assert False, f"Unexpected error: {e}"

    assert isinstance(results, TwoIndependentZResults)


def test_two_independent_z_from_data():
    data = {
        "columns": [[1, 2, 3], [4, 5, 6]],
        "population_diff": 0,
        "population_sd_1": 1.0,
        "population_sd_2": 1.0,
        "confidence_level": 0.95,
    }
    try:
        results = TwoIndependentZTests.from_data(**data)
    except Exception as e:
        assert False, f"Unexpected error: {e}"

    assert isinstance(results, TwoIndependentZResults)
