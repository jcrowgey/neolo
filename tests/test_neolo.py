import pytest
from neolo import neolo
import math


def test_erathos():
    assert neolo.erathos(3) == [2, 3]
    assert neolo.erathos(11) == [2, 3, 5, 7, 11]
    with pytest.raises(AssertionError):
        neolo.erathos(1)
    with pytest.raises(AssertionError):
        neolo.erathos(-11)


def test_lemma1():
    assert neolo.lemma1(1, 2) == 0
    assert neolo.lemma1(5, 2) == 3


def test_lemma2():
    for i in neolo.erathos(23):
        assert neolo.product(
            [k ** v for k, v in neolo.lemma2(i).items()]
        ) == math.factorial(i)
