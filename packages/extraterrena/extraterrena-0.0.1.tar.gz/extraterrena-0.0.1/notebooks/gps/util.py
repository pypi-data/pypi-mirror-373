from sgp4.api import Satrec
from sgp4.api import SGP4_ERRORS
from astropy.time import Time
from astropy.coordinates import TEME, CartesianDifferential, CartesianRepresentation
from astropy import units as u
from astropy.coordinates import ITRS
from astropy.coordinates import EarthLocation, AltAz
from astropy.coordinates import SkyCoord
from typing import Union, Tuple
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
from pytz import timezone
from collections import defaultdict

class TLE:
    """
    See https://celestrak.org/NORAD/documentation/tle-fmt.php for protocol documentation
    """
    def __init__(self, s, t):
        self.first_line = s
        self.second_line = t

        # first line parsing
        self.satellite_number = self.first_line[2:7]
        self.classification = self.first_line[7:8]
        self.international_designator = self.first_line[9:17]

        self.epoch_year = self.first_line[18:20]
        self.epoch = self.first_line[20:32]

        self.first_derivative_of_mean_motion = float(self.first_line[33:43])
        
        self.second_derivative_snip = self.first_line[44:52]
        second_derivative_arg, second_derivative_exponent = self.second_derivative_snip.strip().split('-')
        self.second_derivative_of_mean_motion = float(f"0.{second_derivative_arg}") * 10 ** -int(second_derivative_exponent)

        self.bstar_snip = self.first_line[53:61]
        symbol_to_split = None
        multiplier = None
        if '-' in self.bstar_snip:
            symbol_to_split = '-'
            multiplier = -1
        else:
            symbol_to_split = '+'
            multiplier = 1
        bstar_arg, bstar_exponent = self.bstar_snip.strip().split(symbol_to_split)
        self.bstar_drag_term = float(f"0.{bstar_arg}") * 10 ** (multiplier * int(bstar_exponent))
        
        self.ephemeris_type = self.first_line[62:63]

        self.element_number = self.first_line[64:68]
        self.first_checksum = self.first_line[-1]


        # second line parsing
        self.inclination_degrees = float(self.second_line[8:16])
        self.right_ascension_ascending_node = float(self.second_line[17:25])
        self.eccentricity = float(f"0.{self.second_line[26:33]}")
        self.argument_of_perigee = float(self.second_line[34:42])
        self.mean_anomaly = float(self.second_line[43:51])
        self.mean_motion = float(self.second_line[52:63])
        self.revolution_number_at_epoch = float(self.second_line[63:68])
        self.second_checksum = float(self.second_line[-1])

    def print_all(self):
        for var_name in ['satellite_number', 'classification', 'international_designator', 'epoch_year', 'epoch', 
                         'first_derivative_of_mean_motion', 'second_derivative_of_mean_motion', 'bstar_drag_term', 
                         'ephemeris_type', 'element_number', 'first_checksum', 'inclination_degrees', 
                         'right_ascension_ascending_node', 'eccentricity', 'argument_of_perigee', 'mean_anomaly', 
                         'mean_motion', 'revolution_number_at_epoch', 'second_checksum']:
        
            # Get the value of the variable using locals()
            var_value = getattr(self,var_name)
        
            # Print the variable name and its value
            print(f"{var_name} = {var_value}")


    def _pad_output(self, string_to_pad: Union[str, float], desired_length: int, pad_front=True, front_pad_num: int=3) -> str:
        if not isinstance(string_to_pad, str):
            string_to_pad = "{:.20f}".format(string_to_pad)

        if pad_front:
            desired_length -= len(self._pad_front(string_to_pad, pad=front_pad_num))
        
        if len(string_to_pad) == desired_length:
            return string_to_pad

        if len(string_to_pad) > desired_length:
            return string_to_pad[:desired_length]

        while len(string_to_pad) < desired_length:
            string_to_pad += "0"

        return string_to_pad
        
    def _pad_front(self, value: Union[float, str], pad: int = 3):
        if not isinstance(value, float):
            value = float(value)
        if value < 10: 
            return '  '[(3 - pad):]
        if value < 100:
            return ' '[(3-pad):]

        return ''

    
    def get_tle(self) -> tuple[str, str]:
        first_line = f"1 {self.satellite_number}{self.classification} {self.international_designator} {self.epoch_year}{self.epoch} {self._pad_output('{:.15f}'.format(self.first_derivative_of_mean_motion).replace('0.', '.'), 10, pad_front=False)}"
        # TODO: procedurally generate the 000000-0 format here
        first_line += f" {self.second_derivative_snip} {self.bstar_snip} {self.ephemeris_type} {self.element_number}{self.first_checksum}"

        
        
        second_line = f"2 {self.satellite_number} {self._pad_front(self.inclination_degrees)}{self._pad_output(str(round(self.inclination_degrees,4)), 8)} {self._pad_front(self.right_ascension_ascending_node)}{self._pad_output(str(round(self.right_ascension_ascending_node, 4)), 8)} {self._pad_output(str(round(self.eccentricity,7)).split('.')[-1], 7)} {self._pad_front(self.argument_of_perigee)}{self._pad_output(str(round(self.argument_of_perigee,4)), 8)} {self._pad_front(self.mean_anomaly)}{self._pad_output(str(round(self.mean_anomaly,4)), 8)} {self._pad_front(self.mean_motion, pad=2)}{self._pad_output(str(round(self.mean_motion, 11)), 11, front_pad_num=2)}{self._pad_output(self.revolution_number_at_epoch, 5)}{int(self.second_checksum)}"

        return (first_line, second_line)

    def __sub__(self, other):

        if self.satellite_number != other.satellite_number:
            raise ValueError("This is not the same satellite!")
        
        for var_name in [
                         'first_derivative_of_mean_motion',
                        'inclination_degrees', 
                         'right_ascension_ascending_node', 'eccentricity', 'argument_of_perigee', 'mean_anomaly', 
                         'mean_motion',]:
        
            # Get the value of the variable using locals()
            var_value = getattr(self,var_name)
            other_value = getattr(other, var_name)
        
            # Print the variable name and its value
            print(f"{var_name} = After: {var_value:.4f}, Before: {other_value:.4f}, Diff: {var_value - other_value:.4f}")

def _pad_front(value: Union[float, str], pad: int = 3):
    if not isinstance(value, float):
        value = float(value)
    if value < 10: 
        return '  '[(3 - pad):]
    if value < 100:
        return ' '[(3-pad):]

    return ''

def get_position_at_time(tle: TLE, obstime: Time, location: EarthLocation) -> tuple[float, float]:
    satellite = Satrec.twoline2rv(*tle.get_tle())
    error_code, teme_p, teme_v = satellite.sgp4(obstime.jd1, obstime.jd2)  # in km and km/s
    
    teme_p = CartesianRepresentation(teme_p* u.km)
    teme_v = CartesianDifferential(teme_v * u.km / u.s)
    
    teme = TEME(teme_p.with_differentials(teme_v), obstime=obstime)
    
    itrs_geo = teme.transform_to(ITRS(obstime=obstime))
    topo_itrs_repr = itrs_geo.cartesian.without_differentials() - location.get_itrs(obstime).cartesian
    itrs_topo = ITRS(topo_itrs_repr, obstime=obstime, location=location)
    
    aa = itrs_topo.transform_to(AltAz(obstime=obstime, location=location))
    sc = SkyCoord(alt=aa.alt, az = aa.az, obstime=obstime, frame='altaz', location=location)
    
    return (aa.alt, aa.az)


def polynomial_calc(t: np.ndarray, coefficients) -> np.ndarray:

    values = np.zeros(len(t))
    for i, val in enumerate(coefficients):
        values += val * t ** i

    return values


def get_variable_delays(filename: str, search_text: str) -> dict[int, dict[int, float]]:
    with open(filename, 'rb') as f:
        data = f.readlines()[0:344]
    
        
        nf_delay_data = [str(line) for line in data if search_text in str(line)]
        nf_delay_data = {line.split(search_text)[0].strip(): line.split(search_text)[1].split('\\t') for line in nf_delay_data}
        
        final_nf_delay_data = defaultdict(lambda: defaultdict(list))
        for key, vals in nf_delay_data.items():
            # Index 1 will be the SRC and Index 3 will be the antenna number.
            split_key = key.split(' ')
            src_num = int(split_key[1])
            ant_num = int(split_key[3])
        
            vals = [float(val.strip().replace('\\n', '').replace("'", '')) for val in vals]
            final_nf_delay_data[src_num][ant_num] = vals
        
    return final_nf_delay_data