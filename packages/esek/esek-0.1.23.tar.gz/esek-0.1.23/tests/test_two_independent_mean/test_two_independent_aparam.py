from src.esek.Calculator.TwoIndependentMean.two_independent_aparametric import (
    TwoIndependentAparametricResults,
    TwoIndependentAparametricTests,
)


def test_two_independent_aparametric_from_score():
    assert True, "Method not implemented yet"


def test_two_independent_aparametric_from_parameters():
    assert True, "Method not implemented yet"


def test_two_independent_aparametric_from_data():
    data = {
        "columns": [[1, 2, 3], [4, 5, 6]],
        "confidence_level": 0.95,
    }
    try:
        results = TwoIndependentAparametricTests.from_data(**data)
    except Exception as e:
        assert False, f"Unexpected error: {e}"

    assert isinstance(results, TwoIndependentAparametricResults)
