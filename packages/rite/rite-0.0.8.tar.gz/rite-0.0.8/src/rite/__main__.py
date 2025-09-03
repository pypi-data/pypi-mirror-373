# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Provides a rite entry point
===========================



"""


# =============================================================================
# Imports
# =============================================================================

# Import | Futures
# Import | Future
from __future__ import annotations, print_function

# Import | Standard Library
import platform

try:
    import pkg_resources
except ImportError:
    pkg_resources = None

# Import | Libraries
import rite

# Import | Local Modules


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    print()
    print("rite is set!")
    print()
    print("rite: {}".format(rite.__version__))
    print(
        "Python: {} ({})".format(
            platform.python_version(), platform.python_implementation()
        )
    )

    if pkg_resources:
        working_set = pkg_resources.working_set
        packages = set([p.project_name for p in working_set]) - set(["rite"])
        rite_pkgs = [p for p in packages if p.lower().startswith("rite")]

        if rite_pkgs:
            print("Extensions: {}".format([p for p in rite_pkgs]))
