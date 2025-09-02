from src.esek.Calculator.TwoPairedMean.two_paired_aparametric import (
    TwoPairedAparametricResults,
    TwoPairedAparametricTests,
)


def test_two_paired_aparametric_from_score():
    assert True, "Method not implemented yet"


def test_two_paired_aparametric_from_parameters():
    assert True, "Method not implemented yet"


def test_two_paired_aparametric_from_data():
    data = {
        "columns": [[1, 2, 3], [4, 5, 6]],
        "population_difference": 0.5,
        "confidence_level": 0.95,
    }
    try:
        results = TwoPairedAparametricTests.from_data(**data)
    except Exception as e:
        assert False, f"Unexpected error: {e}"

    assert isinstance(results, TwoPairedAparametricResults)
