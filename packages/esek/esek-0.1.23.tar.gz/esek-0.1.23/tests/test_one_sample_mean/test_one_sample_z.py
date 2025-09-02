from src.esek.Calculator.OneSampleMean.one_sample_z import (
    OneSampleZResults,
    OneSampleZTests,
)


def test_one_sample_z_from_score():
    data = {
        "z_score": 1.96,
        "sample_size": 30,
        "confidence_level": 0.95,
    }
    try:
        results = OneSampleZTests.from_score(**data)
    except Exception as e:
        assert False, f"Unexpected error: {e}"

    assert isinstance(results, OneSampleZResults)


def test_one_sample_z_from_parameters():
    data = {
        "sample_mean": 100,
        "sample_size": 30,
        "population_mean": 95,
        "population_sd": 0.5,
        "confidence_level": 0.95,
    }
    try:
        results = OneSampleZTests.from_parameters(**data)
    except Exception as e:
        assert False, f"Unexpected error: {e}"

    assert isinstance(results, OneSampleZResults)


def test_one_sample_z_from_data():
    data = {
        "column": [[1, 2, 3], [4, 5, 6]],
        "population_mean": 95,
        "population_sd": 0.5,
        "confidence_level": 0.95,
    }
    try:
        results = OneSampleZTests.from_data(**data)
    except Exception as e:
        assert False, f"Unexpected error: {e}"

    assert isinstance(results, OneSampleZResults)
