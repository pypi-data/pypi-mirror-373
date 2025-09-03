#!/usr/bin/env python
# -*- coding: utf-8 -*-


__all__ = [
    "classic",
    "polytechnique"
]

from matplotlib.colors import LinearSegmentedColormap


class NameSpace:
    """
    A class to dynamically create attributes from keyword arguments.
    """

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


blue_black_red = LinearSegmentedColormap.from_list(
    'blue_black_red',
    (
        # Edit this gradient at https://eltos.github.io/gradient/#0:7A90FF-33.9:0025B3-50:000000-75.8:C7030D-100:FF6E75
        (0.000, (0.478, 0.565, 1.000)),
        (0.339, (0.000, 0.145, 0.702)),
        (0.500, (0.000, 0.000, 0.000)),
        (0.758, (0.780, 0.012, 0.051)),
        (1.000, (1.000, 0.431, 0.459))
    )
)


blue_white_red = LinearSegmentedColormap.from_list(
    'blue_white_red',
    (
        # Edit this gradient at https://eltos.github.io/gradient/#0025B3-7A90FF-FFFFFF-FF6E75-C7030D
        (0.000, (0.000, 0.145, 0.702)),
        (0.250, (0.478, 0.565, 1.000)),
        (0.500, (1.000, 1.000, 1.000)),
        (0.750, (1.000, 0.431, 0.459)),
        (1.000, (0.780, 0.012, 0.051))
    )
)

_red_black_blue = LinearSegmentedColormap.from_list(
    'poly_red_black_blue',
    (
        # Edit this gradient at https://eltos.github.io/gradient/#41AAE6-000000-B91E32
        (0.000, (0.255, 0.667, 0.902)),
        (0.500, (0.000, 0.000, 0.000)),
        (1.000, (0.725, 0.118, 0.196))
    )
)

_red_white_blue = LinearSegmentedColormap.from_list('my_gradient', (
    # Edit this gradient at https://eltos.github.io/gradient/#41AAE6-FFFFFF-B91E32
    (0.000, (0.255, 0.667, 0.902)),
    (0.500, (1.000, 1.000, 1.000)),
    (1.000, (0.725, 0.118, 0.196))))

classic = NameSpace(
    blue_black_red=blue_black_red,
    red_black_blue=blue_black_red,
    blue_white_red=blue_white_red,
    red_white_blue=blue_white_red
)

polytechnique = NameSpace(
    red_black_blue=_red_black_blue,
    blue_black_red=_red_black_blue,
    red_white_blue=_red_white_blue,
    blue_white_red=_red_white_blue
)

# -
