#!/usr/bin/env python3
"""
Application class to be used from TestSandbox to keep list of running applications.
"""

# pylint: disable=broad-exception-caught
# pylint: disable=import-outside-toplevel
# pylint: disable=import-error
# pylint: disable=invalid-name
# ruff: noqa: E501
# ruff: noqa: E402

import re
import os
import shlex
import configparser
from time import sleep
from typing import TypeVar
from subprocess import Popen, PIPE
from qecore.utility import AUTOMATIC_LOGIN_IN_EFFECT

try:
    from dogtail.rawinput import (
        typeText,
        pressKey,
        keyCombo,
    )
except Exception as error:
    if not AUTOMATIC_LOGIN_IN_EFFECT:
        print(f"Expected issues in Application: '{error}'")
    else:
        raise Exception from error

from qecore.utility import RunAndLog, overview_action, get_func_params_and_values
from qecore.logger import Logging

logging_class = Logging()
LOGGING = logging_class.logger

# We do this just to satisfy the typing hint
# but without the need to import entire class.
gi_repository_Atspi_Accessible = TypeVar("gi_repository_Atspi_Accessible")


class Application:
    """
    Application class taking care of setup on application side.
    """

    def __init__(
        self,
        component,
        a11y_app_name=None,
        desktop_file_exists=True,
        desktop_file_name="",
        desktop_file_path="",
        app_process_name="",
        session_type="",
        session_desktop="",
        kiosk=None,
    ) -> None:
        """
        .. note::

            Do **NOT** call this by yourself.
            This class is instanced by :py:meth:`sandbox.TestSandbox.get_application`.

        :type component: str
        :param component: Component name - usually the name of the application package.

        :type a11y_app_name: str
        :param a11y_app_name: Name of application as it appears in accessibility tree.

        :type desktop_file_exists: bool
        :param desktop_file_exists: Desktop file of given application exists.

        :type desktop_file_path: str
        :param desktop_file_path: Full posix path to .desktop file of application.

        :type desktop_file_name: str
        :param desktop_file_name: Name of desktop file if not same as component.

        :type app_process_name: str
        :param app_process_name: Name of application process if not same as component.
        """

        LOGGING.debug(get_func_params_and_values())

        # Define shell as None in the moment on initialization.
        self.shell = None
        self.kiosk = kiosk
        self.session_type = session_type
        self.session_desktop = session_desktop
        self.pid = None
        self.instance = None
        self.component = component
        self.a11y_app_name = a11y_app_name if a11y_app_name else component
        self.desktop_file_exists = desktop_file_exists
        self.exit_shortcut = "<Control_L><Q>"
        self.kill = True
        self.kill_command = ""
        self.desktop_file_name = desktop_file_name
        self.desktop_file_path = desktop_file_path
        self.application_list = []
        self.app_process_name = app_process_name if app_process_name else component
        self.icon = None
        self.process = None

        self.name = None
        self.exec = None
        self.icon = None
        self.get_desktop_file_data()

        # To be removed in the future, no more camelCasing.
        if "Flatpak" not in f"{type(self)}":
            # Preserving old api names of functions.
            self.getDesktopFileData = (  # pylint: disable=invalid-name
                self.get_desktop_file_data
            )
            self.getRoot = self.get_root  # pylint: disable=invalid-name
            self.isRunning = self.is_running  # pylint: disable=invalid-name
            self.getPidList = self.get_pid_list  # pylint: disable=invalid-name
            self.getAllKillCandidates = (  # pylint: disable=invalid-name
                self.get_all_kill_candidates
            )

        self.blocked_list = [
            "TMT_",
            "runtest",
            "behave",
            "qecore",
            "dogtail",
            "gnome-shell",
            "harness",
        ]
        self.permitted_list = ["org.gnome.Shell.Extensions", "org.gnome.Extensions"]

    def get_desktop_file_data(self) -> None:
        """
        Parse desktop file.

        .. note::

            Do **NOT** call this by yourself. This method is called by :func:`__init__`.
        """

        LOGGING.debug(get_func_params_and_values() + " for " + self.component)

        desktop_file_help = """
        Specify one when initializing your application in environment.py, options are:
        1) Specify your <name>.desktop file name 'desktop_file_name=\"<name>\"'.
        2) Provide full path to your .desktop file 'desktop_file_path=\"/path/to/desktop/file\"'.
        ' ... = context.sandbox.get_application(..., desktop_file_name="", desktop_file_path="")
        """

        # zenity/gnome-shell do not have desktop file.
        if not self.desktop_file_exists:
            LOGGING.debug(f"Not handling desktop file for component '{self.component}'")
            return

        if self.desktop_file_path:
            LOGGING.debug(
                " ".join(
                    (
                        "loading user provided .desktop file:",
                        f"'{self.desktop_file_path}'",
                    )
                )
            )
            desktop_file = self.desktop_file_path
        else:
            desktop_run = RunAndLog(
                " ".join(
                    (
                        f"rpm -qlf $(which {self.component}) |",
                        "grep /usr/share/applications/ |",
                        "grep .desktop |",
                        f"grep '{self.desktop_file_name}'",
                    )
                )
            )

            if desktop_run.return_code != 0:
                raise UserWarning(
                    f"Desktop file of application '{self.component}' was not found."
                )

            desktop_file = desktop_run.output.strip("\n")
            LOGGING.debug(f".desktop file found: '{desktop_file}'")

        desktop_files_list = desktop_file.split("\n")
        if len(desktop_files_list) != 1:
            assert False, "\n".join(
                (
                    f"More than one .desktop file found: \n{desktop_file}\n",
                    desktop_file_help,
                )
            )

        desktop_file_config = configparser.RawConfigParser()
        list_of_successfully_parsed_files = desktop_file_config.read(desktop_file)

        if not list_of_successfully_parsed_files:
            assert False, "".join(
                (f"Failed attempt to parse the .desktop file: '{desktop_file}'.")
            )

        self.name = desktop_file_config.get("Desktop Entry", "name")
        self.exec = desktop_file_config.get("Desktop Entry", "exec").split(" ")[0]
        self.icon = desktop_file_config.get("Desktop Entry", "icon", fallback=None)
        LOGGING.debug(
            " ".join(
                (
                    f"data name='{self.name}'",
                    f"exec='{self.exec}'",
                    f"icon='{self.icon}'",
                )
            )
        )

    def start_via_command(self, command=None, **kwargs) -> None:
        """
        Start application via command.

        :type command: str
        :param command: Complete command that is to be used to start application.

        :type in_session: bool
        :param in_session: Start application via command in session.
        """

        LOGGING.debug(get_func_params_and_values() + " for " + self.component)

        kill_override = self.kill
        in_session = False
        environ_to_set = None

        for key, val in kwargs.items():
            if "session" in str(key).lower():
                in_session = val

            if "kill" in str(key).lower():
                kill_override = val

            if "environ" in str(key).lower():
                environ_to_set = val

        # Evaluate environ variable to set from common steps.
        if environ_to_set is not None:
            LOGGING.debug("Attempting to setup environ before application start.")
            LOGGING.debug(f"Value of environ: '{environ_to_set}'.")

            keys_and_values_to_set = None
            if isinstance(environ_to_set, str):
                keys_and_values_to_set = re.findall(
                    r"(\w+)\s*=\s*([']{1}.+[']{1}|\S+)", environ_to_set
                )

            for key_and_value in keys_and_values_to_set:
                key, value = key_and_value[0], key_and_value[1]
                LOGGING.debug(f"Setting variable: '{key}' to value: '{value}'.")

                os.environ[key] = value

        # In both cases, if setup or not, use the os.environ. User might have set it.
        environ_to_set = os.environ

        if self.is_running() and kill_override:
            self.kill_application()

        command_or_exec_help = "\n".join(
            (
                "You attempted to use 'start_via_command' without any command provided.",
                "This function gets command from application's .desktop file or from user.",
                "",
                "You can either:",
                "1) In case of the command not changing, define it in your environment.py:",
                '    context.<application>.exec = "<command_to_run>"',
                "2) In case of the command changing in every test case:",
                '   * Start application "<application>" via command "<command>"',
            )
        )

        # In a case of an application with no desktop file.
        # Notify user that they are trying to use incorrect step.
        if command is None and self.exec is None:
            raise RuntimeError(command_or_exec_help)

        command_to_use = command if command else self.exec

        if in_session:
            if self.kiosk:
                raise RuntimeError("Start in session is not available in kiosk mode.")

            pressKey("Esc")
            keyCombo("<Alt><F2>")
            sleep(0.5)
            keyCombo("<Alt><F2>")
            sleep(0.5)

            # The self.shell is None in the moment of __init__.
            # Setting the self.shell for all applications once TestSandbox has it.
            enter_a_command = self.shell.findChild(
                lambda x: ("activate" in x.actions and x.showing) or
                (x.parent and x.parent.labeler and x.parent.labeler.name == "Run a Command")
            )
            enter_a_command.text = command_to_use
            sleep(0.5)
            pressKey("Enter")
        else:
            self.process = Popen(
                shlex.split(command_to_use),
                stdout=PIPE,
                stderr=PIPE,
                encoding="utf-8",
                env=environ_to_set,
            )

            process_is_running = self.process.poll() is None
            if not process_is_running:
                stdout_data, stderr_data = self.process.communicate()

                stdout_data = stdout_data.strip("\n")
                stderr_data = stderr_data.strip("\n")

                error_message = "\n".join(
                    (
                        f"The command used to start the application '{command_to_use}' failed.",
                        f"The 'stdout_data' of executed command are: '{stdout_data}'.",
                        f"The 'stderr_data' of executed command are: '{stderr_data}'.",
                    )
                )
                raise RuntimeError(error_message)

        self.wait_before_app_starts(30)
        self.instance = self.get_root()

    def start_via_menu(self, kill=None) -> None:
        """
        Start application via menu.

        Starting the application by opening shell overview and typing the application
        name that is taken from the application's desktop file. This does no longer work
        in a new gnome-classic as it lost the search bar.
        """

        LOGGING.debug(get_func_params_and_values() + " for " + self.component)

        if self.kiosk:
            raise RuntimeError("Start via menu is not available in kiosk mode.")

        if "classic" in self.session_desktop:
            assert False, "".join(
                (f"Application cannot be started via menu in {self.session_desktop}.")
            )

        if not self.desktop_file_exists:
            raise UserWarning(
                " ".join(
                    (
                        f"The target '{self.a11y_app_name}' doesn't have desktop file.",
                        "Indication of user failure!",
                    )
                )
            )

        kill_override = kill if kill else self.kill

        if self.is_running() and kill_override:
            self.kill_application()

        overview_action(action="show")

        sleep(1)
        typeText(self.name)
        pressKey("Enter")

        self.wait_before_app_starts(30)
        self.instance = self.get_root()

    def close_via_shortcut(self) -> None:
        """
        Close application via shortcut.

        Closing application via shortcut Ctrl+Q.
        If for any reason the application does not have this shortcut you can
        define the shortcut to use in class attribute :py:attr:`exit_shortcut`

        .. note::

            Format of the shortcut is a string with each key character encapsuled in <>.
            Here are  a few examples: <Ctrl><Q> <Alt><F4> <Ctrl><Shift><Q>
        """

        LOGGING.debug(get_func_params_and_values() + " for " + self.component)

        if not self.is_running():
            raise RuntimeWarning(
                "".join(
                    (
                        f"Application '{self.a11y_app_name}' is no longer running. ",
                        "Indication of test failure!",
                    )
                )
            )

        keyCombo(self.exit_shortcut)

        self.wait_before_app_closes(30)
        self.instance = None

    def already_running(self) -> None:
        """
        If application is started by other means, other than methods from this class,
        this will retrieve the root of the application.
        """

        LOGGING.debug(get_func_params_and_values() + " for " + self.component)

        self.wait_before_app_starts(15)
        self.instance = self.get_root()

    def get_root(self) -> gi_repository_Atspi_Accessible:
        """
        Get accessibility root of application.

        :return: Return root object of application.
        :rtype: <dogtail.tree.root.application>

        This method is used upon application start to retrieve a11y object to
        use in the test. You do not need to use this by yourself, but can be useful
        in some situations.
        """

        LOGGING.debug(get_func_params_and_values() + " for " + self.component)

        if self.component != self.a11y_app_name:
            LOGGING.debug(
                f"Get root for '{self.component}' with '{self.a11y_app_name}'"
            )

        # Importing here as there is sometimes an issue with accessibility
        # if the connection is not ready yet.
        # This will make sure the import will happen after the session is loaded.
        from dogtail.tree import (
            root,
        )

        return root.application(self.a11y_app_name)

    def is_running(self) -> bool:
        """
        Get running state of application.
        This state is retrieved by checking if application is present
        in the accessibility tree.

        :return: Return state of application. Running or not.
        :rtype: bool

        This method is used by various other methods in this class to ensure correct
        behavior. You do not need to use this by yourself, but can be useful in some
        situations.
        """

        LOGGING.debug(get_func_params_and_values() + " for " + self.component)

        is_running = False

        # Give an application list a few more tries to load. Following error exists:
        # GLib.GError: atspi_error: The application no longer exists (0)
        for _ in range(3):
            try:
                # Preventing issues of loading a11y on import before session is ready.
                from dogtail.tree import (
                    root,
                )

                self.application_list = [x.name for x in root.applications()]
                is_running = self.a11y_app_name in self.application_list
                LOGGING.debug(f"{self.component} Atspi tree check: '{is_running}'")
                return is_running

            except RuntimeError:
                LOGGING.debug(f"{self.component} is_running(self) - RuntimeError")
                return False

    def get_pid_list(self) -> str:
        """
        Get list of processes of running application.

        :return: Return all running processes of application, \
            separated by new line character, not converting to list. \
            Return nothing if application is not running.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`get_all_kill_candidates`
            when stopping the application.
        """

        LOGGING.debug(get_func_params_and_values() + " for " + self.component)

        if self.is_running():
            return RunAndLog(f"pgrep -fla {self.app_process_name}").output.strip("\n")

        return ""

    def get_all_kill_candidates(self) -> list:
        """
        Take result of :func:`get_pid_list` and return only processes of application.

        :rtype: list
        :return: Return all IDs of application processes.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`kill_application`
            when stopping the application.

        If kill candidate happens to have
        ['runtest', 'behave', 'dogtail', '/usr/bin/gnome-shell']
        in its process name. Process will not be killed.
        Return empty list if no satisfactory process was found.
        This prevents test name colliding with found process so that
        we will not kill the test itself.
        """

        LOGGING.debug(get_func_params_and_values() + " for " + self.component)

        application_pid_string = self.get_pid_list()
        if application_pid_string:
            application_pid_list = application_pid_string.split("\n")
        else:
            return []

        final_pid_list = []
        for process in application_pid_list:
            LOGGING.debug(f"Evaluation of process: '{process}'")

            # Evaluate the block and allow lists.
            block_the_cleanup = [
                blocked_item in process for blocked_item in self.blocked_list
            ]
            allow_the_cleanup = [
                allowed_item in process for allowed_item in self.permitted_list
            ]

            # Block list evaluation for logging to quickly debug things.
            LOGGING.debug(f"Block list: '{self.blocked_list}'")
            LOGGING.debug(f"Block evaluation: '{block_the_cleanup}'")
            # Allow list evaluation for logging to quickly debug things.
            LOGGING.debug(f"Allow list: '{self.permitted_list}'")
            LOGGING.debug(f"Allow evaluation: '{allow_the_cleanup}'")

            # We cleanup only on 'no block' or with 'allow' even if block was made.
            if not any(block_the_cleanup) or any(allow_the_cleanup):
                LOGGING.debug(f"Adding '{process}' to cleanup list.")
                extracted_pid = process.split(" ", 1)[0]
                try:
                    final_pid_list.append(int(extracted_pid))
                except ValueError:
                    # Skip non-digits.
                    pass
            else:
                LOGGING.debug(
                    f"Attempt to add '{process}' to cleanup list was blocked."
                )

        LOGGING.debug(f"Final pid list: '{final_pid_list}'")
        return final_pid_list

    def kill_application(self) -> None:
        """
        Kill application.

        This method is used by :func:`start_via_command` and :func:`start_via_menu`
        to ensure the application is not running when starting the test.
        So we kill all application instances and open a new one to test on.
        You do not need to use this by yourself, but can be useful in some situations.
        """

        LOGGING.debug(get_func_params_and_values() + " for " + self.component)

        if self.is_running() and self.kill:
            if not self.kill_command:
                for pid in self.get_all_kill_candidates():
                    RunAndLog(f"sudo kill -9 {pid} > /dev/null")
            else:
                RunAndLog(self.kill_command)

    # Following two could be merged, I could not think of a nice way of doing it though.
    def wait_before_app_starts(self, time_limit) -> None:
        """
        Wait before application starts.

        :type time_limit: int
        :param time_limit: Number which signifies time before the run is stopped.
        """

        LOGGING.debug(get_func_params_and_values() + " for " + self.component)

        for _ in range(time_limit * 10):
            if not self.is_running():
                sleep(0.1)
            else:
                return

        assert False, " ".join(
            (
                f"Application '{self.a11y_app_name}' was not found",
                f"in application tree: '{self.application_list}'.",
            )
        )

    def wait_before_app_closes(self, time_limit) -> None:
        """
        Wait before application stops.

        :type time_limit: int
        :param time_limit: Number which signifies time before the run is stopped.
        """

        LOGGING.debug(get_func_params_and_values() + " for " + self.component)

        for _ in range(time_limit * 10):
            if self.is_running():
                sleep(0.1)
            else:
                return

        assert False, " ".join(
            (
                f"Application '{self.a11y_app_name}' was still found",
                f"in application tree: '{self.application_list}'.",
            )
        )
