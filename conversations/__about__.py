# SPDX-FileCopyrightText: 2022-present Robert Luke <code@robertluke.net>
#
# SPDX-License-Identifier: MIT
__version__ = "0.9.0"

def get_version(x: str, y:int):
    """What is the installed version of conversations?

    Parameters
    ----------
    x : str
        Description of parameter `x`.
    y : int
        Description of parameter `y`.
    """
    print(x)  # This does some printing.
    print(y)  # This is just for testing.
    return __version__
    