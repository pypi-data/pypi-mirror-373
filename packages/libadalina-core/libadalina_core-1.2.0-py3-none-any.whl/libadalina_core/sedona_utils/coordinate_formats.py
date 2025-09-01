from enum import Enum

class EPSGFormats(Enum):
    """
    Enum representing common EPSG formats used in geospatial data [1]_.

    References
    ----------

    .. [1] Service to explore and search for coordinate
       reference systems https://epsg.io

    """

    EPSG4326 = 4326
    """WGS 84 -- WGS84 - World Geodetic System 1984, used in GPS"""
    EPSG32632 = 32632
    """WGS 84 / UTM zone 32N"""

    @staticmethod
    def from_code(code: int) -> 'EPSGFormats':
        """
        Get the EPSG format from its integer code.

        Parameters
        ----------
        code : int
            Integer code representing the EPSG format.

        Returns
        -------
        EPSGFormats
            The corresponding EPSGFormats.

        Raises
        ------
        ValueError
            If no EPSG format is found for the given code.

        """
        for f in EPSGFormats:
            if f.value == code:
                return f
        raise ValueError(f"No EPSG format found for code {code}")

"""
Default EPSG format used in libadalina.

All DataFrame are converted upon reading and writing to this format.
"""
DEFAULT_EPSG = EPSGFormats.EPSG4326