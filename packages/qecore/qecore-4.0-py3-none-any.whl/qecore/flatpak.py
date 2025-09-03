#!/usr/bin/env python3
"""
Flatpak class to be used from TestSandbox to keep list of running applications.
"""

__author__ = """
Martin Krajnak <mkrajnak@redhat.com>
"""

from os import walk, path
import configparser

from qecore.utility import RunAndLog, get_func_params_and_values

from qecore.application import Application

from qecore.logger import Logging

logging_class = Logging()
LOGGING = logging_class.logger


class Flatpak(Application):
    """
    Flatpak specific class.

    :param Application: Application class.
    :type Application: Application
    """

    def __init__(self, flatpak_id, **kwargs) -> None:
        """
        Initiate Flatpak instance, inherits Application.

        :type flatpak_id: str
        :param flatpak_id: Unique flatpak identifier, mandatory format has 2 dots.
            Param is passed to Application constructor as .component

        :param kwargs: :py:class:`application.Application` parameters.
        """

        LOGGING.debug(get_func_params_and_values())

        # Check if the input is a list of IDs to check.
        if isinstance(flatpak_id, list):
            for flatpak_id_item in flatpak_id:
                try:
                    super().__init__(component=flatpak_id_item, **kwargs)
                    return  # Return successful match.
                except UserWarning:
                    LOGGING.debug(f"Attempt for ID '{flatpak_id_item}' unsuccessful.")

            # If the list was provided, do not continue on string handling.
            RunAndLog("flatpak list")
            raise UserWarning(f"None of the provided IDs '{flatpak_id}' were accepted.")

        # Check the flatpak name if user provided a string.
        if flatpak_id.count(".") != 2:
            raise UserWarning(
                f"Incorrect flatpak name {flatpak_id}, e.g.: 'org.gnome.gedit'."
            )

        # Attempt to check and log if the user did not do a typo.
        try:
            super().__init__(component=flatpak_id, **kwargs)
        except UserWarning as warning:
            LOGGING.debug(f"Flatpak ID provided by the user: '{flatpak_id}' not found.")
            RunAndLog("flatpak list")
            raise UserWarning(f"Flatpak ID '{flatpak_id}' was not found.") from warning

    def kill_application(self) -> None:
        """
        Killing via 'flatpak kill <flatpak_id>', sudo for @system flatpaks.
        """

        LOGGING.debug(get_func_params_and_values())

        if self.is_running() and self.kill:
            # Kills a flatpak installed @System.
            RunAndLog(f"sudo flatpak kill {self.component}")
            # Kills a flatpak installed @User.
            RunAndLog(f"flatpak kill {self.component}")

    def get_desktop_file_data(self) -> None:
        """
        Provide information from .desktop file, two possible locations:
            * flatpak installed as *--user*::

                ~/.local/share/flatpak/app/<flatpak_id>/<arch>/....

            * flatpak installed as *@system* (sudo, root)::

                /var/lib/flatpak/app/<flatpak_id>/<arch>/.....

        .. note::

            Do **NOT** call this by yourself. This method is called by :func:`__init__`.
        """

        LOGGING.debug(get_func_params_and_values())

        def get_desktop_file_path(flatpak_dir) -> None:
            """
            Helper function used for dynamic search of desktop files as
            the path contains a commit number in a folder name.
            """

            desktop_file_name = self.desktop_file_name or self.component
            for root, _, files in walk(flatpak_dir):
                for _file in files:
                    if ".desktop" in _file and desktop_file_name in _file:
                        return path.join(root, _file)
            return None

        if not self.desktop_file_exists:
            return None

        desktop_file = None
        if self.desktop_file_path:
            desktop_file = self.desktop_file_path
        else:
            for pth in ["~/.local/share/flatpak/app/", "/var/lib/flatpak/app/"]:
                pth = path.expanduser(pth)
                if path.isdir(f"{pth}{self.component}"):
                    desktop_file = get_desktop_file_path(f"{pth}{self.component}")
                    break

        if not desktop_file:
            raise UserWarning(f"Desktop file for {self.component} not found.")

        desktop_file_config = configparser.RawConfigParser()
        desktop_file_config.read(desktop_file)

        self.name = desktop_file_config.get("Desktop Entry", "name")
        self.exec = f"flatpak run {self.component}"
        self.icon = desktop_file_config.get("Desktop Entry", "icon", fallback=None)

    def is_running(self) -> bool:
        """
        Double check if running application is really a flatpak.
        """

        LOGGING.debug(get_func_params_and_values())

        flatpak_is_running = self.component in RunAndLog("flatpak ps").output

        if not flatpak_is_running:
            LOGGING.debug(f"Flatpak '{self.name}' is not running.")

        return super().is_running() and flatpak_is_running

    def start_via_menu(self, kill=False) -> None:
        """
        Icons belonging to flatpak applications cannot be distinguished
        from icons of their rpm versions, thus we recommend to remove
        rpm versions of the tested applications during test runs.

        .. note::

            Make sure that the .rpm version of a tested flatpak is not installed.
        """

        LOGGING.debug(get_func_params_and_values())

        rpms_run = RunAndLog(f'rpm -qa | grep -i "{self.name}"')
        if rpms_run.output is not None:
            print(
                f"WARNING: a method could possibly start a non-flatpak application\n"
                f"{self.name} is already installed as .rpm: {rpms_run.output}"
            )

        super().start_via_menu(kill)

    def get_pid_list(self) -> None:
        """
        Not required, killing via flatpak kill <flatpak_id>.

        .. note::

            This method is not available for flatpak objects.
        """

        LOGGING.debug(get_func_params_and_values())

        raise NotImplementedError("Not available for flatpak objects.")

    def get_all_kill_candidates(self) -> None:
        """
        Not required, killing via flatpak kill <flatpak_id>.

        .. note::

            This method is not available for flatpak objects.
        """

        LOGGING.debug(get_func_params_and_values())

        raise NotImplementedError("Not available for flatpak objects.")
