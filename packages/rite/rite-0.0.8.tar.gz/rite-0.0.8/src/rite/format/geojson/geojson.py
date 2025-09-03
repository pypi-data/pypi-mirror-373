# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Provides JSON stuff

"""


# Import | Futures
# […]

# Import | Standard Library
import json

# Import | Libraries
import geojson

# Import | Local Modules
# […]


class FileGeoJSON:
    """
    A class used to represent a GeoJSON File

    ...

    Attributes
    ----------


    Methods
    -------
    test()
        test method
    """

    # Static Methods

    @staticmethod
    def save_to_geojson(path, geometry):
        """"""
        # Serializing json
        dump = geojson.dumps(geometry, sort_keys=True, indent=4)
        # Writing to outfile
        with open(path, "w") as outfile:
            outfile.write(dump)
