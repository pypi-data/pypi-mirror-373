import numpy as np
import pytest

from extraterrena import filters


@pytest.fixture
def acm_test():
    return np.array(
        [
            [
                2400.54220501 + 0.0j,
                -306.90862621 - 558.47263411j,
                -472.6413601 - 176.10442807j,
                -193.74163077 + 134.30679748j,
            ],
            [
                -306.90862621 + 558.47263411j,
                1873.67925343 + 0.0j,
                3.93243609 - 18.78597405j,
                -180.59717607 - 194.84483063j,
            ],
            [
                -472.6413601 + 176.10442807j,
                3.93243609 + 18.78597405j,
                1816.74606276 + 0.0j,
                -435.70396836 - 387.356339j,
            ],
            [
                -193.74163077 - 134.30679748j,
                -180.59717607 + 194.84483063j,
                -435.70396836 + 387.356339j,
                3114.07184317 + 0.0j,
            ],
        ]
    )


def test_null_eigenvalue_filter(acm_test):
    original_eigenvalues, _ = np.linalg.eigh(acm_test)
    corrected_acm = filters.NullEigenvalueFilter().filter(acm_test)

    assert isinstance(corrected_acm, np.ndarray)
    assert acm_test.shape == corrected_acm.shape
    assert not np.allclose(corrected_acm, acm_test)

    new_eigenvalues, _ = np.linalg.eigh(corrected_acm)
    assert np.allclose(original_eigenvalues[:-1], new_eigenvalues[1:])
    assert np.isclose(new_eigenvalues[0], 0)


def test_null_eigenvalue_filter_two_eigenvalues(acm_test):
    original_eigenvalues, _ = np.linalg.eigh(acm_test)
    corrected_acm = filters.NullEigenvalueFilter().filter(acm_test, 2)
    assert isinstance(corrected_acm, np.ndarray)
    assert acm_test.shape == corrected_acm.shape
    assert not np.allclose(corrected_acm, acm_test)

    new_eigenvalues, _ = np.linalg.eigh(corrected_acm)
    assert np.allclose(original_eigenvalues[:-2], new_eigenvalues[2:])
    assert np.isclose(new_eigenvalues[0], 0)
    assert np.isclose(new_eigenvalues[1], 0)


def test_null_eigenvalue_filter_throws_error_if_negative_number_of_eigenvalues(
    acm_test,
):
    with pytest.raises(ValueError):
        filters.NullEigenvalueFilter().filter(acm_test, -1)


def test_shrink_eigenvalue_filter_throws_error_if_negative_number_of_eigenvalues(
    acm_test,
):
    with pytest.raises(ValueError):
        filters.ShrinkEigenvalueFilter().filter(acm_test, -1)


def test_shrink_eigenvalue_filter(acm_test):
    original_eigenvalues, _ = np.linalg.eigh(acm_test)

    corrected_acm = filters.ShrinkEigenvalueFilter().filter(acm_test)

    new_eigenvalues, _ = np.linalg.eigh(corrected_acm)
    assert isinstance(corrected_acm, np.ndarray)
    assert acm_test.shape == corrected_acm.shape

    for eig in original_eigenvalues[:-1]:
        assert np.any(np.isclose(new_eigenvalues, eig))

    assert np.any(np.isclose(new_eigenvalues, np.mean(original_eigenvalues[:-1])))
