from src.esek.Calculator.TwoPairedMean.two_paired_z import (
    TwoPairedZResults,
    TwoPairedZTests,
)


def test_two_paired_z_from_score():
    data = {
        "z_score": 1.96,
        "sample_size": 30,
        "confidence_level": 0.95,
    }
    try:
        results = TwoPairedZTests.from_score(**data)
    except Exception as e:
        assert False, f"Unexpected error: {e}"

    assert isinstance(results, TwoPairedZResults)


def test_two_paired_z_from_parameters():
    data = {
        "sample_mean_1": 100,
        "sample_mean_2": 75,
        "sample_size": 30,
        "population_diff": 5,
        "population_diff_sd": 0.5,
        "confidence_level": 0.95,
    }
    try:
        results = TwoPairedZTests.from_parameters(**data)
    except Exception as e:
        assert False, f"Unexpected error: {e}"

    assert isinstance(results, TwoPairedZResults)


def test_two_paired_z_from_data():
    data = {
        "columns": [[1, 2, 3], [4, 5, 6]],
        "population_diff": 5,
        "population_diff_sd": 0.5,
        "confidence_level": 0.95,
    }
    try:
        results = TwoPairedZTests.from_data(**data)
    except Exception as e:
        assert False, f"Unexpected error: {e}"

    assert isinstance(results, TwoPairedZResults)
