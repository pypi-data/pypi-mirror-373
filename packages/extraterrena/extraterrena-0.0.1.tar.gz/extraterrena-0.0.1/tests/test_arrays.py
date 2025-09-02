import numpy as np
import pytest

from extraterrena import arrays, constants

EPS = 0.0001


class TestArray:
    def test_array_list_positions(self):
        """Test that instantiation works if a list is provided for positions."""

        array = arrays.Array([0.1 * n for n in range(5)])
        assert isinstance(array.positions, np.ndarray)


class TestUniformLinearArray:
    spacing = 1
    atol = 0.01
    frequency = 1e9
    wavelength = constants.c / frequency

    def test_linear_array_positioning_odd(self):
        num_antennas = 3

        array = arrays.UniformLinearArray(num_antennas, self.spacing)
        assert np.allclose(
            array.positions,
            np.array([[-1, 0, 0], [0, 0, 0], [1, 0, 0]]),
            atol=self.atol,
        )
        assert array.num_antennas == num_antennas

    def test_linear_array_positioning_even(self):
        num_antennas = 2

        array = arrays.UniformLinearArray(num_antennas, self.spacing)

        assert np.allclose(
            array.positions, np.array([[-0.5, 0, 0], [0.5, 0, 0]]), atol=self.atol
        )
        assert array.num_antennas == num_antennas

    def test_linear_array_positioning_even_4(self):
        num_antennas = 4

        array = arrays.UniformLinearArray(num_antennas, self.spacing)

        assert np.allclose(
            array.positions,
            np.array([[-1.5, 0, 0], [-0.5, 0, 0], [0.5, 0, 0], [1.5, 0, 0]]),
            atol=self.atol,
        )
        assert array.num_antennas == num_antennas

    def test_nf_steering_vector(self):
        num_antennas = 5
        array = arrays.UniformLinearArray(num_antennas, self.spacing)

        r = 0
        theta = 0
        phi = 0

        nf_steer_vec = array.nf_steering_vector(r, [phi, theta], self.wavelength)

        assert isinstance(nf_steer_vec, np.ndarray)
        assert nf_steer_vec.shape == (5,)
        assert np.allclose(
            nf_steer_vec,
            np.array(
                [
                    np.exp(-1j * 2 * np.pi * 2 * 1 / self.wavelength),
                    np.exp(-1j * 2 * np.pi * 1 / self.wavelength),
                    1,
                    np.exp(-1j * 2 * np.pi * 1 / self.wavelength),
                    np.exp(-1j * 2 * np.pi * 2 / self.wavelength),
                ]
            ),
            atol=self.atol,
        )


class TestLinearArray:
    freq = 1e9
    wavelength = constants.c / freq

    @pytest.fixture
    def linear_array(self) -> arrays.Array:
        return arrays.Array(np.array([0.1 * n for n in range(5)]))

    def test_linear_array_steering_vector(self, linear_array):
        """
        Uses https://au.mathworks.com/help/phased/ref/steervec.html (Line Array Steering Vector)
        We should be the conjugate of this.

        """
        steering_vec = linear_array.steering_vector(
            [0, np.deg2rad(45)], self.wavelength
        )

        assert np.allclose(
            steering_vec,
            np.array(
                [
                    1.0000 + 0.0000j,
                    0.0887 + 0.9961j,
                    -0.9843 + 0.1767j,
                    -0.2633 - 0.9647j,
                    0.9376 - 0.3478j,
                ]
            )
            .astype(np.complex128)
            .conj(),
            atol=EPS,
        )

    def test_linear_array_steering_vector_30(self, linear_array):
        """
        Uses https://au.mathworks.com/help/phased/ref/steervec.html (Line Array Steering Vector)
        We should be the conjugate of this.

        elementPos = (0:.1:.4)
        c = physconst('LightSpeed');
        fc = 1e9;
        lam = c/fc;
        ang = [30;0];
        sv = steervec(elementPos/lam,ang)

        Matlab assumes that if one element is given then it is the y axis.
        Similarly if it is 2D then it is yz co-ordinates instead of xy.
        """
        steering_vec = linear_array.steering_vector(
            [0, np.deg2rad(30)], self.wavelength
        )

        assert np.allclose(
            steering_vec,
            np.array(
                [
                    1.0000 + 0.0000j,
                    0.4994 + 0.8664j,
                    -0.5013 + 0.8653j,
                    -1.0000 - 0.0022j,
                    -0.4975 - 0.8675j,
                ]
            )
            .astype(np.complex128)
            .conj(),
            atol=EPS,
        )

    def test_linear_array_steering_vector_nonzero_phi_value(self, linear_array):
        """

        Matlab code to re-create:
        elementPos = (0:.1:.4)
        c = physconst('LightSpeed');
        fc = 1e9;
        lam = c/fc;
        ang = [45;45];
        sv = steervec(elementPos/lam,ang)

        We then take the conjugate as Matlab is transmission
        and we are receiving.
        """
        steering_vec = linear_array.steering_vector(
            [np.deg2rad(45), np.deg2rad(45)], self.wavelength
        )

        expected = np.array(
            [
                1.0000 + 0.0000j,
                0.4994 + 0.8664j,
                -0.5013 + 0.8653j,
                -1.0000 - 0.0022j,
                -0.4975 - 0.8675j,
            ]
        ).conj()

        assert np.allclose(steering_vec, expected, atol=EPS)


class TestRectangularArray:
    freq = 1e9
    wavelength = constants.c / freq

    @pytest.fixture
    def rec_array(self):
        d = self.wavelength / 4
        return arrays.Array(np.array([(-d, d), (-d, -d), (d, d), (d, -d)]))

    def test_rec_array_0_0(self, rec_array):
        """
        array = phased.URA(2, lam/2);
        array.Element.BackBaffled = true;

        c = physconst('LightSpeed');
        fc = 1e9;
        lam = c/fc;
        ang = [0;0];
        sv = steervec(getElementPosition(array)/lam,ang);
        sv
        """
        steering_vec = rec_array.steering_vector([0, 0], self.wavelength)

        expected = np.array(
            [
                1,
                1,
                1,
                1,
            ]
        ).conj()

        assert np.allclose(steering_vec, expected, atol=EPS)

    def test_rec_array_0_90(self, rec_array):
        """
        array = phased.URA(2, lam/2);
        array.Element.BackBaffled = true;

        c = physconst('LightSpeed');
        fc = 1e9;
        lam = c/fc;
        ang = [90;0];
        sv = steervec(getElementPosition(array)/lam,ang);
        sv

        """

        steering_vec = rec_array.steering_vector([0, np.deg2rad(90)], self.wavelength)

        expected = np.array(
            [
                0.0000 - 1.0000j,
                0.0000 - 1.0000j,
                0.0000 + 1.0000j,
                0.0000 + 1.0000j,
            ]
        ).conj()

        assert np.allclose(steering_vec, expected, atol=EPS)

    def test_rectangular_array_0_45(self, rec_array):
        """
        array = phased.URA(2, lam/2);
        array.Element.BackBaffled = true;

        c = physconst('LightSpeed');
        fc = 1e9;
        lam = c/fc;
        ang = [45;0];
        sv = steervec(getElementPosition(array)/lam,ang);
        sv

        """

        steering_vec = rec_array.steering_vector([0, np.deg2rad(45)], self.wavelength)

        expected = np.array(
            [
                0.4440 - 0.8960j,
                0.4440 - 0.8960j,
                0.4440 + 0.8960j,
                0.4440 + 0.8960j,
            ]
        ).conj()

        assert np.allclose(steering_vec, expected, atol=EPS)

    def test_rectangular_array_30_0(self, rec_array):
        """
        phi = 30;
        theta = 0;


        phi_new = atand(tand(theta) * cosd(phi));
        theta_new = atand(sind(theta) * sind(phi) / sqrt(sind(theta)^2 * cosd(phi)^2 + cosd(theta)^2));


        fc = 1e9;
        lam = c/fc;

        array = phased.URA(2, lam/2);
        array.Element.BackBaffled = true;

        c = physconst('LightSpeed');

        ang = [phi_new;theta_new];
        sv = steervec(getElementPosition(array)/lam,ang);
        sv

        """

        steering_vec = rec_array.steering_vector([np.deg2rad(30), 0], self.wavelength)

        expected = np.array([1, 1, 1, 1]).conj()

        assert np.allclose(steering_vec, expected, atol=EPS)

    def test_rectangular_array_0_30(self, rec_array):
        """
        phi = 0;
        theta = 30;


        phi_new = atand(tand(theta) * cosd(phi));
        theta_new = atand(sind(theta) * sind(phi) / sqrt(sind(theta)^2 * cosd(phi)^2 + cosd(theta)^2));


        fc = 1e9;
        lam = c/fc;

        array = phased.URA(2, lam/2);
        array.Element.BackBaffled = true;

        c = physconst('LightSpeed');

        ang = [phi_new;theta_new];
        sv = steervec(getElementPosition(array)/lam,ang);
        sv

        """

        steering_vec = rec_array.steering_vector([0, np.deg2rad(30)], self.wavelength)

        expected = np.array(
            [
                0.7071 - 0.7071j,
                0.7071 - 0.7071j,
                0.7071 + 0.7071j,
                0.7071 + 0.7071j,
            ]
        ).conj()

        assert np.allclose(steering_vec, expected, atol=EPS)

    def test_rectangular_array_30_30(self, rec_array):
        """phi = 30;
        theta = 30;


        phi_new = atand(tand(theta) * sind(phi));
        theta_new = acosd(sqrt(sind(theta)^2 * sind(phi)^2 + cosd(theta)^2));


        fc = 1e9;
        lam = c/fc;

        array = phased.URA(2, lam/2);
        array.Element.BackBaffled = true;

        c = physconst('LightSpeed');

        ang = [phi_new;theta_new];
        sv = steervec(getElementPosition(array)/lam,ang);
        sv

        """

        steering_vec = rec_array.steering_vector(
            [np.deg2rad(30), np.deg2rad(30)], self.wavelength
        )

        expected = np.array(
            [
                0.9590 - 0.2835j,
                0.4776 - 0.8786j,
                0.4776 + 0.8786j,
                0.9590 + 0.2835j,
            ]
        ).conj()

        assert np.allclose(steering_vec, expected, atol=EPS)

    def test_rectangular_array_60_45(self, rec_array):
        """
        phi = 60;
        theta = 45;


        phi_new = atand(tand(theta) * cosd(phi));
        theta_new = atand(sind(theta) * sind(phi) / sqrt(sind(theta)^2 * cosd(phi)^2 + cosd(theta)^2));


        fc = 1e9;
        lam = c/fc;

        array = phased.URA(2, lam/2);
        array.Element.BackBaffled = true;

        c = physconst('LightSpeed');

        ang = [phi_new;theta_new];
        sv = steervec(getElementPosition(array)/lam,ang);
        sv
        """
        steering_vec = rec_array.steering_vector(
            [np.deg2rad(60), np.deg2rad(45)], self.wavelength
        )

        expected = np.array(
            [
                0.9185 + 0.3954j,
                0.0535 - 0.9986j,
                0.0535 + 0.9986j,
                0.9185 - 0.3954j,
            ]
        ).conj()
        assert np.allclose(steering_vec, expected, atol=EPS)
