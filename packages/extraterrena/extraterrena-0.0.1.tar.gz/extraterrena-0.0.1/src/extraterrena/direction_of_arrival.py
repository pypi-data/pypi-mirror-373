import numpy as np
import polars as pl
from extraterrena import arrays
from abc import ABC
from tqdm import tqdm
import itertools
from loguru import logger


def calc_q(
    steer_vec: np.ndarray,
    noise_subspace_acm: np.ndarray,
) -> float:
    """Calculates the Q factor for a particular steering vector and number of interferers.

    This is the inverse of the MUSIC factor describer in section 9.3.2.1 of Van Trees Optimum Array Processing
    so that likely directions are found as peaks rather than as valleys.

    :param steer_vec: Steering vector for the array to a particular direction.
    :type steer_vec: np.ndarray
    :param noise_subspace_acm: Noise subspace ACM from eigendecomposition of covariance matrix.
    :type noise_subspace_acm: np.ndarray
    :return: Q-factor. Higher value means less energy in the direction of the steering vector.
    :rtype: float
    """
    Q = 1 / np.abs(steer_vec.conj().T @ noise_subspace_acm @ steer_vec)
    return Q


class MUSICBase(ABC):
    def convert_to_dbs(self, df: pl.DataFrame, column_name: str = "Q") -> pl.DataFrame:
        """Converts column of dataframe to decibels.

        :param df: Dataframe containing a column to convert to decibels.
        :type df: pl.DataFrame
        :param column_name: Name of column to transform, defaults to "Q"
        :type column_name: str, optional
        :return: Polars dataframe with the specified column transformed to decibels.
        :rtype: pl.DataFrame
        """

        return df.with_columns(
            (
                10 * pl.col(column_name).abs().log10()
                - 10 * pl.col(column_name).abs().max().log10()
            ).alias(column_name + "_db")
        )


class MUSICDOA1D(MUSICBase):
    """Uses the MUSIC algorithm to return sensitivities to particular directions."""

    def get_directions(
        self,
        array: arrays.Array,
        acm: np.ndarray,
        num_interferers: int,
        wavelength: float,
        theta_min_deg: float = -90,
        theta_max_deg: float = 90,
        theta_steps: int = 1000,
    ) -> pl.DataFrame:
        """Implements the MUSIC algorithm for a 1D far-field source.

        :param array: Array that is sensing the data.
        :type array: arrays.Array
        :param acm: The array correlation matrix.
        :type acm: np.ndarray
        :param num_interferers: The number of interferers that are present in the data.
        :type num_interferers: int
        :param wavelength: The wavelength of the narrowband channel.
        :type wavelength: float
        :param theta_min_deg: Minimum value of theta in degrees to search, defaults to -90
        :type theta_min_deg: float, optional
        :param theta_max_deg: Maximum value of theta in degrees to search, defaults to 90
        :type theta_max_deg: float, optional
        :param theta_steps: Number of search steps between theta_min_deg and theta_max_deg, defaults to 180
        :type theta_steps: int, optional
        :return: A polars DataFrame with the inverse energy in dB in each searched direction. Higher numbers are more likely to be signal sources.
        :rtype: pl.DataFrame
        """
        _, evecs = np.linalg.eigh(acm)
        theta_range = np.linspace(theta_min_deg, theta_max_deg, theta_steps)

        noise_subspace_acm = (
            evecs[:, :-num_interferers] @ evecs[:, :-num_interferers].conj().T
        )
        output = []
        for theta in theta_range:
            steer_vec = array.steering_vector(np.deg2rad(theta), wavelength).T
            Q = calc_q(steer_vec, noise_subspace_acm)
            output.append({"theta": theta, "Q": Q})
        output = pl.from_records(output)
        output = self.convert_to_dbs(output)

        return output


class MUSICDOA2D(MUSICBase):
    def get_directions(
        self,
        array: arrays.Array,
        acm: np.ndarray,
        num_interferers: int,
        wavelength: float,
        theta_min_deg: float = -90,
        theta_max_deg: float = 90,
        theta_steps: int = 1000,
        phi_min_deg: float = -90,
        phi_max_deg: float = 90,
        phi_steps: float = 1000,
    ) -> pl.DataFrame:
        """Implements the MUSIC algorithm for a 2D far-field source.

        :param array: Array that is sensing the data.
        :type array: arrays.Array
        :param acm: The array correlation matrix.
        :type acm: np.ndarray
        :param num_interferers: The number of interferers that are present in the data.
        :type num_interferers: int
        :param wavelength: The wavelength of the narrowband channel.
        :type wavelength: float
        :param theta_min_deg: Minimum value of theta in degrees to search, defaults to -90
        :type theta_min_deg: float, optional
        :param theta_max_deg: Maximum value of theta in degrees to search, defaults to 90
        :type theta_max_deg: float, optional
        :param theta_steps: Number of search steps between theta_min_deg and theta_max_deg, defaults to 180
        :type theta_steps: int, optional
        :param phi_min_deg: Minimum value of phi in degrees to search, defaults to -180
        :type phi_min_deg: float, optional
        :param phi_max_deg: Maximum value of phi in degrees to search, defaults to 180
        :type phi_max_deg: float, optional
        :param phi_steps: Number of search steps between phi_min_deg and phi_max_deg, defaults to 360
        :type phi_steps: int, optional
        :return: A polars DataFrame with the inverse energy in dB in each searched direction. Higher numbers are more likely to be signal sources.
        :rtype: pl.DataFrame
        """
        _, evecs = np.linalg.eigh(acm)

        theta_range = np.linspace(theta_min_deg, theta_max_deg, theta_steps)
        phi_range = np.linspace(phi_min_deg, phi_max_deg, phi_steps)

        noise_subspace_acm = (
            evecs[:, :-num_interferers] @ evecs[:, :-num_interferers].conj().T
        )
        output = []

        THRESHOLD_SET = False
        threshold = 0
        for phi, theta in tqdm(
            itertools.product(phi_range, theta_range),
            total=len(phi_range) * len(theta_range),
        ):
            steer_vec = array.steering_vector(
                [np.deg2rad(phi), np.deg2rad(theta)], wavelength
            )

            Q = calc_q(steer_vec, noise_subspace_acm)

            if not THRESHOLD_SET or Q > threshold:
                output.append({"phi": phi, "theta": theta, "Q": Q})

            if len(output) > 10_000 and not THRESHOLD_SET:
                # To avoid adding millions of records - only record if it's in the top 40% of
                # observations seen thus far.
                THRESHOLD_SET = True
                threshold = pl.from_records(output)["Q"].quantile(0.6)
                logger.info("Threshold set")

        output = pl.from_records(output)
        output = self.convert_to_dbs(output)
        return output


class MUSICNF2D(MUSICBase):
    def get_direction(
        self,
        array: arrays.Array,
        acm: np.ndarray,
        num_interferers: int,
        wavelength: float,
        r_min: float = 0,
        r_max: float = 1_000,
        r_steps: int = 1_000,
        theta_min_deg: float = -90,
        theta_max_deg: float = 90,
        theta_steps: int = 180,
        phi_min_deg: float = -180,
        phi_max_deg: float = 180,
        phi_steps: int = 360,
    ) -> pl.DataFrame:
        """Implements the MUSIC algorithm for a 2D near-field source.

        :param array: Array that is sensing the data.
        :type array: arrays.Array
        :param acm: The array correlation matrix.
        :type acm: np.ndarray
        :param num_interferers: The number of interferers that are present in the data.
        :type num_interferers: int
        :param wavelength: The wavelength of the narrowband channel.
        :type wavelength: float
        :param r_min: Minimum value of r in meters to search, defaults to 0
        :type r_min: float, optional
        :param r_max: Maximum value of r in meters to search, defaults to 1_000
        :type r_max: float, optional
        :param r_steps: Number of search steps between r_min and r_max, defaults to 1_000
        :type r_steps: int, optional
        :param theta_min_deg: Minimum value of theta in degrees to search, defaults to -90
        :type theta_min_deg: float, optional
        :param theta_max_deg: Maximum value of theta in degrees to search, defaults to 90
        :type theta_max_deg: float, optional
        :param theta_steps: Number of search steps between theta_min_deg and theta_max_deg, defaults to 180
        :type theta_steps: int, optional
        :param phi_min_deg: Minimum value of phi in degrees to search, defaults to -180
        :type phi_min_deg: float, optional
        :param phi_max_deg: Maximum value of phi in degrees to search, defaults to 180
        :type phi_max_deg: float, optional
        :param phi_steps: Number of search steps between phi_min_deg and phi_max_deg, defaults to 360
        :type phi_steps: int, optional
        :return: A polars DataFrame with the inverse energy in dB in each searched direction. Higher numbers are more likely to be signal sources.
        :rtype: pl.DataFrame
        """
        _, evecs = np.linalg.eigh(acm)

        ## This should go from 0 to whatever the far field would be for
        ## this particular antenna I guess.
        r_space = np.linspace(r_min, r_max, r_steps)
        theta_space = np.linspace(theta_min_deg, theta_max_deg, theta_steps)
        phi_space = np.linspace(phi_min_deg, phi_max_deg, phi_steps)

        noise_subspace_acm = (
            evecs[:, :-num_interferers] @ evecs[:, :-num_interferers].conj().T
        )
        output = []
        for r in r_space:
            for theta in theta_space:
                for phi in phi_space:
                    steer_vec = array.nf_steering_vector(
                        r, [np.deg2rad(phi), np.deg2rad(theta)], wavelength
                    )

                    Q = calc_q(steer_vec, noise_subspace_acm)

                    output.append({"r": r, "theta": theta, "phi": phi, "Q": Q})

        output = pl.from_records(output)
        output = self.convert_to_dbs(output)
        return output
