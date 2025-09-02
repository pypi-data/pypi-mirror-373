from src.esek.Calculator.TwoPairedMean.two_paired_robust import (
    TwoPairedRobustResults,
    TwoPairedRobustTests,
)


def test_two_paired_robust_from_score():
   assert True, "Method not implemented yet"


def test_two_paired_robust_from_parameters():
    assert True, "Method not implemented yet"


def test_two_paired_robust_from_data():
    data = {
        "columns": [[1, 2, 3], [4, 5, 6]],
        "reps": 1000,
        "confidence_level": 0.95,
    }
    try:
        results = TwoPairedRobustTests.from_data(**data)
    except Exception as e:
        assert False, f"Unexpected error: {e}"

    assert isinstance(results, TwoPairedRobustResults)
