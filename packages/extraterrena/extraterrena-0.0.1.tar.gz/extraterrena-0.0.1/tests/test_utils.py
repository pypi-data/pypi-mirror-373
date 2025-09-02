from extraterrena import utils
import pytest
import numpy as np


@pytest.mark.parametrize(
    "input_angles,expected_output",
    [
        [(0, 0), (0, 0)],
        [(30, 30), (26.5651, 14.4775)],
        [(60, 45), (26.5651, 37.7612)],
    ],
)
def test_van_trees_to_matlab_coords(input_angles, expected_output):
    phi, theta = input_angles
    expected_phi, expected_theta = expected_output

    output_phi, output_theta = utils.convert_van_trees_coords_to_matlab_coords(
        phi, theta
    )
    assert np.isclose(output_phi, expected_phi)
    assert np.isclose(output_theta, expected_theta)


@pytest.mark.parametrize(
    "input_angles,expected_output",
    [
        [(0, 0), (0, 0)],
        [(26.5651, 14.4775), (30, 30)],
        [(26.5651, 37.7612), (60, 45)],
    ],
)
def test_matlab_to_van_trees_coords(input_angles, expected_output):
    phi, theta = input_angles
    expected_phi, expected_theta = expected_output

    output_phi, output_theta = utils.convert_matlab_to_van_trees_coords(phi, theta)

    assert np.isclose(output_phi, expected_phi)
    assert np.isclose(output_theta, expected_theta)


@pytest.mark.xfail
def test_matlab_to_van_trees_coords_expected_fail_0_90():
    """
    The case of zero azimuth is not yet handled.
    """
    phi, theta = (0, 90)

    output_phi, output_theta = utils.convert_matlab_to_van_trees_coords(phi, theta)

    assert np.isclose(output_phi, 90.0)
    assert np.isclose(output_theta, 0.0)
