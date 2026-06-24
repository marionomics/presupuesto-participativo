import pytest
from pb_mes.utils.gini import gini


def test_perfect_equality():
    assert gini([1.0, 1.0, 1.0, 1.0]) == pytest.approx(0.0, abs=1e-9)


def test_perfect_inequality():
    # One person has everything
    assert gini([0.0, 0.0, 0.0, 100.0]) == pytest.approx(0.75, abs=1e-6)


def test_known_value():
    # [1, 2, 3, 4] → Gini = 0.25
    assert gini([1.0, 2.0, 3.0, 4.0]) == pytest.approx(0.25, abs=1e-6)


def test_single_value():
    assert gini([42.0]) == pytest.approx(0.0, abs=1e-9)
