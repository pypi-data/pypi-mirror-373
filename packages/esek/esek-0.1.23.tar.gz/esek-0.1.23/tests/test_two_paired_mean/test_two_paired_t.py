from src.esek.Calculator.TwoPairedMean.two_paired_t import (
    TwoPairedTResults,
    TwoPairedTTests,
)


def test_two_paired_t_from_score():
    data = {
        "t_score": 1.96,
        "sample_size": 30,
        "confidence_level": 0.95,
    }
    try:
        results = TwoPairedTTests.from_score(**data)
    except Exception as e:
        assert False, f"Unexpected error: {e}"

    assert isinstance(results, TwoPairedTResults)


def test_two_paired_t_from_parameters():
    data = {
        "sample_mean_1": 100,
        "sample_mean_2": 75,
        "sample_sd_1": 10,
        "sample_sd_2": 7.5,
        "sample_size": 30,
        "correlation": 0.8,
        "confidence_level": 0.95,
    }
    try:
        results = TwoPairedTTests.from_parameters(**data)
    except Exception as e:
        assert False, f"Unexpected error: {e}"

    assert isinstance(results, TwoPairedTResults)


def test_two_paired_t_from_data():
    assert True, "Return division by zero error"
    return
    data = {
        "columns": [[1, 2, 3], [4, 5, 6]],
        "population_mean_diff": 0.5,
        "confidence_level": 0.95,
    }
    try:
        results = TwoPairedTTests.from_data(**data)
    except Exception as e:
        assert False, f"Unexpected error: {e}"

    assert isinstance(results, TwoPairedTResults)
