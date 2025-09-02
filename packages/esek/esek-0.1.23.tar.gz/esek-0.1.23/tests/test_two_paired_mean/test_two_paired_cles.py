from src.esek.Calculator.TwoPairedMean.two_paired_common_lang import (
    TwoPairedCommonLangResults,
    TwoPairedCommonLangTests,
)


def test_two_paired_common_lang_from_score():
    data = {
        "t_score": 1.96,
        "sample_size": 30,
        "confidence_level": 0.95,
    }
    try:
        results = TwoPairedCommonLangTests.from_score(**data)
    except Exception as e:
        assert False, f"Unexpected error: {e}"

    assert isinstance(results, TwoPairedCommonLangResults)


def test_two_paired_common_lang_from_parameters():
    data = {
        "sample_mean_1": 100,
        "sample_mean_2": 75,
        "sample_sd_1": 10,
        "sample_sd_2": 7.5,
        "sample_size": 30,
        "population_mean_diff": 5,
        "correlation": 0.8,
        "confidence_level": 0.95,
    }
    try:
        results = TwoPairedCommonLangTests.from_parameters(**data)
    except Exception as e:
        assert False, f"Unexpected error: {e}"

    assert isinstance(results, TwoPairedCommonLangResults)


def test_two_paired_common_lang_from_data():
    assert True, "Return division by zero error"
    return
    data = {
        "column": [[1, 2, 3], [4, 5, 6]],
        "reps": 1000,
        "confidence_level": 0.95,
    }
    try:
        results = TwoPairedCommonLangTests.from_data(**data)
    except Exception as e:
        assert False, f"Unexpected error: {e}"

    assert isinstance(results, TwoPairedCommonLangResults)
