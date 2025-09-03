#!/usr/bin/env python3

########################################################################################
# Experimental Atspi API extension                                                     #
########################################################################################

# pylint: disable=broad-exception-caught
# pylint: disable=import-error
# pylint: disable=import-outside-toplevel
# pylint: disable=no-member
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# ruff: noqa: E402
# ruff: noqa: E501

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

import warnings

warnings.filterwarnings("ignore", "g_object_unref")

from qecore.logger import Logging
from qecore.utility import AUTOMATIC_LOGIN_IN_EFFECT

try:
    from dogtail.rawinput import click

except Exception as error:
    if not AUTOMATIC_LOGIN_IN_EFFECT:
        print(f"Expected issues in API: '{error}'")
    else:
        raise Exception from error

DESKTOP_COORDINATES = 0
WINDOW_COORDINATES = 1

logging_class = Logging()
LOGGING = logging_class.logger


class APIExtension:
    """
    Extension class to extend dogtail API.
    """

    def click_offset(
        self, mouse_button=1, offset_x=0, offset_y=0, coord_type=DESKTOP_COORDINATES
    ):
        """
        Generates a raw click on coordinates of the object.
        User is able to define what mouse button will be used, modify an offset from
        those coordinates and choose a type of coordinates to use.

        :param mouse_button: Mouse button [1 - left, 2 - middle, 3 - right]
        :type mouse_button: int

        :param offset_x: Offset from node coordinates in X axis by number of pixels.
        :type offset_x: int

        :param offset_y: Offset from node coordinates in Y axis by number of pixels.
        :type offset_y: int

        :param coord_type: DESKTOP or WINDOW coordinate type.
        :type coord_type: int
        """

        # Ponytail window id handling for certain situations.
        window_id = self.window_id
        if (
            self.get_name().lower() in ["quit", "exit"]
            or "close" in self.get_name().lower()
        ):
            window_id = ""

        if coord_type == DESKTOP_COORDINATES:
            _position = self.get_component_iface().get_position(DESKTOP_COORDINATES)
        elif coord_type == WINDOW_COORDINATES:
            _position = self.get_component_iface().get_position(WINDOW_COORDINATES)
        else:
            raise RuntimeError(f"Unsupported coordinate type: '{str(coord_type)}'")

        def out_of_bounds(coordinates):
            return (
                coordinates.x > 10000
                or coordinates.y > 10000
                or (coordinates.y == 0 and coordinates.x == 0)
                or coordinates.x < 0
                or coordinates.y < 0
            )

        _size = self.get_component_iface().get_size()

        LOGGING.info(f"Atspi.Accessible position X: {_position.x}")
        LOGGING.info(f"Atspi.Accessible position Y: {_position.y}")
        LOGGING.info(f"Atspi.Accessible size X: {str(int(_size.x))}")
        LOGGING.info(f"Atspi.Accessible size Y: {str(int(_size.y))}")

        if _position and out_of_bounds(_position):
            LOGGING.info(f"Possibly wrong type of coordinate: {str(coord_type)}")

        center_position_x = _position.x + int(_size.x / 2) + offset_x
        center_position_y = _position.y + int(_size.y / 2) + offset_y

        coord_type_str = (
            "DESKTOP_COORDINATES" if coord_type == 0 else "WINDOW_COORDINATES"
        )

        LOGGING.info(
            " ".join(
                (
                    f"Mouse button {mouse_button}",
                    f"click at ({center_position_x},{center_position_y})",
                    f"with coordinate type {coord_type_str}",
                )
            )
        )

        # Using raw click from dogtail for now.
        click(center_position_x, center_position_y, mouse_button, window_id=window_id)


def extend_dogtail_api():
    """
    Attempt to have linter compliant way to extend API.
    """
    Atspi.Accessible.__bases__ = (APIExtension,) + Atspi.Accessible.__bases__
