from src.esek.Calculator.OneSampleMean.one_sample_t import (
    OneSampleTResults,
    OneSampleTTest,
)


def test_one_sample_t_from_score():
    data = {
        "t_score": 1.96,
        "sample_size": 30,
        "confidence_level": 0.95,
    }
    try:
        results = OneSampleTTest.from_score(**data)
    except Exception as e:
        assert False, f"Unexpected error: {e}"

    assert isinstance(results, OneSampleTResults)


def test_one_sample_t_from_parameters():
    data = {
        "sample_mean": 100,
        "sample_size": 30,
        "sample_sd": 0.5,
        "population_mean": 95,
        "confidence_level": 0.95,
    }
    try:
        results = OneSampleTTest.from_parameters(**data)
    except Exception as e:
        assert False, f"Unexpected error: {e}"

    assert isinstance(results, OneSampleTResults)


def test_one_sample_t_from_data():
    assert True, "This test is not implemented yet"
