#!/usr/bin/env python3
"""
Utility file that provides various functions.
"""


# pylint: disable=broad-exception-caught
# pylint: disable=protected-access
# pylint: disable=invalid-name
# pylint: disable=import-outside-toplevel
# pylint: disable=import-error
# ruff: noqa: E501
# ruff: noqa: E402

import os
import sys
import traceback
import shlex
from functools import wraps, partial
from subprocess import STDOUT, CalledProcessError, TimeoutExpired, check_output
from time import sleep, time
from types import FunctionType
from typing import TypeVar

# Satisfy the typing hint but without the need to import entire class.
gi_repository_atspi_accessible = TypeVar("gi_repository_atspi_accessible")
Application = TypeVar("Application")

QE_DEVELOPMENT = not os.path.isdir("/mnt/tests/")

from qecore.logger import Logging
logging_class = Logging()
LOGGING = logging_class.logger


def non_critical_execution(function):
    """
    Decorator for non critical functions.
    Do no throw the entire execution away because of an error in non critical parts.

    :param function: Function to execute in try catch block.
    :type function: function
    """

    @wraps(function)
    def wrapper_over_function_with_arguments(self, *args, **kwargs) -> None:
        """
        Wrapper for a function accepting arbitrary arguments.
        """

        try:
            return function(self, *args, **kwargs)
        except Exception as error:
            if (
                hasattr(self, "context")
                and self.context
                and hasattr(self.context, "embed")
            ):
                self.context.embed(
                    mime_type="text/plain",
                    data=repr(error),
                    caption=f"Error while executing: '{function.__name__}'",
                )

            # No matter what happens, send the error to stdout.
            LOGGING.info(
                f"_non_critical_execution in function '{function.__name__}'\n{error}"
            )
            traceback.print_exc(file=sys.stdout)

    return wrapper_over_function_with_arguments


def get_application(context, application) -> Application:
    """
    Get Application class instance of an application, based upon given name.

    :type context: <behave.runner.Context>
    :param context: Context object that is passed from common_steps.

    :type application: str
    :param application: String of application identification: name.

    :rtype: <qecore.application.Application>
    :return: Application class instance

    .. note::

        Do **NOT** call this by yourself.
        This function is called by :mod:`common_steps`.
    """

    app_class_to_return = None
    try:
        # Get app from environment file.
        app_class_to_return = getattr(context, application)
    except AttributeError:
        # Get app from sandbox application list.
        for app in context.sandbox.applications:
            if app.component == application:
                app_class_to_return = app
                break
    except TypeError:
        app_class_to_return = context.sandbox.default_application
        assert context.sandbox.default_application is not None, "\n".join(
            (
                "Default application was not found. Check your environment file!",
                "This is indication that no application was defined in environment.py.",
            )
        )

    assert app_class_to_return is not None, "\n".join(
        (
            f"Application '{application}' was not found.",
            "Possibly wrongly defined application in environment.py file",
            "or incorrect use of decorator in .feature file.",
        )
    )

    assert not isinstance(app_class_to_return, str), " ".join(
        (
            "Application class was not found.",
            "Usually indication of not installed application.",
        )
    )

    return app_class_to_return


def get_application_root(  # pylint: disable=unused-argument
    context, application
) -> gi_repository_atspi_accessible:
    """
    Get Accessibility object of an application, based upon given name.

    :type context: <behave.runner.Context>
    :param context: Context object that is passed from common steps.

    :type application: str
    :param application: String of application identification: name.

    :rtype: <dogtail.tree.root.application>
    :return: Return root object of application.

    .. note::

        Do **NOT** call this by yourself.
        This function is called by :mod:`common_steps`.
    """

    from dogtail.tree import (
        root,
    )

    try:
        root_to_return = root.application(application)
    except Exception as error:
        traceback.print_exc(file=sys.stdout)
        raise UserWarning(
            "".join(
                (
                    "Application was not found in accessibility. ",
                    "Check your environment or feature file!",
                )
            )
        ) from error

    return root_to_return


def run(command, timeout=None) -> str:
    """
    Execute a command and get output.

    :type command: str
    :param command: Command to be executed.

    :rtype: str
    :return: Return string value of command output or exception error output.
    """

    try:
        output = check_output(
            command, shell=True, stderr=STDOUT, encoding="utf-8", timeout=timeout
        )
        return output
    except CalledProcessError as error:
        return error.output


def run_verbose(command, timeout=None) -> tuple:
    """
    Execute a command and get output in verbose format.

    :type command: str
    :param command: Command to be executed.

    :rtype: list
    :return: Return list with following format (output, return code, exception).
    """

    try:
        output = check_output(
            command, shell=True, stderr=STDOUT, encoding="utf-8", timeout=timeout
        )
        return (output, 0, None)
    except CalledProcessError as error:
        return (error.output, error.returncode, error)


def run_embed(context, command, *a, **kw):
    """
    Execute a command and get output.
    This version of command run will also embed results to the html log.

    :type context: <behave.runner.Context>
    :param context: Context object that will be used embedding.

    :type command: str
    :param command: Command to be executed.

    :rtype: list
    :return: Return list with following format (output, return code, exception).
    """

    try:
        output = check_output(
            command, shell=True, stderr=STDOUT, *a, **kw, encoding="utf-8"
        )
        return_code = 0
        error = None
    except CalledProcessError as process_error:
        output = process_error.output
        return_code = process_error.returncode
        error = process_error

    context.embed("text/plain", f"$?={return_code}", caption=f"{command} result")
    context.embed("text/plain", output, caption=f"{command} output")

    return (error.output, error.returncode, error)


def overview_action(action="hide") -> None:
    """
    Hide or show application overview.

    :type action: str
    :param action: Hide or show application overview.

    This function takes only 'hide' and 'show' value.
    """

    # DBus calls are deprecated
    # https://gitlab.gnome.org/GNOME/gnome-shell/-/merge_requests/1970

    LOGGING.debug(f"Overview action: '{action}'")

    assert action in ["hide", "show"], "".join(
        (
            "Unknown option, only defined ones are 'show' or 'hide'.",
            f"You tried to use: '{action}'",
        )
    )

    from dogtail.tree import (
        root,
    )

    gnome_shell = root.application("gnome-shell")

    activities_buttons = gnome_shell.findChildren(
        lambda x: x.name == "Activities"
        and (x.roleName == "label" or x.roleName == "toggle button")
    )

    if len(activities_buttons) == 1:
        from dogtail.predicate import (
            GenericPredicate,
        )

        # Get the only child as an object.
        activities_button = activities_buttons[0]

        # Find Ancestor unfortunately takes only Predicates not lambdas alone, \
        # will use it since implementing it here would be too long.

        activities_toggle_button = None
        # If the label was found, find an ancestor with toggle button.
        if activities_button.roleName == "label":
            activities_toggle_button = activities_button.findAncestor(
                GenericPredicate(roleName="toggle button")
            )
        # If label was not found the toggle button is the actual node we found.
        else:
            activities_toggle_button = activities_button

        # Make sure the activities is in wanted state.
        for _ in range(5):
            if (action == "hide" and activities_toggle_button.checked) or (
                action == "show" and not activities_toggle_button.checked
            ):
                activities_toggle_button.click()
                sleep(1)

            else:
                return

    else:
        pass  # possibly in gnome-classic


# behave-common-steps leftover.
def wait_until(
    tested, element=None, timeout=30, period=0.25, params_in_list=False
) -> bool:
    """
    This function keeps running lambda with specified params until the
    result is True or timeout is reached. Instead of lambda, Boolean variable
    can be used instead.

    Sample usages::

        >>> wait_until(lambda x: x.name != 'Loading...', context.app.instance)
        Pause until window title is not 'Loading...'.
        Return False if window title is still 'Loading...'
        Throw an exception if window doesn't exist after default timeout

        >>> wait_until(lambda element, expected: x.text == expected,
            (element, 'Expected text'), params_in_list=True)
        Wait until element text becomes the expected (passed to the lambda)

        >>> wait_until(dialog.dead)
        Wait until the dialog is dead
    """

    if isinstance(tested, bool):

        def curried_func():
            return tested

    # Or if callable(tested) and element is a list or a tuple.
    elif (
        isinstance(tested, FunctionType)
        and isinstance(element, (tuple, list))
        and params_in_list
    ):
        curried_func = partial(tested, *element)
    # Or if callable(tested) and element is not None?
    elif isinstance(tested, FunctionType) and element is not None:
        curried_func = partial(tested, element)
    else:
        curried_func = tested

    exception_thrown = None
    must_end = int(time()) + timeout
    while int(time()) < must_end:
        try:
            if curried_func():
                return True
        except Exception as error:
            # If lambda has thrown the exception we'll re-raise it later
            # and forget about if lambda passes.
            exception_thrown = error
        sleep(period)
    if exception_thrown is not None:
        raise exception_thrown

    return False


KEY_VALUE = {
    "Alt": 64,
    "Alt_L": 64,
    "Alt_R": 108,
    "Shift": 50,
    "Shift_L": 50,
    "Shift_R": 62,
    "Ctrl": 37,
    "Tab": 23,
    "Super": 133,
}


class HoldKey:
    """
    Simple utility to press a key and do some other actions.

    This is a context manager so the usage is as follows::

        >>> with HoldKey("Alt"):
        >>>     do_some_stuff()

    """

    def __init__(self, key_name) -> None:
        # Import only when required.
        from dogtail.rawinput import (
            holdKey,
        )

        self.key_name = key_name
        holdKey(self.key_name)

    def __enter__(self):
        return self

    def __exit__(self, my_type, value, trace) -> None:
        # Import only when required.
        from dogtail.rawinput import (
            releaseKey,
        )

        releaseKey(self.key_name)


class Tuple(tuple):
    """
    Simple tuple class with some defined arithmetic operations.

    :type command: tuple
    :param command: Tuple.
    """

    def __add__(self, other):
        return Tuple(x + y for x, y in zip(self, other))

    def __rmul__(self, other):
        return Tuple(other * x for x in self)

    def __eq__(self, other) -> bool:
        return all(x == y for x, y in zip(self, other))

    def __lt__(self, other) -> bool:
        return self[0] < other[0] or self[1] < other[1]

    def __gt__(self, other) -> bool:
        return self[0] > other[0] or self[1] > other[1]


def get_center(node) -> Tuple:
    """
    Simple utility to get the center of the node.

    :type node: <dogtail.tree.Node>
    :param node: Node passed to the function.

    :rtype: Tuple
    :return: Tuple with coordinates of the center of a Node.
    """

    return Tuple(
        (
            int(node.position[0] + node.size[0] / 2),
            int(node.position[1] + node.size[1] / 2),
        )
    )


def validate_command(command) -> str:
    """
    Simple utility to try and escape any character that is not alpha character.

    :type command: str
    :param command: Command to be executed.

    :rtype: str
    :return: Validated command.
    """

    parsed_command = shlex.split(command)
    valid_command = ""
    for command_part in parsed_command:
        for character in command_part:
            valid_command += f"\\{character}" if not character.isalpha() else character
        valid_command += " "
    return valid_command


def verify_path(template_path):
    """
    Simple utility to verify if the file exists.

    :type template_path: str
    :param template_path: File location.

    :rtype: str or None
    :return: File path if found, None if not found.
    """

    try:
        assert os.path.isfile(template_path)
    except Exception as error:
        raise UserWarning(f"Desired file was not found: {error}") from error
    return template_path


def plain_dump(node) -> None:
    """
    Simple attempt to get more information from a11y tree.

    :type node: <dogtail.tree.root.application>
    :param node: Accessibility node.
    """

    spacer = " "

    def crawl(node, depth) -> None:
        dump(node, depth)
        for child in node.children:
            crawl(child, depth + 1)

    def dump_std_out(item, depth) -> None:
        print(
            "".join(
                (
                    spacer * depth,
                    str(item),
                    f"     [p:{item.position}, ",
                    f"s:{item.size}, ",
                    f"vis:{item.visible}, ",
                    f"show:{item.showing}]",
                )
            )
        )

    dump = dump_std_out
    crawl(node, 0)


def patch_scenario(scenario, max_attempts=3, stability=False):
    """
    Changing implementation of behave patch to enable stability logic.
    https://github.com/behave/behave/blob/main/behave/contrib/scenario_autoretry.py
    """

    import functools
    from behave.model import ScenarioOutline

    def scenario_run_with_retries(scenario_run, *args, **kwargs):
        final_attempt = 0
        for attempt in range(1, max_attempts + 1):
            final_attempt = attempt
            # Log what attempt are we on.
            if attempt < max_attempts + 1:
                logic = "Stability" if stability else "Auto retry"
                LOGGING.debug(f"{logic} scenario attempt '{attempt}'.")

            # The scenario_run makes the actual scenario run
            # Returns True on failure.
            scenario_run_failed = scenario_run(*args, **kwargs)

            # So if the result is False it did not fail.
            if not scenario_run_failed and not stability:
                # Return False which means it did not fail.
                LOGGING.debug(f"Auto retry scenario passed after '{attempt}' attempts.")
                return False

            # If the run failed and we are testing stability, end the run here as fail.
            if scenario_run_failed and stability:
                # Return True which means it did fail.
                LOGGING.debug(f"Scenario is not stable, fail on attempt '{attempt}'.")
                return True

        # If stability is in effect and we get here, the logic passes.
        if stability:
            # If it got to this point nothing has failed.
            LOGGING.debug(f"The scenario is stable after '{final_attempt}' attempts.")
            return False

        # If stability is not in effect it should end much earlier.
        LOGGING.debug(f"Auto retry scenario failed after '{final_attempt}' attempts.")
        return True

    if isinstance(scenario, ScenarioOutline):
        scenario_outline = scenario
        for scenario in scenario_outline.scenarios:
            scenario_run = scenario.run
            scenario.run = functools.partial(scenario_run_with_retries, scenario_run)
    else:
        scenario_run = scenario.run
        scenario.run = functools.partial(scenario_run_with_retries, scenario_run)


def get_func_params_and_values():
    """
    Simple way to have logging data from the place it was called in.
    """

    # Get callers frame parameters.
    _local_func_parameters = sys._getframe().f_back.f_locals.keys()
    # Get callers frame parameter values.
    _local_func_parameters_value = sys._getframe().f_back.f_locals.values()

    _map_of_keys_and_values = [
        x if "self" == x else x if "context" == x else str(x) + "=" + str(y)
        for x, y in zip(_local_func_parameters, _local_func_parameters_value)
    ]

    return f"({', '.join(_map_of_keys_and_values)})"


class RunAndLog:
    """
    Utility class for better representation and logging of executed command.
    """

    def __init__(self, command, timeout=None):
        self._command = command
        self._timeout = timeout

        self._output = None
        self._return_code = None
        self._error = None

        self.run_and_log()

    def formatted_output(self):
        """
        Based on number of new lines decide how to format it.
        """

        # Lets 'repr' the output if there is only one line.
        # If there are more lines lets keep the log more readable and output it as is.
        if self._output and self._output.count("\n") > 1:
            return self._output

        return repr(self._output)

    def run_and_log(self):
        """
        Run and Log the command execution.
        """

        try:
            LOGGING.debug(f"Executing: '{self._command}'")
            self._output = check_output(
                self._command,
                shell=True,
                stderr=STDOUT,
                encoding="utf-8",
                timeout=self._timeout,
            )

            self._return_code = 0
            self._error = None

            LOGGING.debug(
                " ".join(
                    (
                        f"Command run: output='{self.formatted_output()}',",
                        f"return_code='{self._return_code}',",
                        f"error='{self._error}'",
                    )
                )
            )

        except CalledProcessError as error:
            self._output = error.output
            self._return_code = error.returncode
            self._error = error
            LOGGING.debug(
                " ".join(
                    (
                        f"CalledProcessError caught: output='{self.formatted_output()}',",
                        f"return_code='{self._return_code}',",
                        f"error='{self._error}'",
                    )
                )
            )
        except TimeoutExpired as error:
            self._output = error.output
            self._return_code = -1
            self._error = error
            LOGGING.debug(
                " ".join(
                    (
                        f"TimeoutExpired caught: output='{self.formatted_output()}',",
                        f"return_code='{self._return_code}',",
                        f"error='{self._error}'",
                    )
                )
            )

        except Exception as error:
            self._output = error
            self._return_code = -1
            self._error = error
            LOGGING.debug(
                " ".join(
                    (
                        f"Unexpected Exception caught: output='{self.formatted_output()}',",
                        f"return_code='{self._return_code}',",
                        f"error='{self._error}'",
                    )
                )
            )

    @property
    def command(self):
        """
        Get and log the command value.
        """

        LOGGING.debug(f"Command value: '{self._command}'")

        return self._command

    @property
    def timeout(self):
        """
        Get and log the timeout value.
        """

        LOGGING.debug(f"Timeout value: '{self._timeout}'")

        return self._timeout

    @property
    def output(self):
        """
        Get and log the output value.
        """

        LOGGING.debug(f"Output value: '{self.formatted_output()}'")

        return self._output

    @property
    def return_code(self):
        """
        Get and log the return_code value.
        """

        LOGGING.debug(f"Return code value: '{self._return_code}'")

        return self._return_code

    @property
    def error(self):
        """
        Get and log the error value.
        """

        LOGGING.debug(f"Error value: '{self._error}'")

        return self._error

    def __str__(self):
        return str(self._output)


def log_message_to_journal(priority, identifier, invoke):
    """
    Invoke a program to be logged in journal.

    :param priority: Priority of the message.
    :type priority: str

    :param identifier: Identifier we want in the journal.
    :type identifier: str

    :param invoke: Invoke a program to execute.
    :type invoke: str
    """

    LOGGING.debug(get_func_params_and_values())

    # journal entry -p priority -t identifier [invoke a program]
    RunAndLog(
        " ".join(
            (
                "systemd-cat",
                f"-p {priority}",
                f"-t {identifier}",
                invoke,
            )
        )
    )


# Pulled from dogtail-2.0 code to make things easier.


class TreeRepresentationQecore:
    """
    Accessible Structure Representation from given Accessible Node.
    """

    def __init__(
        self, accessible_node, structure_format="plain", file_name=None, labels=False
    ):
        self.spacer = "  "
        self.format = structure_format
        self.accessible_node = accessible_node
        self.tree_representation = ""
        self.file_name = file_name
        self.labels = labels

    def _get_label_string(self, acc_object):
        labeler_string = ""
        if self.labels and acc_object.labeler:
            labeler_string += f" (labeler.text='{acc_object.labeler.text}') "
            labeler_string += f" (labeler.name='{acc_object.labeler.name}') "

        if self.labels and not acc_object.labeler:
            labeler_string += " (No labeler) "

        return labeler_string

    def _represent_structure_as_plain(self, acc_object, level=0):
        labeler_string = self._get_label_string(acc_object)

        tree_representation = (
            self.spacer * level + str(acc_object) + labeler_string + "\n"
        )

        for child in acc_object.children:
            # Not adding Action strings by choice, we can revisit in the future.

            tree_representation += self._represent_structure_as_plain(child, level + 1)

        return tree_representation

    def _represent_structure_as_verbose(self, acc_object, level=0):
        if not acc_object:
            return

        labeler_string = self._get_label_string(acc_object)

        verbose_str = "".join(
            (
                str(acc_object),
                " - ",
                f"(position:'{acc_object.position}', size:'{acc_object.size}', ",
                f"visible:{acc_object.visible}, showing:{acc_object.showing})",
                f"{labeler_string}",
            )
        )

        tree_representation = self.spacer * level + verbose_str + "\n"

        for child in acc_object.children:
            # Not adding Action strings by choice, we can revisit in the future.

            tree_representation += self._represent_structure_as_verbose(
                child, level + 1
            )

        return tree_representation

    def _represent_structure_as_tree(self, node, last=True, spacer=""):
        self._recursive_tree_structure_construction(node, last=last, spacer=spacer)
        return self.tree_representation

    def _recursive_tree_structure_construction(self, acc_object, last, spacer):
        if not acc_object:
            return

        prefix_spacer = "    "
        prefix_extend = " │  "
        suffix_branch = " ├──"
        suffix_last = " └──"

        labeler_string = self._get_label_string(acc_object)

        # Attempt to shorten the line.
        suffix_based_on_last = suffix_last if last else suffix_branch
        # Add a line to the tree representation.

        self.tree_representation += (
            (spacer + suffix_based_on_last + str(acc_object)) + labeler_string + "\n"
        )

        for index, child in enumerate(acc_object.children):
            # Not adding Action strings by choice, we can revisit in the future.

            # Check if the index is last.
            is_last = index == acc_object.get_child_count() - 1
            # Make a new spacer.
            new_spacer = spacer + (prefix_spacer if last else prefix_extend)

            self._recursive_tree_structure_construction(
                child, last=is_last, spacer=new_spacer
            )

    def load_data_to_file(self, data):
        """
        Insert Accessible Structure Representation to the file.

        :param data: Data to insert to the file.
        :type data: str

        :raises OSError: Raise OSError if the is an issue with file manipulation.
        """

        try:
            with open(self.file_name, "w", encoding="utf-8") as file_:
                file_.write(data)
        except OSError as error:
            raise OSError(f"Issue with opening '{self.file_name}' file.") from error

    def __str__(self):
        if self.format == "plain":
            plain_data = self._represent_structure_as_plain(self.accessible_node)

            if self.file_name:
                self.load_data_to_file(data=plain_data)
                return f"[ Plain structure was inserted in file '{self.file_name}'. ]"

            return plain_data

        if self.format == "verbose":
            verbose_data = self._represent_structure_as_verbose(self.accessible_node)

            if self.file_name:
                self.load_data_to_file(data=verbose_data)
                return f"[ Verbose structure was inserted in file '{self.file_name}'. ]"

            return verbose_data

        if self.format == "tree":
            tree_data = self._represent_structure_as_tree(self.accessible_node)

            if self.file_name:
                self.load_data_to_file(data=tree_data)
                return f"[ Tree structure was inserted in file '{self.file_name}'. ]"

            return tree_data

        return f"[Unknown format selected '{self.format}']"

    def __repr__(self):
        return "<Accessible Structure Representation>"


def keyboard_character_input(characters_to_write):
    """
    Type characters with keyboard using 'uinput' library.

    :param characters_to_write: Characters to typo with keyboard.
    :type characters_to_write: str
    """

    if os.geteuid() != 0:
        LOGGING.debug("Using 'uinput' library is not possible with non-root user.")
        raise RuntimeError("Using 'uinput' library is not possible with non-root user.")

    LOGGING.debug("Checking availability of 'uinput' library.")

    import importlib

    if not importlib.util.find_spec("uinput"):
        raise RuntimeError("Missing module 'uinput' on the System. Unable to use this function.")

    LOGGING.debug("The 'uinput' library is available.")

    import uinput
    from uinput import _chars_to_events

    events_to_emit = _chars_to_events(characters_to_write)

    for event in events_to_emit:
        with uinput.Device(events_to_emit) as device:
            sleep(0.2)
            device.emit_click(event)


def keyboard_key_input(key_to_press):
    """
    Press a keyboard key.

    :param characters_to_write: Characters to typo with keyboard.
    :type characters_to_write: str
    """

    if os.geteuid() != 0:
        LOGGING.debug("Using 'uinput' library is not possible with non-root user.")
        raise RuntimeError("Using 'uinput' library is not possible with non-root user.")

    LOGGING.debug("Checking availability of 'uinput' library.")

    import importlib

    if not importlib.util.find_spec("uinput"):
        raise RuntimeError("Missing module 'uinput' on the System. Unable to use this function.")

    LOGGING.debug("The 'uinput' library is available.")

    import uinput


    key_to_press_validated = key_to_press

    if key_to_press.lower() == "super":
        key_to_press_validated = "LEFTMETA"

    key_to_press = f"KEY_{str(key_to_press_validated).upper()}"
    key_exists = hasattr(uinput, key_to_press)
    LOGGING.debug(f"Attempting to use key '{key_to_press}', exists: '{str(key_exists)}'.")

    key_event = None
    if key_exists:
        key_event = getattr(uinput, key_to_press)
    else:
        raise RuntimeError(f"Attempting to use key '{key_to_press}', which does not exist.")

    with uinput.Device([key_event]) as device:
        sleep(0.2)
        device.emit_click(key_event)


def keyboard_key_combo_input(combo_string):
    """
    Press a keyboard key combo.

    :param characters_to_write: Characters to typo with keyboard.
    :type characters_to_write: str
    """

    if os.geteuid() != 0:
        LOGGING.debug("Using 'uinput' library is not possible with non-root user.")
        raise RuntimeError("Using 'uinput' library is not possible with non-root user.")

    LOGGING.debug("Checking availability of 'uinput' library.")

    import importlib

    if not importlib.util.find_spec("uinput"):
        raise RuntimeError("Missing module 'uinput' on the System. Unable to use this function.")

    LOGGING.debug("The 'uinput' library is available.")

    import uinput

    key_events = []

    import re
    combo_string_parsed = re.findall(r"<(.*?)>", combo_string)

    for key_to_press in combo_string_parsed:

        key_to_press_validated = key_to_press

        if key_to_press.lower() == "super":
            key_to_press_validated = "LEFTMETA"

        uinput_key = f"KEY_{str(key_to_press_validated).upper()}"
        uinput_key_exists = hasattr(uinput, uinput_key)
        LOGGING.debug(f"Attempting to use key '{uinput_key}', exists: '{str(uinput_key_exists)}'.")

        if uinput_key_exists:
            key_events.append(getattr(uinput, uinput_key))
        else:
            raise RuntimeError(f"Attempting to use key '{uinput_key}', which does not exist.")

    with uinput.Device(key_events) as device:
        sleep(0.2)
        device.emit_combo(key_events)


AUTOMATIC_LOGIN_IN_EFFECT = RunAndLog("pgrep -f '.*python.*qecore.*no-autologin'").return_code != 0
