#!/usr/bin/env python3
"""
TestSandbox class.
"""

# pylint: disable=broad-exception-caught
# pylint: disable=unused-wildcard-import
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=no-name-in-module
# pylint: disable=import-outside-toplevel
# pylint: disable=import-error
# pylint: disable=line-too-long
# pylint: disable=wildcard-import
# pylint: disable=bidirectional-unicode
# ruff: noqa: E402
# ruff: noqa: F403
# ruff: noqa: E501

import os
import sys
import base64
import traceback
import signal
import atexit
import time
import xml.etree.ElementTree as ET
from time import sleep
from pathlib import Path
from subprocess import Popen
from mimetypes import MimeTypes
from typing import Union
import behave
from behave.model import Step
import pkg_resources

from qecore.utility import AUTOMATIC_LOGIN_IN_EFFECT
try:
    from dogtail.utils import config, isA11yEnabled, enableA11y
    from dogtail.rawinput import keyCombo
except Exception as error:
    if not AUTOMATIC_LOGIN_IN_EFFECT:
        print(f"Expected issues in TestSandbox: '{error}'")
    else:
        raise Exception from error

from qecore.application import Application
from qecore.flatpak import Flatpak
from qecore.icons import qecore_icons, QECoreIcon
from qecore.utility import (
    RunAndLog,
    overview_action,
    non_critical_execution,
    get_func_params_and_values,
    log_message_to_journal,
)

# First check: dogtail utility for accessibility check and enabling.
if not isA11yEnabled() and AUTOMATIC_LOGIN_IN_EFFECT:
    print("Accessibility not detected running. Enabling via dogtail...")
    enableA11y()
    sleep(2)

# Second check: gsettings command to get the state and enable if set to false.
GET_ACCESSIBILITY = "gsettings get org.gnome.desktop.interface toolkit-accessibility"
SET_ACCESSIBILITY = "gsettings set org.gnome.desktop.interface toolkit-accessibility true"
if "true" not in RunAndLog(GET_ACCESSIBILITY).output and AUTOMATIC_LOGIN_IN_EFFECT:
    print("Accessibility not detected running. Enabling via gsettings command...")
    RunAndLog(SET_ACCESSIBILITY)

from qecore.logger import Logging
logging_class = Logging()
LOGGING = logging_class.logger


NO_VALUES = ["", "n", "no", "f", "false", "0"]


class TestSandbox:
    """
    TestSandbox class.
    """

    def __init__(self, component, context=None, kiosk=False) -> None:
        """
        :type component: str
        :param component: Name of the component that is being tested.

        :param context: Holds contextual information during the running of tests.
        :type context: <behave.runner.Context>

        .. note::

            You are able to use autoretry option via variable:
            AUTORETRY=<INT> behave -kt <test_name>

            You are able to use stability option via variable:
            STABILITY=<INT> behave -kt <test_name>

            You are able to use general logging via variable:
            LOGGING=yes behave -kt <test_name>

            You are able to enable backtrace generation from qecore with:
            BACKTRACE=yes behave -kt <test_name>

            You can enforce embedding for testing purposes via debug variable:
            QECORE_EMBED_ALL=yes

            You can start the execution with no cache which will delete created files:
            QECORE_NO_CACHE=yes behave -kt <test_name>

        """

        self._log_sandbox_initiation_to_journal(component=component)

        if context is not None:
            assert isinstance(context, behave.runner.Context), "".join(  # type: ignore
                "Unexpected argument, context should be <behave.runner.Context>"
            )

        # Handling environment variables.
        def _get_env_value_lower(env_value_to_get):
            return os.environ.get(env_value_to_get, "").lower()

        # Probably a good idea to move the rich text to variable RICH_TRACEBACK=true
        self._rich_traceback = _get_env_value_lower("RICH_TRACEBACK") not in NO_VALUES

        # Keep in mind to add any new value also to headless script.
        self._autoretry = _get_env_value_lower("AUTORETRY")
        self._stability = _get_env_value_lower("STABILITY")
        self._embed_all = _get_env_value_lower("QECORE_EMBED_ALL") not in NO_VALUES
        self._no_cache = _get_env_value_lower("QECORE_NO_CACHE") not in NO_VALUES
        self._enable_screencast = _get_env_value_lower("QECORE_ENABLE_SCREENCAST") not in NO_VALUES
        self._enable_screencast_from_console = _get_env_value_lower("QECORE_ENABLE_SCREENCAST") != ""
        self._logging_to_console = _get_env_value_lower("LOGGING") not in NO_VALUES
        self._production = _get_env_value_lower("PRODUCTION") not in NO_VALUES
        self._production_from_console = _get_env_value_lower("PRODUCTION") != ""
        self._generate_backtrace = _get_env_value_lower("BACKTRACE") not in NO_VALUES

        # Logging to the console.
        if self._logging_to_console:
            logging_class.qecore_debug_to_console()
            # Debug is showing only after above function, logging it after it is done.
            LOGGING.info("Setting qecore to log in console.")

        # Handling resetting of the logger class to not have logs from previous runs.
        # In previous versions this was done simply by erasing the file.
        # But in special cases when we run another script within TestSandbox as another
        # process, it did not find the logger and deleted the file to create another
        # logger, in effect erasing all of our logs in that run.
        # Now we simply null the file on request so that the logger is functional from
        # all files in our automation stack.
        LOGGING.debug(f"Truncating logger file located at '{logging_class.log_file}'.")
        logging_class.qecore_truncate_the_logger_file()

        if context is not None:
            for formatter in context._runner.formatters:
                if (
                    "pretty" in formatter.name
                    and getattr(formatter, "colored", None) is not None
                ):
                    formatter.colored = not self._logging_to_console

        LOGGING.debug(f"(self, component={component}, context={repr(context)})")

        # This might actually be required - we can fix the issue while running.
        self.do_not_let_dogtail_abort_on_bugged_a11y()

        # Older versions of dogtail do not have this option.
        # Qecore still must work on older distributions.
        try:
            LOGGING.debug(f"gtk4 offset: '{config.gtk4Offset}'")
        except Exception:
            LOGGING.debug("No gtk4 offset config option defined.")

        LOGGING.debug("Accessibility is somehow turning off, making another check.")
        # First check: dogtail utility for accessibility check and enabling.
        if not isA11yEnabled() and AUTOMATIC_LOGIN_IN_EFFECT:
            print("Accessibility not detected running. Enabling via dogtail.")
            enableA11y()
            sleep(2)

        # Second check: gsettings command to get the state and enable if set to false.
        if "true" not in RunAndLog(GET_ACCESSIBILITY).output and AUTOMATIC_LOGIN_IN_EFFECT:
            print("Accessibility not detected running. Enabling via gsettings command.")
            RunAndLog(SET_ACCESSIBILITY)

        # Evaluate if the session is running in --unsafe-mode.
        LOGGING.debug("Evaluating --unsafe-mode in gnome-shell")
        self.unsafe_mode_query = " ".join(
            (
                "gdbus call --session --dest org.gnome.Shell --object-path /org/gnome/Shell",
                "--method org.gnome.Shell.Eval 'global.context.unsafe_mode'",
            )
        )
        self.unsafe_mode = RunAndLog(self.unsafe_mode_query)

        self.context = context
        self.automatic_login = AUTOMATIC_LOGIN_IN_EFFECT
        self.shell = None

        self.faulty_session = False

        if self.context:
            self.context.failed_setup = None

        self.kiosk = kiosk
        self.component = component
        self.current_scenario = None
        self.background_color = None
        self.background_image_revert = False
        self.background_image_location = ""

        self.disable_welcome_tour = True

        self.disable_gtk4_shadows = True

        self.enable_animations = None

        self.enable_close_yelp = True

        self.logging_start = None
        self.capture_screenshot_run = None
        self.capture_screenshot_portal_run = None
        self.capture_screenshot_dbus = (None, None)
        self.capture_screenshot_temp_file = "/tmp/screenshot.png"

        self.record_video = (
            self._enable_screencast if self._enable_screencast_from_console else True
        )
        LOGGING.debug(f"Setting record_video to: '{self.record_video}'")
        self.record_video_pid = None

        self.attach_video = True
        self.attach_video_on_pass = False

        self.attach_journal = True
        self.attach_journal_on_pass = False

        self.attach_coredump = self._generate_backtrace
        self.attach_coredump_on_pass = True
        self.attach_coredump_file_check = False

        self.attach_screenshot = True
        self.attach_screenshot_on_pass = False
        self.which_gnome_screenshot_run = False

        self.failed_test = False

        self.opt_in_tree_on_fail = False

        self.attach_faf = True
        self.attach_faf_on_pass = True

        self.status_report = True

        self.logging_cursor = None
        self.test_execution_start = None

        self.workspace_return = False

        self.set_keyring = True
        self.keyring_process_pid = None

        self.wait_for_stable_video = True

        # Turn production off via environ in local machine.
        self.production = self._production if self._production_from_console else True
        LOGGING.debug(f"Setting production to: '{self.production}'")

        self.timeout_handling = True

        self._after_scenario_hooks = []
        self.reverse_after_scenario_hooks = False

        self.html_report_links = True

        self.embed_separate = False
        self.change_title = True
        self.session_icon_to_title = True
        self.default_application_icon_to_title = False

        self.applications = []
        self.package_list = {"gnome-shell", "mutter", component}
        self.default_application = None

        self._new_log_indicator = True
        self._scenario_skipped = False

        self._project_git_url = None
        self._project_git_commit = None

        self._attach_qecore_debug = True
        self._attach_qecore_debug_on_pass = False
        self._qecore_debug_log_file = "/tmp/qecore_logger.log"

        self._set_up_before_feature_hook()
        self._set_up_scenario_skip_check()
        self._retrieve_session_data()
        self._check_for_coredump_fetching()
        self._set_g_debug_environment_variable()

    def before_scenario(self, context, scenario) -> None:
        """
        Actions that are to be executed before every scenario.

        :param context: Holds contextual information during the running of tests.
        :type context: <behave.runner.Context>

        :type scenario: <Scenario>
        :param scenario: Pass this object from environment file.

        .. note::

            You can enforce embedding for testing purposes via debug variable:
            QECORE_EMBED_ALL=yes
        """

        LOGGING.debug(get_func_params_and_values())

        if hasattr(context, "failed_setup") and context.failed_setup:
            # Upon failed setup we care only about embedding setup.
            self._set_up_embedding(context)
            # Load the data from failed setup variable.
            data = context.failed_setup
            # Embed the data to the log.
            context.embed("text", data, "Failed setup in Before All")
            sys.exit(1)

        # Setup embedding early before any other part has a chance to fail.
        self._set_up_embedding(context)

        self._scenario_skipped = False

        self.failed_test = False

        # If QECORE_EMBED_ALL is set, set production to True.
        self.production = self.production or self._embed_all

        if not self.automatic_login:
            LOGGING.debug(" ======== AutomaticLogin disabled - ending before_scenario. ======== ")
            return

        self._wait_until_shell_becomes_responsive()

        self.disable_shadows_for_gtk4()

        self._set_welcome_tour()

        self._set_animations()

        self.current_scenario = scenario.tags[-1]
        self._set_journal_log_start_time()
        self._set_coredump_log_start_time()

        if not self.kiosk:
            overview_action(action="hide")

        self.disable_debug_logs_from_dogtail()

        self.set_typing_delay(0.2)

        self.set_debug_to_stdout_as(False)
        self._close_yelp()
        self._close_initial_setup()
        self._copy_data_folder()
        self.set_blank_screen_to_never()

        if self.change_title:
            self._set_title(context)

        if self.timeout_handling:
            self._set_timeout_handling()

        if self.record_video and self.production:
            self._start_recording()

        self._detect_keyring()
        self._return_to_home_workspace()

        # Separator of testing suite and setup logs.
        LOGGING.debug(" ======== Start of the test suite section ======== ")
        self._log_starting_automation_suite_to_journal(scenario)

    def after_scenario(self, context, scenario) -> None:
        """
        Actions that are to be executed after every scenario.

        :param context: Holds contextual information during the running of tests.
        :type context: <behave.runner.Context>

        :type scenario: <Scenario>
        :param scenario: Pass this object from environment file.
        """

        # Separator of testing suite and setup logs.
        LOGGING.debug(" ======== End of the test suite section ======== ")
        self._log_ending_automation_suite_to_journal(scenario)

        LOGGING.debug(get_func_params_and_values())

        # Adding faulty session skip, no need to do after_scenario with crashed shell.
        if self.faulty_session:
            raise RuntimeError("Session was not usable. Unable to continue.")

        # Define variable for step to use in case of rich text print.
        failed_step = None

        LOGGING.debug(f"Handling Scenario Status: '{scenario.status}'")
        if scenario.status not in ("passed", "skipped"):
            self.failed_test = True

            for step in scenario.steps:
                LOGGING.debug(f"Handling Step Status: '{step.status}'")
                if step.status not in ("passed", "skipped"):
                    failed_step = step

        # Check if the test failed and if failed step was located.
        # Do this only if RICH_TRACEBACK is enabled.
        if self._rich_traceback and self.failed_test and failed_step:
            self.print_rich_traceback(failed_step)

        self._capture_image()

        if self.background_image_revert:
            self._revert_background_image()

        if self.record_video and self.production:
            self._stop_recording()

        if not self.kiosk and self.automatic_login:
            try:
                overview_action(action="hide")
            except Exception as error:
                LOGGING.debug(f"Lets not fail in after_scenario on atspi issue: '{error}'")

        # If users opt in they can get tree in the html report on fail to check nodes.
        # Needs to be executed before application cleanup starts.
        if self.failed_test and self.opt_in_tree_on_fail:
            self._attach_tree_on_fail()

        for application in self.applications:
            application.kill_application()

        self._attach_screenshot_to_report(context)

        self._attach_journal_to_report(context)

        self._attach_coredump_log_to_report(context)

        self._attach_video_to_report(context)

        self._attach_abrt_link_to_report(context)

        self._attach_version_status_to_report(context)

        self._process_after_scenario_hooks(context)

        self._process_embeds(context)

        self._attach_qecore_debug_log(context)

        if self.html_report_links:
            self._html_report_links(context)

        self._new_log_indicator = False

        self._log_end_of_automation_suite_handling_to_journal()

    def print_rich_traceback(self, step: Step):
        """
        Print an exception traceback from a failed step using https://pypi.org/project/rich/

        Inspiration from https://github.com/behave/behave/issues/996#issuecomment-1036359580
        Modified so that we can use it from after_scenario and to have detection of the module.
        """

        LOGGING.debug(get_func_params_and_values())

        try:
            from rich.console import Console
            from rich.traceback import Traceback

            LOGGING.info("Using 'rich' traceback print.")

        except ImportError:
            LOGGING.info("Module 'rich' not found, either unavailable or not installed.")
            LOGGING.info("You can install it by 'python3 -m pip install rich'.")
            return

        if not (
            getattr(step, "exception", False) and getattr(step, "exc_traceback", False)
        ):
            return

        rich_traceback = Traceback.from_exception(
            type(step.exception),
            step.exception,
            step.exc_traceback,
            show_locals=True,
            suppress=[behave],
        )

        # Forcing terminal on the console, because behave captures output.
        console = Console(force_terminal=True)
        console.print(rich_traceback)

    def _after_all(self, context) -> None:  # pylint: disable=unused-argument

        """
        This is executed as behave after_all hook,
        if context is proved in :func:`__init__`.

        :param context: Holds contextual information during the running of tests.
        :type context: <behave.runner.Context>

        .. note::
            Do **NOT** call this, if you provided context to :func:`__init__`.
        """

        LOGGING.debug(get_func_params_and_values())

        self._scenario_skip_check_cb(do_assert=True)

    def _scenario_skip_check_cb(self, do_assert=False) -> None:
        """
        Callback function. Checks if any scenario was executed.

        .. note::

            Do **NOT** call this by yourself. This method is called when test ends.
        """

        LOGGING.debug(get_func_params_and_values())

        if do_assert:
            assert not self._scenario_skipped, "No scenario matched tags"
        else:
            if self._scenario_skipped:
                print("No scenario matched tags, exiting with error code 1.")
                # sys.exit, raise, assert do not work in an atexit hook.
                os._exit(1)  # pylint: disable=protected-access

    def _set_up_scenario_skip_check(self) -> None:
        """
        Remember in sandbox if any scenario (:func:`before_scenario`) was executed.

        If context provided, set after_all behave hook, otherwise set atexit hook.

        .. note::

            Do **NOT** call this by yourself. This method is called at :func:`__init__`.
        """

        LOGGING.debug(get_func_params_and_values())

        self._scenario_skipped = True

        if self.context is not None:
            LOGGING.debug("context is set, setting after_all behave hook")

            def get_hook(old_hook):
                def hook_runner(*args, **kwargs) -> None:
                    if old_hook is not None:
                        LOGGING.debug("execute environment after_all HOOK")
                        old_hook(*args, **kwargs)
                    else:
                        LOGGING.debug("after_all not defined in environment")
                    LOGGING.debug("execute QECore after_all HOOK")
                    self._after_all(*args, **kwargs)

                return hook_runner

            hooks = self.context._runner.hooks  # pylint: disable=protected-access
            hooks["after_all"] = get_hook(hooks.get("after_all", None))
            self.context._runner.hooks = hooks  # pylint: disable=protected-access
        else:
            LOGGING.debug("context is None, setting atexit hook")
            atexit.register(self._scenario_skip_check_cb)

    def _before_feature(self, context, feature) -> None:
        """
        This is executed as behave before_feature hook,
        if context is proved in :func:`__init__`.

        :param context: Holds contextual information during the running of tests.
        :type context: <behave.runner.Context>

        .. note::
            Do **NOT** call this, if you provided context to :func:`__init__`.
        """

        LOGGING.debug(get_func_params_and_values())

        # Checking what tags are used with behave on cmd line.
        behave_tags = context.config.tags
        LOGGING.debug(f"Using context.config.tags: '{behave_tags}'")

        cmdline_tags = set(behave_tags[0].split(",")) if behave_tags else set()

        # Save message and fill it later. Its too long so have it on separate line.
        debug_message = "Enabling {} option for '{}' with number of tries {}"

        from qecore.utility import patch_scenario

        # The auto retry option has to be set for features - therefore 'before_feature'.
        # If it is set for scenarios in before_scenario it is already too late.
        # And it cannot be done in before_all since behave did not load it yet.
        for scenario in feature.scenarios:
            # Now we check all scenarios in the feature.
            # And only care about scenario started by us and not all scenarios.
            if any([tag for tag in cmdline_tags if tag in scenario.effective_tags]):
                # Check if the user attempted to use AUTORETRY with invalid value.
                if self._autoretry and not self._autoretry.isdigit():
                    LOGGING.info(f"Using invalid value AUTORETRY='{self._autoretry}'")

                # Check if the user attempted to use STABILITY with invalid value.
                if self._stability and not self._stability.isdigit():
                    LOGGING.info(f"Using invalid value STABILITY='{self._autoretry}'")

                # Check if the user attempted to use both AUTORETRY and STABILITY.
                if self._autoretry.isdigit() and self._stability.isdigit():
                    LOGGING.info("An attempt to use both AUTORETRY and STABILITY.")

                # Check if AUTORETRY was defined.
                if self._autoretry.isdigit():
                    # Debug message.
                    debug_log = debug_message.format(
                        "Auto Retry", scenario.name, self._autoretry
                    )
                    LOGGING.info(debug_log)

                    # Patching the behave run.
                    patch_scenario(scenario, int(self._autoretry), stability=False)
                    LOGGING.info("The AUTORETRY takes priority, discarding the tags.")

                    # Continue to another tag.
                    continue

                # Check if STABILITY was defined.
                elif self._stability.isdigit():
                    # Debug message.
                    debug_log = debug_message.format(
                        "Stability", scenario.name, self._stability
                    )
                    LOGGING.info(debug_log)

                    # Patching the behave run.
                    patch_scenario(scenario, int(self._stability), stability=True)
                    LOGGING.info("The STABILITY takes priority, discarding the tags.")

                    # Continue to another tag.
                    continue

                # AUTORETRY nor STABILITY was defined.
                LOGGING.debug("No environmental variable used, continuing to tags.")

                # Get the actual @autoretry=X or @stability=Y tag to parse.
                first_match = next(
                    (
                        tag
                        for tag in scenario.effective_tags
                        if "autoretry=" in tag or "stability=" in tag
                    ),
                    None,
                )

                # Autoretry or stability tag was found.
                # And it had a specific number defined.
                if first_match:
                    # Split the first match to see how many attempts user wants.
                    _, number_of_tries = first_match.split("=")
                    # Save the max attempts as integer.
                    max_attempts = int(number_of_tries)

                    # Get stability as a bool value.
                    stability = "stability" in first_match

                    logic = "Stability" if stability else "Auto retry"

                    LOGGING.debug(
                        debug_message.format(logic, scenario.name, max_attempts)
                    )
                    patch_scenario(scenario, max_attempts, stability=stability)

    def _set_up_before_feature_hook(self) -> None:
        """
        Setting up before_feature hook for behave.
        This will make preparation in before_feature to allow auto retry feature.

        .. note::

            Do **NOT** call this by yourself. This method is called at :func:`__init__`.
        """

        LOGGING.debug(get_func_params_and_values())

        if self.context is not None:
            LOGGING.debug("context is set, setting before_feature auto retry hook")

            def get_hook(old_hook):
                def hook_runner(*args, **kwargs) -> None:
                    if old_hook is not None:
                        LOGGING.debug("execute environment before_feature HOOK")
                        old_hook(*args, **kwargs)
                    else:
                        LOGGING.debug("before_feature not defined in environment")
                    LOGGING.debug("execute QECore before_feature HOOK")
                    self._before_feature(*args, **kwargs)

                return hook_runner

            hooks = self.context._runner.hooks  # pylint: disable=protected-access
            hooks["before_feature"] = get_hook(hooks.get("before_feature", None))
            self.context._runner.hooks = hooks  # pylint: disable=protected-access
        else:
            LOGGING.debug("context is None, cannot set before_feature HOOK")

    def _graceful_exit(self, signum, frame) -> None:  # pylint: disable=unused-argument
        """
        If killed externally, run user defined hooks not to break tests that will be
        executed next.

        .. note::

            Do **NOT** call this by yourself. This method is called when killed
            externally (timeout).
        """

        LOGGING.debug(get_func_params_and_values())

        assert False, f"Timeout: received signal: '{signum}'"

    @non_critical_execution
    def _start_recording(self) -> None:
        """
        Start recording the video.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`before_scenario`.
        """

        LOGGING.debug(get_func_params_and_values())

        if not self.automatic_login:
            LOGGING.debug("No video during disabled AutomaticLogin.")
            return

        self.display_clock_seconds()
        self.set_max_video_length_to(600)

        active_script_recordings_output = RunAndLog(
            "pgrep -fla qecore_start_recording"
        ).output.strip("\n")
        LOGGING.debug("removing active recordings")
        LOGGING.debug(f"Active recording detected: '{active_script_recordings_output}'")

        command = "pgrep -f qecore_start_recording"
        leftover_recording_processes_pids_output = RunAndLog(command).output.strip("\n")
        if leftover_recording_processes_pids_output is not None:
            leftover_recording_process_pid_list = (
                leftover_recording_processes_pids_output.split("\n")
            )
            for script_pid in leftover_recording_process_pid_list:
                RunAndLog(f"sudo kill -9 {script_pid}")

        active_screen_casts = RunAndLog("pgrep -fla Screencast").output.strip("\n")
        LOGGING.debug("removing active Screencasts")
        LOGGING.debug(f"Active screencasts detected: '{active_screen_casts}'")

        leftover_screencast_processes_pids_output = RunAndLog(
            "pgrep -f Screencast"
        ).output.strip("\n")
        if leftover_screencast_processes_pids_output:
            leftover_screencast_process_pid_list = (
                leftover_screencast_processes_pids_output.split("\n")
            )
            for screen_cast_pid in leftover_screencast_process_pid_list:
                RunAndLog(f"sudo kill -9 {screen_cast_pid}")

        # RHEL-10
        if "10." in self.distribution_version:
            LOGGING.debug("Handling Screencast start on RHEL-10")

            absolute_path_to_video = os.path.expanduser("~/Videos/Screencasts")
            RunAndLog(f"sudo rm -rf {absolute_path_to_video}/Screencast*")

            keyCombo("<Ctrl><Shift><Alt><R>")
            sleep(0.2)

            self.shell.findChild(
                lambda x: x.name == "Screen" and x.roleName == "label"
            ).click()
            sleep(0.2)

            self.shell.findChild(
                lambda x: x.name == ""
                and x.text is None
                and x.roleName in ("button", "push button")
                and x.size[0] == x.size[1]
                and x.showing
            ).click()
            sleep(0.2)

        # RHEL-8/RHEL-9
        else:
            LOGGING.debug("Handling Screencast start on RHEL-8/9")

            absolute_path_to_video = os.path.expanduser("~/Videos")
            RunAndLog(f"sudo rm -rf {absolute_path_to_video}/Screencast*")

            record_video_process = Popen("qecore_start_recording", shell=True)
            self.record_video_pid = record_video_process.pid

    @non_critical_execution
    def _stop_recording(self) -> None:
        """
        Stop recording the video.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`after_scenario`.
        """

        LOGGING.debug(get_func_params_and_values())

        if not self.automatic_login:
            LOGGING.debug("No video during disabled AutomaticLogin.")
            return

        # RHEL-10
        if "10." in self.distribution_version:
            # Videos nowadays are only started with the shortcut.
            # keyCombo("<Ctrl><Shift><Alt><R>")
            LOGGING.debug("Handling Screencast stop on RHEL-10")

            # Recording label can be missing if the screencasting was not started.
            recording_label = self.shell.findChild(
                lambda x: ":" in x.name and x.showing
            )
            # If the recording label is there, click it to stop the recording.
            if recording_label:
                recording_label.click()
            # If the label is not there simply log it and continue.
            else:
                LOGGING.debug("ScreenCasting issue, label not found.")

            sleep(0.2)

        # RHEL-8/RHEL-9
        else:
            LOGGING.debug("Handling Screencast stop on RHEL-8/9")

            # Stop screencasting started by qecore.
            if self.record_video_pid is not None:
                RunAndLog(f"sudo kill -9 {self.record_video_pid} > /dev/null")

        # Giving the org.gnome.Shell.Screencast chance to end
        # on its own - before killing it.
        for timer in range(30):
            screencast_process = RunAndLog("pgrep -f Screencast").output.strip("\n")
            if screencast_process:
                sleep(0.1)
            else:
                LOGGING.debug(
                    "".join(
                        (
                            "",
                            f"Screencast process ended in '{str(timer/10)}' seconds.",
                        )
                    )
                )
                break

        # Failsafe.
        leftover_recording_processes_pids = RunAndLog(
            "pgrep -f 'qecore_start_recording|Screencast'"
        ).output.strip("\n")
        if leftover_recording_processes_pids:
            # Purely for logging purposes.
            leftover_recording_processes = RunAndLog(
                "pgrep -fla 'qecore_start_recording|Screencast'"
            ).output.strip("\n")
            LOGGING.debug(f"leftover processes: '{leftover_recording_processes}'")

            # Kill any leftover process.
            leftover_recording_processes_pid_list = (
                leftover_recording_processes_pids.split("\n")
            )
            for leftover_process_pid in leftover_recording_processes_pid_list:
                LOGGING.debug(
                    "".join(
                        (
                            "failsafe needed, ",
                            f"killing active recording '{leftover_process_pid}'",
                        )
                    )
                )
                RunAndLog(f"sudo kill -9 {leftover_process_pid}")

            sleep(1)

        self.record_video_pid = None

    def get_application(
        self,
        name,
        a11y_app_name=None,
        desktop_file_exists=True,
        desktop_file_name="",
        desktop_file_path="",
        app_process_name="",
    ) -> Application:
        """
        Return application to be used in test.

        :type name: str
        :param name: Name of the package that provides the application.

        :type a11y_app_name: str
        :param a11y_app_name: Application's name as it appears in the a11y tree.

        :type desktop_file_exists: bool
        :param desktop_file_exists: Does desktop file of the application exist?

        :type desktop_file_name: str
        :param desktop_file_name: Application's desktop file name.

        :type app_process_name: str
        :param app_process_name: Application's name as it appears in a running process.

        :return: Application class instance
        :rtype: <qecore.application.Application>
        """

        LOGGING.debug(get_func_params_and_values())

        # Inform about wrong usage in case of gnome-shell.
        if name == "gnome-shell":
            LOGGING.info("You are attempting to define gnome-shell as an application.")
            LOGGING.info("This is not required. Use 'context.sandbox.shell'")

        new_application = Application(
            name,
            a11y_app_name=a11y_app_name,
            desktop_file_exists=desktop_file_exists,
            desktop_file_name=desktop_file_name,
            desktop_file_path=desktop_file_path,
            app_process_name=app_process_name,
            session_type=self.session_type,
            session_desktop=self.session_desktop,
            kiosk=self.kiosk,
        )

        self.package_list.add(name)
        self.applications.append(new_application)
        self.default_application = (
            new_application
            if self.default_application is None
            else self.default_application
        )

        return new_application

    def get_flatpak(self, flatpak_id, **kwargs) -> Flatpak:
        """
        Return flatpak to be used in test.

        :type flatpak_id: str
        :param flatpak_id: Unique name of flatpak, mandatory format: org.flathub.app

        :return: Flatpak class instance
        :rtype: <qecore.flatpak.Flatpak>
        """

        LOGGING.debug(get_func_params_and_values())

        flatpak = Flatpak(flatpak_id=flatpak_id, **kwargs)
        self.applications.append(flatpak)
        self.default_application = self.default_application or flatpak
        return flatpak

    @non_critical_execution
    def add_package(self, package_input) -> None:
        """
        Add package for a Status embed to the html log.

        :type package_input: str or list
        :param package_input: Package string or Package list .
        """

        LOGGING.debug(get_func_params_and_values())

        if isinstance(package_input, str):
            self.package_list.add(package_input)

        elif isinstance(package_input, list):
            self.package_list = self.package_list.union(package_input)

        else:
            self.package_list.add("You did not provide a string or a list.")

    def _wait_until_shell_becomes_responsive(self) -> None:
        """
        Give some time if shell is not yet loaded fully.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`sandbox.TestSandbox.__init__`.
        """

        LOGGING.debug(get_func_params_and_values())

        if not self.automatic_login:
            return

        if self.kiosk:
            self.shell = None
            return

        # Save starting point in time.
        starting_point = time.time()

        error_message = ""
        for _ in range(30):
            # Get current point in time.
            current_point = time.time()
            # Check if more than 60 seconds passed. Fail if yes.
            if current_point - starting_point > 60:
                LOGGING.debug("Session is not usable. Exiting after 60 seconds.")
                self.faulty_session = True
                raise RuntimeError("Session is not usable. Exiting after 60 seconds.")

            try:
                from dogtail.tree import root

                # Quite a race condition in the following generator can happen.
                # We will create a list of applications from Atspi objects, but when
                # one of them is an Application that was just closed, the x.name will no
                # longer have a root to be called upon. In such case the name fetch will
                # crash the run as if the entire accessibility was gone, which is not
                # true in this case.
                try:
                    applications_list = [x.name for x in root.applications()]

                except RuntimeError as error:
                    LOGGING.debug(f"Error caught: '{error}', retry in 1 second.")
                    sleep(1)
                    applications_list = [x.name for x in root.applications()]

                if "gnome-shell" not in applications_list:
                    LOGGING.debug("gnome-shell not detected in a11y root yet.")
                    sleep(1)

                else:
                    self.shell = root.application("gnome-shell")

                    # Once we have shell set the in applications also.
                    for application in self.applications:
                        application.shell = self.shell

                    return

            except RuntimeError as error:
                LOGGING.debug("Session is not usable. Exiting.")
                self.faulty_session = True
                raise RuntimeError("Most likely broken a11y, exiting.") from error

            except Exception as error:
                error_message = error
                LOGGING.debug(f"Session is not usable yet: '{error}'.")

        # This should never be reached.
        raise RuntimeError(
            f"This point should not be reached. Unable to continue: '{error_message}'"
        )

    def _retrieve_session_data(self) -> None:
        """
        Get session/system data.

        .. note::

            Do **NOT** call this by yourself. This method is called by :func:`__init__`.
        """

        LOGGING.debug(get_func_params_and_values())

        self.architecture = RunAndLog("uname -m").output.strip("\n")
        LOGGING.debug(f"architecture detected: '{self.architecture}'")

        # Distributions expected for now:
        # self.distribution = ["Red Hat Enterprise Linux", "Fedora"]
        distribution_run = RunAndLog("cat /etc/os-release | grep ^NAME=")
        self.distribution = (
            distribution_run.output.split("=")[-1].strip("\n").strip('"')
        )
        LOGGING.debug(f"distribution detected: '{self.distribution}'")

        # Distribution version.
        distribution_version_run = RunAndLog("cat /etc/os-release | grep ^VERSION_ID=")
        self.distribution_version = (
            distribution_version_run.output.split("=")[-1].strip("\n").strip('"')
        )
        LOGGING.debug(f"distribution_version detected: '{self.distribution_version}'")

        self.session_display = RunAndLog("echo $DISPLAY").output.strip("\n")
        if not self.session_display:
            LOGGING.debug(
                "".join(
                    (
                        "session display is not set - retrieve from ",
                        "qecore_get_active_display",
                    )
                )
            )

            self.session_display = RunAndLog("qecore_get_active_display").output.strip("\n")
            os.environ["DISPLAY"] = self.session_display

        LOGGING.debug(f"session_display detected: '{self.session_display}'")

        try:
            import dbus

            bus = dbus.SessionBus()
            obj = bus.get_object(
                "org.gnome.Mutter.DisplayConfig", "/org/gnome/Mutter/DisplayConfig"
            )
            interface = dbus.Interface(obj, "org.gnome.Mutter.DisplayConfig")
            call_method = interface.get_dbus_method("GetCurrentState")
            method_call_output = call_method()

            # Unwrapping the values to deal with usual types and not dbus types.
            def unwrap(value):
                if isinstance(value, dbus.ByteArray):
                    return "".join([str(x) for x in value])
                if isinstance(value, (dbus.Array, list, tuple, dbus.Struct)):
                    return [unwrap(x) for x in value]
                if isinstance(value, (dbus.Dictionary, dict)):
                    return dict([(unwrap(x), unwrap(y)) for x, y in value.items()])
                if isinstance(value, (dbus.Signature, dbus.String)):
                    return str(value)
                if isinstance(value, dbus.Boolean):
                    return bool(value)
                if isinstance(
                    value,
                    (
                        dbus.Int16,
                        dbus.UInt16,
                        dbus.Int32,
                        dbus.UInt32,
                        dbus.Int64,
                        dbus.UInt64,
                    ),
                ):
                    return int(value)
                if isinstance(value, (dbus.Double)):
                    return float(value)
                if isinstance(value, dbus.Byte):
                    return bytes([int(value)])
                return value

            # Recursive helper function to walk the data structure.
            # Data structure is searched for current resolution.
            def search_dbus_structure(dbus_object, previous_object=None):

                # Check if the structure is dictionary.
                if isinstance(dbus_object, dict):
                    for key, value in dbus_object.items():
                        # Check for the wanted condition of a dictionary.
                        # We need current display.
                        if key == "is-current" and value is True:
                            # If current object value is True
                            # return previous object's values.
                            return previous_object[1], previous_object[2]

                        # Check the result from the recursive function.
                        result_found = search_dbus_structure(value, dbus_object)
                        # End if there was result present. Return the value.
                        if result_found:
                            return result_found

                # Check if the structure is iterable but not a string.
                elif hasattr(dbus_object, "__iter__") and not isinstance(
                    dbus_object, str
                ):
                    # Check all the items present in the object.
                    for item in dbus_object:
                        # Check the result from the recursive function.
                        result_found = search_dbus_structure(item, dbus_object)
                        # End if there was result present. Return the value.
                        if result_found:
                            return result_found

            self.resolution = search_dbus_structure(unwrap(method_call_output))
            self.resolution_x = int(self.resolution[0])
            self.resolution_y = int(self.resolution[1])

            LOGGING.debug(f"resolution: '{self.resolution}'")
            LOGGING.debug(f"resolution_x: '{self.resolution_x}'")
            LOGGING.debug(f"resolution_y: '{self.resolution_y}'")

        except Exception as error:
            self.resolution = f"The resolution retrieval failed for: {error}"
            LOGGING.debug(f"resolution error: '{self.resolution}'")

        self.session_desktop = RunAndLog("echo $XDG_SESSION_DESKTOP").output.strip("\n")
        LOGGING.debug(f"session_desktop detected: '{self.session_desktop}'")

        self.session_type = "x11"
        if (
            "XDG_SESSION_TYPE" in os.environ
            and "wayland" in os.environ["XDG_SESSION_TYPE"]
        ):
            self.session_type = "wayland"
        LOGGING.debug(f"session_type detected: '{self.session_type}'")

    def _set_up_embedding(self, context) -> None:
        """
        Set up embedding to the behave html formatter.

        :param context: Holds contextual information during the running of tests.
        :type context: <behave.runner.Context>

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`before_scenario`.
        """

        LOGGING.debug(get_func_params_and_values())

        def embed_data(
            mime_type, data, caption, html_el=None, fail_only=False, separate=None
        ) -> None:
            LOGGING.debug(get_func_params_and_values())

            if context.html_formatter is None:
                LOGGING.debug("skipping embed as no html formatter detected")
                return

            formatter = context.html_formatter

            if separate is None:
                separate = self.embed_separate

            # If data is empty we want to finish html tag by at least one character
            non_empty_data = " " if not data else data

            if html_el is None:
                html_el = formatter.actual["act_step_embed_span"]

            if mime_type == "call" or fail_only:
                context._to_embed.append(  # pylint: disable=protected-access
                    {
                        "html_el": html_el,
                        "mime_type": mime_type,
                        "data": non_empty_data,
                        "caption": caption,
                        "fail_only": fail_only,
                        "separate": separate,
                    }
                )
            else:
                formatter._doEmbed(  # pylint: disable=protected-access
                    html_el, mime_type, non_empty_data, caption
                )
                if separate:
                    ET.SubElement(html_el, "br")

        def set_title(title, append=False, tag="span", **kwargs) -> None:
            for (
                formatter
            ) in context._runner.formatters:  # pylint: disable=protected-access
                if (
                    formatter.name == "html"
                    and getattr(formatter, "set_title", None) is not None
                ):
                    formatter.set_title(title=title, append=append, tag=tag, **kwargs)

                elif (
                    formatter.name == "html-pretty"
                    and getattr(formatter, "set_title", None) is not None
                ):
                    formatter.set_title(title=title)

        # Set up a variable that we can check against if there is a formatter in use.
        context.html_formatter = None

        # Main reason for this is backwards compatibility.
        # There always used to be context.embed defined and was ignored if called.
        # We define the same to not break the legacy usage while checking
        # html_formatter to save time.
        def _dummy_embed(*args, **kwargs) -> None:  # pylint: disable=unused-argument
            pass

        context.embed = _dummy_embed

        for formatter in context._runner.formatters:  # pylint: disable=protected-access
            # Formatter setup for html.
            if formatter.name == "html":
                formatter.embedding = embed_data
                context.html_formatter = formatter
                context.embed = embed_data
                break

            # Formatter setup for html-pretty.
            if formatter.name == "html-pretty":
                context.html_formatter = formatter
                context.embed = formatter.embed
                break

        context._to_embed = []  # pylint: disable=protected-access
        context.set_title = set_title

    def add_after_scenario_hook(self, callback, *args, **kwargs) -> None:
        """
        Creates hook from callback function and its arguments.
        Hook will be called during :func:`sandbox.after_scenario`.

        :type callback: <function>
        :param callback: function to be called

        .. note::
            Hooks are called in :func:`sandbox.after_scenario` in the order they were
            added. To reverse the order of execution set
            `sandbox.reverse_after_scenario_hooks` (default `False`).

        **Examples**::

            # already defined function
            def something():
                ...

            sandbox.add_after_scenario_hook(something)

            # generic function call
            sandbox.add_after_scenario_hook(function_name, arg1, arg2, kwarg1=val1, ...)

            # call command
            sandbox.add_after_scenario_hook(
                subprocess.call,
                "command to be called",
                shell=True
            )

            # embed data - if you want them embedded in the last step
            sandbox.add_after_scenario_hook(
                context.embed,
                "text/plain",
                data,
                caption="DATA"
            )

            # embed data computed later (read log file)
            sandbox.add_after_scenario_hook(lambda context:
                context.embed(
                    "text/plain",
                    open(log_file).read(),
                    caption="LOG"
                ),
                context
            )
        """

        LOGGING.debug(get_func_params_and_values())

        self._after_scenario_hooks += [(callback, args, kwargs)]

    def _set_timeout_handling(self) -> None:
        """
        Set up signal handling.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`before_scenario`.
        """

        LOGGING.debug(get_func_params_and_values())

        signal.signal(signal.SIGTERM, self._graceful_exit)
        RunAndLog("touch /tmp/qecore_timeout_handler")

    def _set_welcome_tour(self) -> None:
        """
        Disable gnome-welcome-tour via gsettings command if allowed.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`before_scenario`.
        """

        LOGGING.debug(get_func_params_and_values())

        if self.disable_welcome_tour:
            RunAndLog(
                " ".join(
                    (
                        "gsettings",
                        "set",
                        "org.gnome.shell",
                        "welcome-dialog-last-shown-version",
                        "100.0",  # larger number than the current 40+-
                    )
                )
            )

    def _set_animations(self) -> None:
        """
        Set animations via gsettings command.
        Default value is None so the settings is not set.
        Unless user specifies otherwise.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`before_scenario`.
        """

        LOGGING.debug(get_func_params_and_values())

        if self.enable_animations is not None:
            RunAndLog(
                " ".join(
                    (
                        "gsettings",
                        "set",
                        "org.gnome.desktop.interface",
                        "enable-animations",
                        "true" if self.enable_animations else "false",
                    )
                )
            )

    @non_critical_execution
    def _set_journal_log_start_time(self) -> None:
        """
        Save time.
        Will be used to retrieve logs from journal.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`before_scenario`.
        """

        LOGGING.debug(get_func_params_and_values())

        initial_cursor_output = RunAndLog(
            "sudo journalctl --lines=0 --show-cursor"
        ).output.strip()
        cursor_target = initial_cursor_output.split("cursor: ", 1)[-1]
        self.logging_cursor = f'"--after-cursor={cursor_target}"'

    @non_critical_execution
    def _set_coredump_log_start_time(self) -> None:
        """
        Save time.
        Will be used to retrieve coredumpctl list.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`before_scenario`.
        """

        LOGGING.debug(get_func_params_and_values())

        self.test_execution_start = RunAndLog("date +%s").output.strip("\n")

    def _close_yelp(self) -> None:
        """
        Close yelp application that is opened after fresh system installation.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`before_scenario`.
        """

        LOGGING.debug(get_func_params_and_values())

        # switch to allow not closing yelp in before_scenario.
        # Corner case was found in which we test yelp and don't close between scenarios.
        if not self.enable_close_yelp:
            return

        help_process_id = RunAndLog("pgrep yelp").output.strip("\n")
        if help_process_id.isdigit():
            RunAndLog(f"kill -9 {help_process_id}")

    def _close_initial_setup(self) -> None:
        """
        Close initial setup window that is opened after the first login to the system.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`before_scenario`.
        """

        LOGGING.debug(get_func_params_and_values())

        RunAndLog("echo yes > ~/.config/gnome-initial-setup-done")

    def set_blank_screen_to_never(self) -> None:
        """
        Set blank screen to never.
        For longer tests it is undesirable for screen to lock.

        .. note::

            This method is called by :func:`before_scenario`.
            There was never need to have other options,
            we do not want the system to sleep during the test.
        """

        LOGGING.debug(get_func_params_and_values())

        RunAndLog("gsettings set org.gnome.desktop.session idle-delay 0")

    @non_critical_execution
    def set_max_video_length_to(self, number=600) -> None:
        """
        Set maximum allowed video length. With default value for 10 minutes.

        :type number: int
        :param number: Maximum video length.

        .. note::

            This method is called by :func:`before_scenario`.
            You can overwrite the setting.
        """

        LOGGING.debug(get_func_params_and_values())

        RunAndLog(
            " ".join(
                (
                    "gsettings set",
                    "org.gnome.settings-daemon.plugins.media-keys",
                    f"max-screencast-length {number}",
                )
            )
        )

    @non_critical_execution
    def display_clock_seconds(self) -> None:
        """
        Display clock seconds for better tracking test in video.

        .. note::

            This method is called by :func:`before_scenario`.
            There was never need to have other options,
            as we want to see the seconds ticking during the test.
        """

        LOGGING.debug(get_func_params_and_values())

        RunAndLog("gsettings set org.gnome.desktop.interface clock-show-seconds true")

    def _return_to_home_workspace(self) -> None:
        """
        Return to home workspace.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`before_scenario`.
        """

        LOGGING.debug(get_func_params_and_values())

        if not self.workspace_return:
            return

        keyCombo("<Super><Home>")

    def disable_debug_logs_from_dogtail(self) -> None:
        """
        Disable logs from dogtail, they are useless.

        :type number: int
        :param number: Time in between accepted key strokes.

        .. note::

            This method is called by :func:`before_scenario`.
            You can overwrite the setting.
        """

        LOGGING.debug(get_func_params_and_values())

        try:
            config.logDebugToFile = False
            config.logDebugToStdOut = False
        except AttributeError:
            LOGGING.debug("Deprecated when used with dogtail-2.0.")

    def set_typing_delay(self, number) -> None:
        """
        Set typing delay so slower machines will not lose characters on type.

        :type number: int
        :param number: Time in between accepted key strokes.

        .. note::

            This method is called by :func:`before_scenario`.
            You can overwrite the setting.
        """

        LOGGING.debug(get_func_params_and_values())

        config.typingDelay = number

    def do_not_let_dogtail_abort_on_bugged_a11y(self) -> None:
        """
        Do not let dogtail abort when we can fix the issue while running.

        .. note::

            This method is called by :func:`before_scenario`.
            You can overwrite the setting.
        """

        LOGGING.debug(get_func_params_and_values())

        config.checkForA11y = False

    def set_debug_to_stdout_as(self, true_or_false=False) -> None:
        """
        Set debugging to stdout.

        :type true_or_false: bool
        :param true_or_false: Decision if debug to stdout or not.

        .. note::

            This method is called by :func:`before_scenario`.
            You can overwrite the setting.
        """

        LOGGING.debug(get_func_params_and_values())

        try:
            config.logDebugToStdOut = true_or_false
        except AttributeError:
            LOGGING.debug("Deprecated when used with dogtail-2.0.")

    def _copy_data_folder(self) -> None:
        """
        Copy data/ directory content to the /tmp/ directory.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`before_scenario`.
        """

        LOGGING.debug(get_func_params_and_values())

        if os.path.isdir("data/"):
            RunAndLog("rsync -r data/ /tmp/")

    def _detect_keyring(self) -> None:
        """
        Detect if keyring was setup. If not, setup the keyring with empty password.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`before_scenario`.
        """

        LOGGING.debug(get_func_params_and_values())

        if not self.set_keyring:
            return

        if self.kiosk:
            return

        current_user = os.path.expanduser("~")

        is_keyring_set = os.path.isfile("/tmp/keyring_set")
        LOGGING.debug(f"keyring set by qecore: '{is_keyring_set}'")

        is_keyring_in_place = os.path.isfile(
            f"{current_user}/.local/share/keyrings/default"
        )
        LOGGING.debug(f"default keyring exists: '{is_keyring_in_place}'")

        if not is_keyring_set or not is_keyring_in_place or self._no_cache:
            LOGGING.debug(
                f"removing all keyrings from '{current_user}/.local/share/keyrings/'."
            )
            RunAndLog(f"sudo rm -rf {current_user}/.local/share/keyrings/*")

            # This should always succeed.
            # If not, do not fail here, let behave handle it and generate html log.
            try:
                LOGGING.debug("creating keyring process.")

                create_keyring_process = Popen("qecore_create_keyring", shell=True)
                self.keyring_process_pid = create_keyring_process.pid
                sleep(1)

                LOGGING.debug("confirming empty password for keyring in session.")
                self.shell.child("Continue").click()
                sleep(0.2)

                LOGGING.debug("confirming to store password unencrypted in session.")
                self.shell.child("Continue").click()
                sleep(0.2)
            except Exception as error:
                print(f"error with keyring creation/confirmation: '{error}'")
                traceback.print_exc(file=sys.stdout)

                LOGGING.debug("failed to create, end the session prompt.")
                create_keyring_process.kill()

            RunAndLog("touch /tmp/keyring_set")

    @non_critical_execution
    def _capture_image(self, do_checks=True) -> None:
        """
        Capture screenshot after failed step.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`after_scenario`.
        """

        if not self.automatic_login:
            return

        # Always check, until specified otherwise.
        if do_checks:

            if not self.production:
                return

            if not (self.attach_screenshot or self._embed_all):
                return

            if not (
                self.attach_screenshot_on_pass or self.failed_test or self._embed_all
            ):
                return

        else:
            LOGGING.info("Skipping Screenshot Capture handling checks.")

        LOGGING.debug(get_func_params_and_values())

        # Making screenshots makes sense only when disable-save-to-disk is set to 'false'.
        disable_save_to_disk_run = RunAndLog(
            "gsettings get org.gnome.desktop.lockdown disable-save-to-disk"
        )

        if "true" in disable_save_to_disk_run.output:
            LOGGING.info("Setting disable-save-to-disk to 'false' via gsettings.")
            RunAndLog(
                "gsettings set org.gnome.desktop.lockdown disable-save-to-disk false"
            )

        # Check if GNOME Screenshot still exists on the system.
        self.which_gnome_screenshot_run = RunAndLog("which gnome-screenshot")

        # GNOME Screenshot exists.
        if self.which_gnome_screenshot_run.return_code == 0:
            self.capture_screenshot_run = RunAndLog(
                f"gnome-screenshot -f {self.capture_screenshot_temp_file}"
            )

        # Special case, have to check few scenarios.
        else:
            self.capture_screenshot_portal_run = RunAndLog(
                "qecore_capture_screenshot", timeout=5
            )

        # If Screenshot via portal fails, lets try to use dbus directly.
        if (
            self.capture_screenshot_portal_run.return_code != 0
            or self.capture_screenshot_portal_run.output == "\n"
        ):
            # Try to capture screenshot with DBus.
            try:
                LOGGING.debug("Capturing Screenshot via DBus.")
                from dasbus.connection import SessionMessageBus

                os.environ["DBUS_SESSION_BUS_ADDRESS"] = "unix:path=/run/user/1000/bus"
                bus = SessionMessageBus()
                proxy = bus.get_proxy(
                    "org.gnome.Shell.Screenshot", "/org/gnome/Shell/Screenshot"
                )
                self.capture_screenshot_dbus = proxy.Screenshot(
                    True, False, self.capture_screenshot_temp_file
                )

            # Upon error, lets set the result to fail and save the error.
            except Exception as error:
                LOGGING.debug(f"Capturing Screenshot via DBus failed with error: '{error}'.")
                self.capture_screenshot_dbus = (False, error)

    @non_critical_execution
    def capture_window_screenshot(self, file_name="/tmp/window_screenshot.png") -> None:
        """
        Capture screenshot of a window.
        Provided the user is using --unsafe-mode.
        """

        LOGGING.debug(get_func_params_and_values())

        # Check if GNOME Screenshot still exists on the system.
        _gnome_screenshot_exists = RunAndLog("which gnome-screenshot").return_code == 0

        _screenshot_capture_run = None
        _screenshot_portal_capture_run = None

        # GNOME Screenshot exists.
        if _gnome_screenshot_exists:
            _screenshot_capture_run = RunAndLog(f"gnome-screenshot -w -f {file_name}")
            sleep(0.1)

            # The GNOME Screenshot exists but the execution failed.
            if _screenshot_capture_run.return_code != 0:
                LOGGING.debug("Screenshot window capture failed.")
            # The GNOME Screenshot exists and the execution was a success.
            else:
                LOGGING.debug(f"Screenshot window capture was a success - '{file_name}'")

        # GNOME Screenshot does not exist, lets use script.
        else:
            _screenshot_portal_capture_run = RunAndLog(
                f"qecore_capture_window_screenshot {file_name}", timeout=5
            )

            # Script was used but the execution failed.
            if _screenshot_portal_capture_run.return_code != 0:
                LOGGING.debug("Screenshot window capture via gdbus failed.")

            # Script was used and the execution was a success - lets parse the result.
            else:

                result = "false"
                file_location = ""

                try:
                    _script_output = _screenshot_portal_capture_run.output
                    result, file_location = (
                        _script_output[1:-1].replace(" ", "").split(",")
                    )

                    # Execution was a success.
                    if "true" in result:
                        LOGGING.info(f"Image location: '{file_location}'")

                    # Execution failed, give reason as to why.
                    else:
                        LOGGING.info(f"Window image capture failed: '{_script_output}'")
                        LOGGING.info("Keep in mind that --unsafe-mode has to be used.")

                except Exception as error:
                    LOGGING.info(f"Window image capture failed on exception: '{error}'")

        return file_location

    @non_critical_execution
    def _check_for_coredump_fetching(self) -> None:
        """
        Set attach_coredump variable if set in Jenkins - tested via file existence.

        .. note::

            Do **NOT** call this by yourself. This method is called by :func:`__init__`.
        """

        LOGGING.debug(get_func_params_and_values())

        self.attach_coredump_file_check = os.path.exists("/tmp/qecore_coredump_fetch")

    @non_critical_execution
    def _set_g_debug_environment_variable(self) -> None:
        """
        Setup environment variable G_DEBUG as 'fatal-criticals'.

        .. note::

            Do **NOT** call this by yourself. This method is called by :func:`__init__`.
        """

        LOGGING.debug(get_func_params_and_values())

        # Environment value set upon checked field in Jenkins.
        if os.path.isfile("/tmp/headless_enable_fatal_critical"):
            LOGGING.debug("set G_DEBUG=fatal-criticals.")
            os.environ["G_DEBUG"] = "fatal-criticals"

        # Fatal_warnings has bigger priority than criticals.
        # Should both options be set in Jenkins the warning will overwrite the variable.
        if os.path.isfile("/tmp/headless_enable_fatal_warnings"):
            LOGGING.debug("set G_DEBUG=fatal-warnings.")
            os.environ["G_DEBUG"] = "fatal-warnings"

    @non_critical_execution
    def _set_title(self, context) -> None:
        """
        Append component name and session type to HTML title.

        :param context: Holds contextual information during the running of tests.
        :type context: <behave.runner.Context>

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`before_scenario`.
            Use :func:`context.set_title` to set HTML title.
        """

        LOGGING.debug(get_func_params_and_values())

        formatter_instance = getattr(context, "html_formatter", None)
        if formatter_instance is None:
            return

        if formatter_instance.name == "html":
            context.set_title("", tag="br", append=True)

            if self.default_application_icon_to_title:
                icon = self.get_default_application_icon()
                if icon is not None:
                    context.set_title(
                        "",
                        append=True,
                        tag="img",
                        alt=self.session_type[1],
                        src=icon.to_src(),
                        style="height:1.8rem; vertical-align:text-bottom;",
                    )

                context.set_title(f"{self.component} - ", append=True, tag="small")

            if self.session_icon_to_title:
                context.set_title(
                    "",
                    append=True,
                    tag="img",
                    alt=self.session_type[1],
                    src=qecore_icons[self.session_type].to_src(),
                    style="height:1.8rem; vertical-align:text-bottom;",
                )

                context.set_title(
                    self.session_type[1:],
                    append=True,
                    tag="small",
                    style="margin-left:-0.4em;",
                )

            self.change_title = False

        elif formatter_instance.name == "html-pretty":
            formatter_instance.set_icon(icon=qecore_icons[self.session_type].to_src())

    @non_critical_execution
    def get_default_application_icon(self) -> Union[QECoreIcon, None]:
        """
        Get icon for default application.

        :return: icon or None
        :rtype: <icons.QECoreIcon>
        """

        LOGGING.debug(get_func_params_and_values())

        # Importing here because of sphinx documentation generating issues.
        import gi  # pylint: disable=import-outside-toplevel

        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk  # pylint: disable=import-outside-toplevel

        if self.default_application and self.default_application.icon:
            icon_theme = Gtk.IconTheme.get_default()
            icon = icon_theme.lookup_icon(self.default_application.icon, 48, 0)
            if icon:
                icon_path = icon.get_filename()
                if icon_path:
                    mime = MimeTypes()
                    mime_type = mime.guess_type(icon_path)[0]
                    data_base64 = base64.b64encode(open(icon_path, "rb").read())
                    data_encoded = data_base64.decode("utf-8").replace("\n", "")
                    return QECoreIcon(mime_type, "base64", data_encoded)
        return None

    @non_critical_execution
    def attach_text_to_report(self, data, caption="Default Caption") -> None:
        """
        Attach string data to the html report.

        :type data: str
        :param data: string to be embedded to the html file. Or <file_path> to the data.

        :type caption: str
        :param caption: Caption that is to be displayed in test html report.

        .. note::

            Usage of this requires context to be initiated in TestSandbox which you can
            do in you in 'environment.py' file as follows:

            context.sandbox = TestSandbox("<component>", context=context)
        """

        LOGGING.debug(get_func_params_and_values())

        file_path = None
        validated_data = data
        # Do not try to check filename for long data.
        # Leads to OSError on some filesystems.
        filename_len_limit = 256

        if isinstance(data, Path):
            file_path = data

        if isinstance(data, str) and (len(data) < filename_len_limit):
            try:
                file_path = Path(str(data))
                if not file_path.is_file():
                    file_path = None
            except OSError:
                file_path = None

        if file_path:
            try:
                with file_path.open("r", encoding="utf-8") as _file:
                    validated_data = _file.read()

            except ValueError as error:
                validated_data = f"data removed: ValueError: '{error}'"

            except FileNotFoundError as error:
                validated_data = f"data removed: FileNotFoundError: '{error}'"

        # Validate context.
        if self.context is None:
            LOGGING.info("You did not provide 'context' in TestSandbox __init__.")
            return

        # Validate data.
        if not isinstance(validated_data, str):
            LOGGING.info("Data required of type 'str'.")
            LOGGING.info(f"You provided '{type(validated_data)}'.")
            return

        # Validate caption.
        if not isinstance(caption, str):
            LOGGING.info("Caption required of type 'str'.")
            LOGGING.info(f"You provided '{type(caption)}'.")
            return

        # Execute the embed, attaching desired text to the html report.
        self.context.embed(mime_type="text/plain", data=validated_data, caption=caption)

    @non_critical_execution
    def _attach_tree_on_fail(self) -> None:
        """
        Attach tree structure representation of an application upon failed test.

        :param context: Holds contextual information during the running of tests.
        :type context: <behave.runner.Context>
        """

        LOGGING.debug(get_func_params_and_values())

        if not self.automatic_login:
            return

        from qecore.utility import TreeRepresentationQecore

        for application in self.applications:
            application_root = None

            if application.is_running():
                application_root = application.get_root()
            else:
                continue

            tree_data = TreeRepresentationQecore(application_root, "tree", labels=True)

            embed_caption = f"Tree of '{application.component}' at the moment of fail"

            # Execute the embed, attaching desired text to the html report.
            self.context.embed(
                mime_type="text/plain", data=str(tree_data), caption=embed_caption
            )

    @non_critical_execution
    def _attach_screenshot_to_report(self, context, do_checks=True) -> None:
        """
        Attach screenshot to the html report upon failed test.

        :param context: Holds contextual information during the running of tests.
        :type context: <behave.runner.Context>

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`after_scenario`.
        """

        LOGGING.debug(get_func_params_and_values())

        # Always check, until specified otherwise.
        if do_checks:

            # Running this function makes sense only when formatter is defined.
            if context.html_formatter is None:
                LOGGING.debug("No formatter defined.")
                return

            if not self.production:
                LOGGING.debug(f"self.production='{str(self.production)}'.")
                return

            if not (self.attach_screenshot or self._embed_all):
                LOGGING.debug(f"self.attach_screenshot='{str(self.attach_screenshot)}'.")
                return

            if not (self.attach_screenshot_on_pass or self.failed_test or self._embed_all):
                LOGGING.debug(f"self.failed_test='{str(self.failed_test)}'.")
                return

        else:
            LOGGING.info("Skipping Attach Screenshot to Report handling checks.")

        # The GNOME Screenshot exists.
        if self.which_gnome_screenshot_run.return_code == 0:
            # The GNOME Screenshot exists but the execution failed.
            if self.capture_screenshot_run.return_code != 0:
                LOGGING.debug("Screenshot capture failed.")
                self.attach_text_to_report(
                    data=str(self.capture_screenshot_run.error),
                    caption="Screenshot Failed",
                )
            # The GNOME Screenshot exists and the execution was a success.
            else:
                LOGGING.debug("Attempting to attach screenshot to report.")
                self.attach_image_to_report(
                    context,
                    self.capture_screenshot_temp_file,
                    "GNOME Screenshot",
                    fail_only=not (self.attach_screenshot_on_pass or self._embed_all),
                )

        # The screenshot was done via Portal.
        elif self.capture_screenshot_portal_run:
            # The Portal Screenshot exists but the execution failed.
            if self.capture_screenshot_portal_run.return_code != 0:
                LOGGING.debug("Screenshot Portal capture failed.")
                self.attach_text_to_report(
                    data=str(self.capture_screenshot_portal_run.error),
                    caption="Screenshot via Portal Failed",
                )
            # The Portal Screenshot exists and the execution was a success.
            else:
                LOGGING.debug("Attempting to attach Portal Screenshot to report.")
                image_path_stripped = (
                    self.capture_screenshot_portal_run.output.lstrip("file:/").rstrip("\n")
                )
                image_path = "/" + image_path_stripped
                self.attach_image_to_report(
                    context,
                    image_path,
                    "Screenshot via Portal",
                )

        # Check if the dbus capture was successful.
        if self.capture_screenshot_dbus[0] is not None:
            if self.capture_screenshot_dbus[0] is False:
                LOGGING.debug("Screenshot via DBus capture failed.")
                self.attach_text_to_report(
                    data=str(self.capture_screenshot_dbus[1]),
                    caption="Screenshot via DBus Failed",
                )
            else:

                LOGGING.debug("Attempting to attach DBus Screenshot to report.")
                self.attach_image_to_report(
                    context,
                    self.capture_screenshot_dbus[1],
                    "Screenshot via DBus",
                )

        # All option that were tried failed.
        else:
            LOGGING.debug("All options, GNOME Screenshot, Portal and DBus have failed.")

        LOGGING.debug(f"Erasing temporary screenshot capture file {self.capture_screenshot_temp_file}.")
        RunAndLog(f"sudo rm -rf {self.capture_screenshot_temp_file}")

    @non_critical_execution
    def attach_captured_screenshot_to_report(self, caption="default") -> None:
        """
        Capture and attach screenshot to the html report.

        :type caption: str
        :param caption: Caption that is to be displayed in test html report.

        .. note::

            Usage of this requires context to be initiated in TestSandbox which you can
            do in you in 'environment.py' file as follows:

            context.sandbox = TestSandbox("<component>", context=context)
        """

        LOGGING.debug(get_func_params_and_values())

        # Validate context.
        if self.context is None:
            LOGGING.info("You did not provide 'context' in TestSandbox __init__.")
            return

        # Running this function makes sense only when formatter is defined.
        if self.context.html_formatter is None:
            LOGGING.info("No formatter was defined, nowhere to attach screenshot to.")
            return

        # Validate caption.
        if not isinstance(caption, str):
            LOGGING.info("Caption required of type 'str'.")
            LOGGING.info(f"You provided '{type(caption)}'.")
            return

        # Validate caption content. Not critical, do not end on this.
        if caption == "default":
            LOGGING.info("No caption set, you might want to consider naming the file.")
            LOGGING.info('_attach_captured_screenshot_to_report(caption="caption")')

        LOGGING.debug("Deliberate choice to capture and attach Screenshot to report.")
        # Bypass the check variable.
        self._capture_image(do_checks=False)

        # Use already defined function to embed the screenshot to the report.
        self._attach_screenshot_to_report(context=self.context, do_checks=False)

    @non_critical_execution
    def attach_image_to_report(
        self, context, image="", caption="Default Caption", fail_only=False
    ) -> None:
        """
        Attach image to the html report upon user request.

        :param context: Holds contextual information during the running of tests.
        :type context: <behave.runner.Context>

        :type image: str
        :param image: Location of the image/png file.

        :type caption: str
        :param caption: Caption that is to be displayed in test html report.

        :type fail_only: bool
        :param fail_only: attach only if scenario fails

        .. note::

            Use this to attach any image to report at any time.
        """

        # Running this function makes sense only when formatter is defined.
        if context.html_formatter is None:
            LOGGING.debug("No formatter defined.")
            return

        if not self.production:
            LOGGING.debug(f"self.production='{str(self.production)}'.")
            return

        LOGGING.debug(f"Path to the image to be embedded: '{image}'")

        LOGGING.debug(get_func_params_and_values())

        if os.path.isfile(image):
            data_base64 = base64.b64encode(open(image, "rb").read())
            data_encoded = data_base64.decode("utf-8").replace("\n", "")
            context.embed(
                mime_type="image/png",
                data=data_encoded,
                caption=caption,
                fail_only=fail_only,
            )

    @non_critical_execution
    def _attach_video_to_report(self, context) -> None:
        """
        Attach video to the html report upon failed test.

        :param context: Holds contextual information during the running of tests.
        :type context: <behave.runner.Context>

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`after_scenario`.
        """

        LOGGING.debug(get_func_params_and_values())

        # Running this function makes sense only when formatter is defined.
        if context.html_formatter is None:
            LOGGING.debug("No formatter defined.")
            return

        if not (self.production and self.record_video):
            LOGGING.debug(f"self.production='{str(self.production)}'.")
            LOGGING.debug(f"self.record_video='{str(self.record_video)}'.")
            return

        if not (self.attach_video or self._embed_all):
            LOGGING.debug(f"self.attach_video='{str(self.attach_video)}'.")
            return

        if not (self.attach_video_on_pass or self.failed_test or self._embed_all):
            LOGGING.debug(f"self.failed_test='{str(self.failed_test)}'.")
            LOGGING.debug(f"self.attach_video_on_pass='{str(self.attach_video_on_pass)}'.")
            return

        # Fedora/RHEL-10 handling.
        if os.path.isdir(os.path.expanduser("~/Videos/Screencasts")):
            absolute_path_to_video = os.path.expanduser("~/Videos/Screencasts")
        # RHEL8/9 handling.
        else:
            absolute_path_to_video = os.path.expanduser("~/Videos")

        screencast_list = [
            f"{absolute_path_to_video}/{file_name}"
            for file_name in os.listdir(absolute_path_to_video)
            if "Screencast" in file_name
        ]
        LOGGING.debug(f"screencast list '{screencast_list}'")

        video_name = f"{self.component}_{self.current_scenario}"
        absolute_path_to_new_video = f"{absolute_path_to_video}/{video_name}.webm"
        LOGGING.debug(f"absolute path to new video '{absolute_path_to_new_video}'")

        if screencast_list == []:
            LOGGING.debug("No video file found.")
            context.embed(
                mime_type="text/plain",
                data="No video file found.",
                caption="Video",
                fail_only=not (self.attach_video_on_pass or self._embed_all),
            )
        else:
            if self.wait_for_stable_video:
                self._wait_for_video_encoding(screencast_list[0])

            data_base64 = base64.b64encode(open(screencast_list[0], "rb").read())
            data_encoded = data_base64.decode("utf-8").replace("\n", "")
            context.embed(
                mime_type="video/webm",
                data=data_encoded,
                caption="Video",
                fail_only=not (self.attach_video_on_pass or self._embed_all),
            )

            LOGGING.debug("Renaming Screencast.")
            RunAndLog(f"mv '{screencast_list[0]}' {absolute_path_to_new_video}")
            sleep(0.1)

            LOGGING.debug("Erasing unsaved videos.")
            RunAndLog(f"sudo rm -rf {absolute_path_to_video}/Screencast*")

    @non_critical_execution
    def _attach_journal_to_report(self, context) -> None:
        """
        Attach journal to the html report upon failed test.

        :param context: Holds contextual information during the running of tests.
        :type context: <behave.runner.Context>

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`after_scenario`.
        """

        LOGGING.debug(get_func_params_and_values())

        # Running this function makes sense only when formatter is defined.
        if context.html_formatter is None:
            LOGGING.debug("No formatter defined.")
            return

        if not self.production:
            LOGGING.debug(f"self.production='{str(self.production)}'.")
            return

        if not (self.attach_journal or self._embed_all):
            LOGGING.debug(f"self.attach_journal='{str(self.attach_journal)}'.")
            return

        if not (self.attach_journal_on_pass or self.failed_test or self._embed_all):
            LOGGING.debug(f"self.failed_test='{str(self.failed_test)}'.")
            LOGGING.debug(
                f"self.attach_journal_on_pass='{str(self.attach_journal_on_pass)}'."
            )
            return

        journal_run = RunAndLog(
            " ".join(
                (
                    "sudo journalctl --all",
                    f"--output=short-precise {self.logging_cursor}",
                    "> /tmp/journalctl_short.log",
                )
            )
        )

        if journal_run.return_code != 0:
            LOGGING.debug("creation of journalctl log failed.")
            context.embed(
                mime_type="text/plain",
                data=f"Creation of journalctl file failed: \n{journal_run.error}\n",
                caption="journalctl",
                fail_only=not (self.attach_journal_on_pass or self._embed_all),
            )
        else:
            LOGGING.debug("creation of journalctl log succeeded.")
            journal_data = self.file_loader("/tmp/journalctl_short.log")

            context.embed(
                mime_type="text/plain",
                data=journal_data,
                caption="journalctl",
                fail_only=not (self.attach_journal_on_pass or self._embed_all),
            )

        LOGGING.debug("erase the journalctl log.")
        RunAndLog("rm /tmp/journalctl_short.log")

    @non_critical_execution
    def _attach_coredump_log_to_report(self, context) -> None:
        """
        Attach coredump log to the html report upon failed test.

        :param context: Holds contextual information during the running of tests.
        :type context: <behave.runner.Context>

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`after_scenario`.
        """

        LOGGING.debug(get_func_params_and_values())

        # Running this function makes sense only when formatter is defined.
        if context.html_formatter is None:
            LOGGING.debug("No formatter defined.")
            return

        if not self.production:
            LOGGING.debug(f"self.production='{str(self.production)}'.")
            return

        if not (
            self.attach_coredump or self.attach_coredump_file_check or self._embed_all
        ):
            LOGGING.debug(f"self.attach_coredump='{str(self.attach_coredump)}'.")
            short_coredump_check = str(self.attach_coredump_file_check)
            LOGGING.debug(f"self.attach_coredump_file_check='{short_coredump_check}'.")
            return

        if not (self.attach_coredump_on_pass or self.failed_test or self._embed_all):
            LOGGING.debug(f"self.failed_test='{str(self.failed_test)}'.")
            LOGGING.debug(
                f"self.attach_coredump_on_pass='{str(self.attach_coredump_on_pass)}'."
            )
            return

        # Get coredump list results only from duration of the test.
        coredump_list_run = RunAndLog(
            f"sudo coredumpctl list --since=@{self.test_execution_start}"
        )

        # If there are no coredumps end right here.
        if "No coredumps found." in coredump_list_run.output:
            LOGGING.debug("No coredumps found.")
            return

        coredump_log = "/tmp/qecore_coredump.log"
        debuginfo_install_log = "/tmp/qecore_debuginfo_install.log"

        # Empty the coredump file logs.
        if os.path.isfile(coredump_log):
            LOGGING.debug("emptying the coredump log.")
            RunAndLog(f">{coredump_log}")

        # Do not empty debuginfo log - the content is desired in all possible tests.
        if not os.path.isfile(debuginfo_install_log):
            LOGGING.debug("creating debuginfo log file.")
            RunAndLog(f"touch {debuginfo_install_log}")

        # Get packages to be installed from gdb.
        def get_packages_from_coredump(pid) -> Union[str, None]:
            # Get first gdb output and load it to file to parse over.
            RunAndLog(f"echo 'q' | sudo coredumpctl gdb {pid} 2&> {coredump_log}")

            # Set the base variable to return with all data.
            desired_data = ""

            # Open the file and iterate over its lines.
            with open(coredump_log, "r", encoding="utf-8") as coredump_file:
                # Loading one line at a time.
                next_line = coredump_file.readline()

                # Loop until there is no next line.
                while next_line:
                    # Parse correct lines to fetch debuginfo packages.
                    if "debug" in next_line and "install" in next_line:
                        _, target = next_line.split("install ", 1)
                        desired_data += target.strip("\n") + " "

                    # If there is no coredump file present there si nothing to fetch.
                    elif "Coredump entry has no core attached." in next_line:
                        LOGGING.debug("coredump entry has no core attached.")
                        return None

                    # Load the next line.
                    next_line = coredump_file.readline()

            return desired_data

        # Install all packages that gdb desires.
        def install_debuginfo_packages(pid) -> None:
            # We need gdb to be installed.
            if "not installed" in RunAndLog("rpm -q gdb").output:
                LOGGING.debug("installing gdb.")
                RunAndLog(f"sudo dnf install -y gdb >> {debuginfo_install_log}")

            # Iterate a few times over the gdb to get packages and install them.
            packages_installed_in_last_attempt = ""
            for _ in range(20):
                packages_to_install = get_packages_from_coredump(pid)

                # Install required packages but break if packages were already
                # attempted to be installed.
                if packages_to_install and (
                    packages_to_install != packages_installed_in_last_attempt
                ):
                    packages_installed_in_last_attempt = packages_to_install
                    RunAndLog(
                        "".join(
                            (
                                "sudo dnf debuginfo-install -y ",
                                f"{packages_to_install} >> {debuginfo_install_log}",
                            )
                        )
                    )
                else:
                    break

        # Load coredump lines as provided.
        list_of_results = coredump_list_run.output.rstrip("\n").split("\n")[1:]
        valid_coredump_counter = 0

        for coredump_line in list_of_results:
            starting_time = time.time()

            coredump_line_split = coredump_line.split(" ")
            coredump_line_filtered = [x for x in coredump_line_split if x]
            coredump_pid_to_investigate = coredump_line_filtered[4]
            coredump_executable = coredump_line_filtered[9]

            # Check if coredump file does not exist.
            if coredump_line_filtered[8] == "none":
                # Attach data to html report.
                data = " ".join(
                    (
                        f"Coredump entry '{coredump_pid_to_investigate}'",
                        "has no core attached.",
                    )
                )
                context.embed(
                    mime_type="text/plain",
                    data=data,
                    caption=f"coredump_log_{coredump_pid_to_investigate}_no_core",
                )
                continue

            # Install all debuginfos given by coredump file with found pid.
            install_debuginfo_packages(coredump_pid_to_investigate)

            # All debuginfo packages should be installed now - get the backtrace and
            # attach it to report.
            gdb_command = "thread apply all bt full"
            RunAndLog(
                "".join(
                    (
                        f"echo '{gdb_command}' | sudo coredumpctl ",
                        f"gdb {coredump_pid_to_investigate} 2&> {coredump_log}",
                    )
                )
            )

            # Calculate the total execution time of coredump fetch.
            coredump_fetch_time = time.time() - starting_time

            valid_coredump_counter += 1
            backtrace_caption = " ".join(
                (
                    f"Backtrace from coredump pid '{coredump_pid_to_investigate}'",
                    f"with executable '{coredump_executable}'",
                    f"and it took '{coredump_fetch_time:.1f}s'",
                )
            )

            context.embed(
                mime_type="text/plain",
                data=self.file_loader(coredump_log),
                caption=backtrace_caption,
            )

        if valid_coredump_counter != 0:
            context.embed(
                mime_type="text/plain",
                data=self.file_loader(debuginfo_install_log),
                caption="debug_info_install_log",
            )

    @non_critical_execution
    def _attach_abrt_link_to_report(self, context) -> None:
        """
        Attach abrt link to the html report upon detected abrt FAF report.

        :param context: Holds contextual information during the running of tests.
        :type context: <behave.runner.Context>

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`after_scenario`.
        """

        LOGGING.debug(get_func_params_and_values())

        # Running this function makes sense only when formatter is defined.
        if context.html_formatter is None:
            LOGGING.debug("No formatter defined.")
            return

        if not self.production:
            LOGGING.debug(f"self.production='{str(self.production)}'.")
            return

        if not (self.attach_faf or self._embed_all):
            LOGGING.debug(f"self.attach_faf='{str(self.attach_faf)}'.")
            return

        if not (self.attach_faf_on_pass or self.failed_test or self._embed_all):
            LOGGING.debug(f"self.failed_test='{str(self.failed_test)}'.")
            LOGGING.debug(f"self.attach_faf_on_pass='{str(self.attach_faf_on_pass)}'.")
            return

        faf_reports = set()
        faf_reports_data = []

        # There are a few known prefixes for directories.
        abrt_known_directories_identifiers = [
            "oops",
            "vmcore",
            "ccpp",
            "Python",
            "Java",
        ]

        abrt_directories_run = RunAndLog("sudo ls /var/spool/abrt/")
        LOGGING.debug(f"abrt_directories result: '{abrt_directories_run.output}'")
        LOGGING.debug(
            f"abrt_directories known prefixes: '{abrt_known_directories_identifiers}'"
        )

        if abrt_directories_run.return_code != 0:
            LOGGING.debug(
                f"abrt_directories return code was non-zero: '{abrt_directories_run.return_code}'"
            )
            return

        # List of directories is empty - there is no faf to be processed.
        if abrt_directories_run.output == "":
            LOGGING.debug(
                " abrt_directories the directory was empty: no data to be processed."
            )
            return

        # Utility function to get data from abrt files.
        def _abrt_directory_data_fetch(data_id, file_to_read) -> str:
            # Set default value to use on error.
            abrt_faf_file_data = ""

            # Log what file is getting parsed.
            # Have to check like this since the files will not load with non-root user.
            if RunAndLog(f"sudo ls {file_to_read}").return_code != 0:
                LOGGING.debug(f"no such file '{file_to_read}'")
                return abrt_faf_file_data

            LOGGING.debug(f"reading file '{file_to_read}'")

            # Cat the file to prevent IO issues.
            abrt_faf_file_run = RunAndLog(f"sudo cat '{file_to_read}'")
            if abrt_faf_file_run.return_code == 0:
                # Get the data without the end line character.
                abrt_faf_file_data = abrt_faf_file_run.output.strip("\n")
                # Log the data that will be returned.
                LOGGING.debug(f"{data_id} data removed but viewable in 'FAF reports data'.")
            else:
                LOGGING.debug(f"non-zero return code '{abrt_faf_file_run.error}'")

            # Return the data from file.
            return abrt_faf_file_data

        # Check just the directories that are unique.
        unique_reasons = set()
        unique_faf_directories_to_check = set()

        # Go over all abrt directories and get FAF links with reason.
        LOGGING.debug("parsing links")
        abrt_directories_as_list = abrt_directories_run.output.strip("\n").split("\n")
        for abrt_directory in abrt_directories_as_list:
            reason_file = f"/var/spool/abrt/{abrt_directory}/reason"
            reported_to_file = f"/var/spool/abrt/{abrt_directory}/reported_to"

            try:
                abrt_faf_reason = _abrt_directory_data_fetch("reason", reason_file)

                # If the reason is unique mark the directory to pull data from it later.
                if abrt_faf_reason and (abrt_faf_reason not in unique_reasons):
                    unique_faf_directories_to_check.add(abrt_directory)
                    # Keeping the list of unique reasons.
                    unique_reasons.add(abrt_faf_reason)

                abrt_faf_reported_to = _abrt_directory_data_fetch(
                    "reported_to", reported_to_file
                )

                # Hyperlink needs a little bit of extra parsing.
                abrt_faf_lines = abrt_faf_reported_to.split("ABRT Server: URL=")[-1]
                abrt_faf_hyperlink = abrt_faf_lines.split("\n")[0]

                # Success condition for link is a fail reason and hyperlink present.
                if abrt_faf_reason and abrt_faf_hyperlink:
                    data_to_insert = (abrt_faf_hyperlink, f"Reason: {abrt_faf_reason}")
                    faf_reports.add(data_to_insert)

            except Exception as error:  # pylint: disable=broad-except
                LOGGING.debug(f"Exception caught: {error}'")

        # Embed the links.
        LOGGING.debug("Attempting to embed FAF links.")
        if faf_reports:
            context.embed(
                "link",
                faf_reports,
                caption="FAF reports",
                fail_only=not (self.attach_faf_on_pass or self._embed_all),
            )

        # Pull all the data only from unique directories.
        LOGGING.debug(f"parsing data in {unique_faf_directories_to_check}")
        for unique_faf_directory in unique_faf_directories_to_check:
            # Main data to pull.
            cmdline_file = f"/var/spool/abrt/{unique_faf_directory}/cmdline"
            backtrace_file = f"/var/spool/abrt/{unique_faf_directory}/backtrace"
            component_file = f"/var/spool/abrt/{unique_faf_directory}/component"
            # Pull the reason and reported again to have the proper logs on fail.
            reason_file = f"/var/spool/abrt/{unique_faf_directory}/reason"
            reported_to_file = f"/var/spool/abrt/{unique_faf_directory}/reported_to"

            # Handle parts one by one to make sure any error is shown in logs.
            try:
                abrt_faf_cmdline = _abrt_directory_data_fetch("cmdline", cmdline_file)
            except Exception as error:  # pylint: disable=broad-except
                abrt_faf_cmdline = error

            try:
                abrt_faf_backtrace = _abrt_directory_data_fetch(
                    "backtrace", backtrace_file
                )
            except Exception as error:  # pylint: disable=broad-except
                abrt_faf_backtrace = error

            try:
                abrt_faf_component = _abrt_directory_data_fetch(
                    "component", component_file
                )
            except Exception as error:  # pylint: disable=broad-except
                abrt_faf_component = error

            try:
                abrt_faf_reason = _abrt_directory_data_fetch("reason", reason_file)
            except Exception as error:  # pylint: disable=broad-except
                abrt_faf_reason = error

            try:
                abrt_faf_reported_to = _abrt_directory_data_fetch(
                    "reported_to", reported_to_file
                )

                # Hyperlink needs a little bit of extra parsing.
                abrt_faf_lines = abrt_faf_reported_to.split("ABRT Server: URL=")[-1]
                abrt_faf_hyperlink = abrt_faf_lines.split("\n")[0]
            except Exception as error:  # pylint: disable=broad-except
                abrt_faf_hyperlink = error

            # Adding visual spacer only after the first entry.
            if len(faf_reports_data) == 0:
                visual_spacer = ""
            else:
                visual_spacer = "=" * 80 + "\n"

            faf_reports_data.append(
                (
                    visual_spacer,
                    f"<h4>ABRT component:</h4> {abrt_faf_component}\n",
                    f"<h4>ABRT reason:</h4> {abrt_faf_reason}\n",
                    f"<h4>ABRT reported_to:</h4> {abrt_faf_hyperlink}\n",
                    f"<h4>ABRT cmdline:</h4> {abrt_faf_cmdline}\n",
                    f"<h4>ABRT backtrace:</h4> {abrt_faf_backtrace}\n",
                )
            )

        # Embed the data
        LOGGING.debug("Attempting to embed FAF data.")

        # Formatting data to respect html tags and local string format.
        formatted_data = ""
        for data_entry in faf_reports_data:
            formatted_data += "".join(data_entry)

        if faf_reports_data:
            context.embed(
                "text/html",
                formatted_data,
                "FAF reports data",
            )

    @non_critical_execution
    def _attach_version_status_to_report(self, context) -> None:
        """
        Process status report - this will attach version of many components needed for
        correct function.

        :param context: Holds contextual information during the running of tests.
        :type context: <behave.runner.Context>

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`after_scenario`.
        """

        LOGGING.debug(get_func_params_and_values())

        # Running this function makes sense only when formatter is defined.
        if context.html_formatter is None:
            LOGGING.debug("No formatter defined.")
            return

        cached_versions_file = "/tmp/qecore_version_status.txt"

        if self.status_report and self._new_log_indicator:
            # If there is no cache to be kept, delete the file with data and create new.
            if self._no_cache:
                RunAndLog(f"sudo rm -rf {cached_versions_file}")
                # Just in case to prevent race conditions.
                sleep(0.1)

            # If the cached file exists attach it.
            if os.path.isfile(cached_versions_file):
                context.embed(
                    "text/html",
                    data=self.file_loader(cached_versions_file),
                    caption="Status",
                    fail_only=False,
                )
                return

            status_data = "<h4>Versions used in testing:</h4>"

            # Iterate over components and get package version.
            LOGGING.debug(f"Handling package list: '{self.package_list}'")

            for component in self.package_list:
                # Get a component version.
                component_rpm_run = RunAndLog(f"rpm -q '{component}'")
                status_data += "\n".join((f"  {component_rpm_run.output}",))

            # Import version from module.
            try:
                qecore_version = pkg_resources.require("qecore")[0].version
            except ImportError as error:
                qecore_version = f"__qecore_version_unavailable__: '{error}'"

            # Import version from module.
            try:
                behave_version = pkg_resources.require("behave")[0].version
            except ImportError as error:
                behave_version = f"__behave_version_unavailable__: '{error}'"

            # Import version from module.
            try:
                behave_html_pretty_formatter_version = pkg_resources.require(
                    "behave_html_pretty_formatter"
                )[0].version
            except ImportError as error:
                behave_html_pretty_formatter_version = (
                    f"__formatter_version_unavailable__: '{error}'"
                )

            # Get dogtail rpm version.
            # To be changed when dogtail 1.0 is released to pypi.
            dogtail_base = RunAndLog("rpm -q python3-dogtail").output.strip("\n")
            dogtail_scripts = RunAndLog("rpm -q python3-dogtail-scripts").output.strip("\n")

            ponytail_base = RunAndLog("rpm -q gnome-ponytail-daemon").output.strip("\n")

            # One of the following should be installed.
            ponytail_version_to_list = ""

            ponytail_python_run = RunAndLog("rpm -q gnome-ponytail-daemon-python")
            ponytail_python3_run = RunAndLog("rpm -q python3-gnome-ponytail-daemon")

            if ponytail_python_run.return_code == 0:
                ponytail_version_to_list = ponytail_python_run.output.strip("\n")

            elif ponytail_python3_run.return_code == 0:
                ponytail_version_to_list = ponytail_python3_run.output.strip("\n")

            else:
                LOGGING.debug("Missing ponytail package, this should not happen.")
                ponytail_version_to_list = " and ".join(
                    (
                        ponytail_python_run.output.strip("\n"),
                        ponytail_python3_run.output.strip("\n"),
                    )
                )

            # Only purpose of this is to have a shorter variable.
            html_pretty_short = behave_html_pretty_formatter_version

            # Make a header for modules.
            status_data += "\n<h4>Versions from modules:</h4>"

            # Join the data from modules and dogtail rpm.
            status_data += "\n".join(
                (
                    f"  qecore: '{qecore_version}'",
                    f"  behave: '{behave_version}'",
                    f"  behave_html_pretty_formatter: '{html_pretty_short}'",
                    f"  dogtail: {dogtail_base}",
                    f"  dogtail: {dogtail_scripts}",
                    f"  ponytail: {ponytail_base}",
                    f"  ponytail: {ponytail_version_to_list}",
                )
            )

            # Embed the data to the report.
            with open(cached_versions_file, "w+", encoding="utf-8") as _cache_file:
                _cache_file.write(status_data)

            context.embed("text/html", status_data, caption="Status", fail_only=False)

    def _process_after_scenario_hooks(self, context) -> None:
        """
        Process attached after_scenario_hooks.

        :param context: Holds contextual information during the running of tests.
        :type context: <behave.runner.Context>

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`after_scenario`.
        """

        LOGGING.debug(get_func_params_and_values())

        hook_errors = ""

        if self.reverse_after_scenario_hooks:
            LOGGING.debug("reversing _after_scenario_hooks")
            self._after_scenario_hooks.reverse()

        LOGGING.debug(f"processing {len(self._after_scenario_hooks)} hooks")

        for callback, args, kwargs in self._after_scenario_hooks:
            try:
                callback(*args, **kwargs)
            except Exception as error:  # pylint: disable=broad-except
                error_trace = traceback.format_exc()
                hook_errors += "\n\n" + error_trace
                context.embed(
                    "text/plain",
                    f"Hook Error: {error}\n{error_trace}",
                    caption="Hook Error",
                )

        self._after_scenario_hooks = []

        assert not hook_errors, "".join(
            f"Exceptions during after_scenario hook:{hook_errors}"
        )

    @non_critical_execution
    def _process_embeds(self, context) -> None:
        """
        Process postponed embeds (with mime_type="call" or fail_only=True).

        :param context: Holds contextual information during the running of tests.
        :type context: <behave.runner.Context>

        :type scenario: <behave.model.Scenario>
        :param scenario: Passed object.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`after_scenario`.
        """

        LOGGING.debug(get_func_params_and_values())

        scenario_fail = self.failed_test or self._embed_all

        embeds = getattr(context, "_to_embed", [])
        LOGGING.debug(f"process {len(embeds)} embeds")

        for kwargs in embeds:
            # Execute postponed "call"s.
            if kwargs["mime_type"] == "call":
                # "data" is function, "caption" is args, function returns triple.
                mime_type, data, caption = kwargs["data"](*kwargs["caption"])
                kwargs["mime_type"], kwargs["data"], kwargs["caption"] = (
                    mime_type,
                    data,
                    caption,
                )
            # skip "fail_only" when scenario passed
            if not scenario_fail and kwargs["fail_only"]:
                continue
            # Reset "fail_only" to prevent loop.
            kwargs["fail_only"] = False
            context.embed(**kwargs)
        context._to_embed = []  # pylint: disable=protected-access

    @non_critical_execution
    def _html_report_links(self, context) -> None:
        """
        Fetch a tag link to the git repository in current commit.

        :param context: Holds contextual information during the running of tests.
        :type context: <behave.runner.Context>

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`after_scenario`.
        """

        LOGGING.debug(get_func_params_and_values())

        # Running this function makes sense only when formatter is defined.
        if context.html_formatter is None:
            LOGGING.debug("No formatter defined.")
            return

        git_url = self.project_git_url
        git_commit = self.project_git_commit
        if not git_url or not git_commit:
            LOGGING.debug("The git_url or git_commit is not valid.")
            return

        project_url_base = f"{git_url}/-/tree/{git_commit}/"
        qecore_url_base = "/".join(
            ("https://gitlab.com", "dogtail/qecore/-/tree/master/qecore/")
        )
        nmci_url_base = "/".join(
            (
                "https://gitlab.freedesktop.org",
                "NetworkManager/NetworkManager-ci/-/tree/master/",
            )
        )

        # This will return an instance of PrettyHTMLFormatter.
        formatter_instance = getattr(context, "html_formatter", None)

        # If no instance was given end the handling.
        if formatter_instance is None:
            LOGGING.debug("No instance of formatter found.")
            return

        # Formatter html handling.
        if formatter_instance.name == "html":
            LOGGING.debug("Handling 'html' formatter.")

            # Search for links in scenario HTML element.
            scenario_el = getattr(formatter_instance, "scenario_el", None)
            if scenario_el is None:
                LOGGING.debug("Formatter instance has no scenario_el attribute.")
                return

            scenario_file = scenario_el.find(".//span[@class='scenario_file']")
            step_files = scenario_el.findall(".//div[@class='step_file']/span")
            tags_el = scenario_el.find(".//span[@class='tag']")

            # Link tags to scenario (.feature file).
            if tags_el is not None:
                tags = tags_el.text.split()
                tags.reverse()
                tags_el.text = ""
                scenario_name = True

                for tag in tags:
                    if tag.startswith("@rhbz"):
                        bug_id = tag.replace("@rhbz", "").rstrip(",")
                        link_el = ET.Element(
                            "a",
                            {
                                "href": "https://bugzilla.redhat.com/" + bug_id,
                                "target": "_blank",
                                "style": "color:inherit",
                            },
                        )
                        link_el.text = tag
                        tags_el.insert(0, link_el)

                    elif scenario_name:
                        scenario_name = False
                        if scenario_file is not None:
                            file_name, line = scenario_file.text.split(":", 2)
                            link_el = ET.Element(
                                "a",
                                {
                                    "href": project_url_base + file_name + "#L" + line,
                                    "target": "_blank",
                                    "style": "color:inherit",
                                },
                            )
                            link_el.text = tag
                            tags_el.insert(0, link_el)

                    else:
                        span_el = ET.Element("span")
                        span_el.text = tag
                        tags_el.insert(0, span_el)

            # Link files.
            for file_el in [scenario_file] + step_files:
                if file_el is not None and ":" in file_el.text:
                    file_name, line = file_el.text.split(":", 2)
                    if file_name.startswith("NMci"):
                        url = nmci_url_base + file_name.replace("NMci/", "", 1)

                    elif "/site-packages/qecore/" in file_name:
                        url = (
                            qecore_url_base
                            + file_name.split("/site-packages/qecore/")[-1]
                        )

                    else:
                        url = project_url_base + file_name

                    link = ET.SubElement(
                        file_el,
                        "a",
                        {
                            "href": url + "#L" + line,
                            "target": "_blank",
                            "style": "color:inherit",
                        },
                    )
                    link.text = file_el.text
                    file_el.text = ""

        # Formatter html-pretty handling.
        if formatter_instance.name == "html-pretty":
            LOGGING.debug("Handling 'html-pretty' formatter.")

            # Iterate over the data we have and change links where necessary.
            for feature in formatter_instance.features:
                for scenario in feature.scenarios:
                    # Iterate over all tags.
                    for tag in scenario.tags:
                        # Tag class has attributes behave_tag and link
                        # The tag becomes link only after this setup, the default on
                        # formatters' side is <span>.

                        # If the tag.link is not None, it was modified already,
                        # skip another attempt to modify it to link.
                        if tag.has_link():
                            break

                        # Either it becomes a link to Bugzilla, Jira or link to git.
                        if tag.behave_tag.startswith("rhbz"):
                            # Extract just the number from th @rhbz tag so we can link
                            # it to bugzilla.
                            bug_id = tag.behave_tag.replace("rhbz", "").rstrip(",")
                            bug_link = "https://bugzilla.redhat.com/" + bug_id

                            # Tag becomes link to bugzilla.
                            tag.set_link(bug_link)

                        # Either it becomes a link to Jira
                        elif tag.behave_tag.startswith(
                            "RHEL"
                        ) or tag.behave_tag.startswith("DESKTOP"):
                            # Extract just the number from th @RHEL tag so we can link
                            # it to Jira.
                            bug_id = tag.behave_tag.rstrip(",")
                            bug_link = "https://issues.redhat.com/browse/" + bug_id

                            # Tag becomes link to Jira.
                            tag.set_link(bug_link)

                        # No reason to not attempt to do link every single
                        # time, everything should be on git.
                        else:
                            # Tag becomes link to git project.
                            # If the tag was normalized for Outline as a string, use
                            # the scenario location line.
                            if isinstance(tag.behave_tag, str):
                                tag.set_link(
                                    project_url_base
                                    + scenario.location.filename
                                    + "#L"
                                    + str(scenario.location.line)
                                )
                            else:
                                tag.set_link(
                                    project_url_base
                                    + scenario.location.filename
                                    + "#L"
                                    + str(tag.behave_tag.line)
                                )

                    # Iterate once over all steps to make links to its location.
                    for step in scenario.steps:
                        # Iterate over it only in case it was not set yet and
                        # the location exists.
                        if not step.location_link and step.location:
                            # Split the location to file_name and line number
                            # so we can shape it.
                            file_name, line = step.location.split(":", 2)
                            # Handling for NMci project.
                            if file_name.startswith("NMci"):
                                url = nmci_url_base + file_name.replace("NMci/", "", 1)
                            # Handling for qecore project.
                            elif "/site-packages/qecore/" in file_name:
                                url = (
                                    qecore_url_base
                                    + file_name.split("/site-packages/qecore/")[-1]
                                )
                            # Handling for all other projects.
                            else:
                                url = project_url_base + file_name

                            # Set the actual link so formatter can use it.
                            step.location_link = url + "#L" + line

    @property
    def project_git_url(self) -> str:
        """
        Property that returns git url of the project.

        :return: String with the git url.
        :rtype: str
        """

        remote = getattr(self, "_project_git_url", None)
        if remote is None:
            git_remote_run = RunAndLog("sudo git config --get remote.origin.url")
            use_remote = git_remote_run.output.strip("\n")[:-4]

            if git_remote_run.return_code != 0:
                use_remote = ""

            elif use_remote.startswith("git@"):
                use_remote = use_remote.replace(":", "/").replace("git@", "https://")

            self._project_git_url = use_remote

        LOGGING.debug(f"The project_git_url property is returning '{str(self._project_git_url)}'")
        return self._project_git_url

    @property
    def project_git_commit(self) -> str:
        """
        Property that returns git commit of the project.

        :return: String with the git url.
        :rtype: str
        """

        commit = getattr(self, "_project_git_commit", None)
        if commit is None:
            git_commit_run = RunAndLog("sudo git rev-parse HEAD")
            use_commit = git_commit_run.output.strip("\n")

            if git_commit_run.return_code != 0:
                use_commit = ""

            self._project_git_commit = use_commit

        LOGGING.debug(f"The project_git_commit property is returning '{str(self._project_git_commit)}'")
        return self._project_git_commit

    @non_critical_execution
    def _wait_for_video_encoding(self, file_name) -> None:
        """
        Wait until the video is fully encoded.
        This is verified by video's changing size.
        Once the file is encoded the size will not change anymore.

        :type file_name: str
        :param file_name: Video location for size verification.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`attach_video_to_report`.

        This fixes some issues with the video and most of the time the video will
        get passed with all data, in the testing this took between 2-5 seconds.
        But there still are situations when the encoding is not made in the trivial
        amount of time mostly on slower machines. Currently the hard cutoff is 60
        seconds after that the wait will terminate and the video will get passed as
        is to the html report.

        This time loss is no issue with few failing tests and has huge advantage of
        having an entire video with all controlling elements (sometimes the video cannot
        be moved to the middle, or does not have data about its length).
        With many failing tests this might add significant time to the testing time.
        To prevent waiting for the encoded video and therefore not waiting at all use::

            <qecore.sandbox.TestSandbox>.wait_for_stable_video = False
        """

        LOGGING.debug(get_func_params_and_values())

        current_size = 0
        current_stability = 0

        iteration_cutoff = 0

        while current_stability < 30:
            new_size = os.path.getsize(file_name)
            if current_size == new_size:
                current_stability += 1
            else:
                current_stability = 0

            current_size = new_size
            sleep(0.1)

            iteration_cutoff += 1
            if iteration_cutoff > 600:
                break

        LOGGING.debug(f"The stability counter: '{current_stability}")
        LOGGING.debug(f"The iteration cutoff: '{iteration_cutoff}'")

    @non_critical_execution
    def set_background(
        self, color="", background_image=None, background_image_revert=False
    ) -> None:
        """
        Change background to a single color or an image.

        :type color: str
        :param color: String black/white to set as background color.

        :type background_image: str
        :param background_image: Image location to be set as background.

        :type background_image_revert: bool
        :param background_image_revert: Upon settings this to True,
            the :func:`after_scenario` will return the background to the original state,
            after the test.

        To get the wanted color you can pass strings as follows::

            color="black"
            color="white"
            color="#FFFFFF" # or any other color represented by hexadecimal
        """

        LOGGING.debug(get_func_params_and_values())

        self.background_image_revert = background_image_revert

        if self.background_image_revert:
            self.background_image_location = RunAndLog(
                "gsettings get org.gnome.desktop.background picture-uri"
            ).output.strip("\n")

        if background_image:
            if "file://" in background_image:
                RunAndLog(
                    "".join(
                        (
                            "gsettings set org.gnome.desktop.background ",
                            f"picture-uri {background_image}",
                        )
                    )
                )

            else:
                RunAndLog(
                    "".join(
                        (
                            "gsettings set org.gnome.desktop.background ",
                            f"picture-uri file://{background_image}",
                        )
                    )
                )
        elif color == "white":
            RunAndLog("gsettings set org.gnome.desktop.background picture-uri file://")
            RunAndLog('gsettings set org.gnome.desktop.background primary-color "#FFFFFF"')
            RunAndLog('gsettings set org.gnome.desktop.background secondary-color "#FFFFFF"')
            RunAndLog('gsettings set org.gnome.desktop.background color-shading-type "solid"')
        elif color == "black":
            RunAndLog("gsettings set org.gnome.desktop.background picture-uri file://")
            RunAndLog('gsettings set org.gnome.desktop.background primary-color "#000000"')
            RunAndLog('gsettings set org.gnome.desktop.background secondary-color "#000000"')
            RunAndLog('gsettings set org.gnome.desktop.background color-shading-type "solid"')
        elif "#" in color:
            RunAndLog("gsettings set org.gnome.desktop.background picture-uri file://")
            RunAndLog(f"gsettings set org.gnome.desktop.background primary-color '{color}'")
            RunAndLog(f"gsettings set org.gnome.desktop.background secondary-color '{color}'")
            RunAndLog('gsettings set org.gnome.desktop.background color-shading-type "solid"')
        else:
            LOGGING.debug(
                " ".join(
                    (
                        f"Color '{color}' is not defined.",
                        "You can define one yourself and submit merge request.",
                    )
                )
            )

    @non_critical_execution
    def _revert_background_image(self) -> None:
        """
        Revert background image to the before-test state.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`after_scenario`.
        """

        LOGGING.debug(get_func_params_and_values())

        RunAndLog(
            " ".join(
                (
                    "gsettings",
                    "set",
                    "org.gnome.desktop.background",
                    "picture-uri",
                    self.background_image_location,
                )
            )
        )

    def file_loader(self, file_name) -> str:
        """
        Load content from file or upon UnicodeDecodeError debug the location
        of the error and return replaced data.

        :type file_name: str
        :param file_name: String representation of file location.

        :rtype: str
        :return: File data or some debug data and file content replaced in places that
            were not readable.
        """

        LOGGING.debug(get_func_params_and_values())

        _file_data = ""
        if not os.path.isfile(file_name):
            LOGGING.debug("File does not exist.")

            return "File does not exist."

        LOGGING.debug("File exists, continuing to read.")

        try:
            _file_data = open(file_name, "r", encoding="utf-8").read()
            LOGGING.debug("File read is successful.")

        except UnicodeDecodeError as error:
            LOGGING.debug("File read is NOT successful.")

            # Gather all lines that contain non-ASCII characters.
            _file = open(file_name, "rb")
            non_ascii_lines = [
                line for line in _file if any(_byte > 127 for _byte in line)
            ]
            _file.close()

            # Attempt to load the file and replace all error data.
            file_content = open(
                file_name, "r", encoding="utf-8", errors="replace"
            ).read()

            _file_data = f"\nException detected:\n{error}"
            _file_data += (
                f"\nDetected non-ASCII lines:\n{non_ascii_lines}"
                if any(non_ascii_lines)
                else "None"
            )
            _file_data += f"\nReplaced file content:\n{file_content}"

        LOGGING.debug("return _file_data.")

        return _file_data

    @non_critical_execution
    def _attach_qecore_debug_log(self, context) -> None:
        """
        Load content from file or upon UnicodeDecodeError debug the location
        of the error and return replaced data.

        :param context: Holds contextual information during the running of tests.
        :type context: <behave.runner.Context>

        """

        LOGGING.debug(get_func_params_and_values())

        LOGGING.debug("Attaching debug log to the html report.")

        if not (self._attach_qecore_debug or self._embed_all):
            LOGGING.debug(
                f"self._attach_qecore_debug={self._attach_qecore_debug}.",
            )
            return

        if not (
            self._attach_qecore_debug_on_pass or self.failed_test or self._embed_all
        ):
            LOGGING.debug(
                "".join(
                    (
                        f"self.failed_test='{self._attach_qecore_debug}' ",
                        "self._attach_qecore_debug_on_pass=",
                        f"'{str(self._attach_qecore_debug_on_pass)}'.",
                    )
                )
            )
            return

        # Attach this log only once.
        if self._new_log_indicator:
            # If the file is not there, the content will be name of the file.
            # In such case do not embed at all.
            if os.path.isfile(self._qecore_debug_log_file):
                context.embed("text", self._qecore_debug_log_file, "qecore_debug_log")
            else:
                LOGGING.debug("no file to attach.")

    @non_critical_execution
    def enable_logging_to_console(self) -> None:
        """
        Enable logging to console after sandbox is initiated.
        """

        LOGGING.info("Setting qecore to log in console.")
        logging_class.qecore_debug_to_console()

        LOGGING.debug(get_func_params_and_values())

    def disable_shadows_for_gtk4(self) -> None:
        """
        Disable shadows for gtk4.
        """

        LOGGING.debug(get_func_params_and_values())

        if not self.disable_gtk4_shadows:
            LOGGING.debug("Removing gtk4 shadows disabled.")
            LOGGING.debug("Keep in mind that gtk.css file already created is not removed.")
            return

        current_user = os.path.expanduser("~")
        gtk_4_directory = f"{current_user}/.config/gtk-4.0"

        # First, lets check the directory in config directory.
        LOGGING.debug("Checking for gtk-4.0 directory")
        if not os.path.isdir(gtk_4_directory):
            LOGGING.debug("Directory gtk-4.0 not present, creating.")
            mkdir_run = RunAndLog(f"mkdir {gtk_4_directory}")
            sleep(0.2)

            # Check if the directory was created properly.
            if mkdir_run.return_code != 0:
                LOGGING.debug(f"Directory gtk-4.0 failed to be created: '{mkdir_run.error}'.")
                return

        else:
            LOGGING.debug("Directory gtk-4.0 is present.")

        # Second, lets check if the file is present in gtk-4.0 directory.
        gtk_4_css_file = f"{current_user}/.config/gtk-4.0/gtk.css"
        if not os.path.isfile(gtk_4_css_file):
            # Create the file with proper content.
            LOGGING.debug("File gtk.css is not present, creating the file.")

            file_contents = "\n".join(
                (
                    "/* Disable shadows */",
                    "window, .popover, .tooltip {",
                    "    box-shadow: none;",
                    "}\n",
                )
            )

            # Using x mode since we only care about creating a file.
            with open(gtk_4_css_file, "x+", encoding="utf-8") as _file:
                _file.write(file_contents)
            sleep(0.2)

            # Check if the content was inserted properly.
            if not os.path.isfile(gtk_4_css_file):
                LOGGING.debug("Inserting of content to file failed.")
                return

            LOGGING.debug("Creation of the file was a success.")

        else:
            # Lets not write in already present file to not mess up user setup.
            LOGGING.debug("File gtk.css is already present, not making any changes.")

    def _log_sandbox_initiation_to_journal(self, component=None):
        """
        Logging TestSandbox initiation to journal.
        """

        header_message = "Initiating qecore TestSandbox."
        component_tested = f"Component Tested: {component}."

        program_to_invoke = f"echo '===== {header_message} {component_tested} ====='"

        log_message_to_journal(
            priority="warning", identifier="qecore", invoke=program_to_invoke
        )

    def _log_starting_automation_suite_to_journal(self, scenario):
        """
        Logging start of the automation suite.
        """

        header_message = "Starting an Automation Scenario."
        component_tested = f"Component Tested: {self.component}."
        scenario_running = f"Scenario Running: {scenario.tags[-1]}"

        program_to_invoke = (
            f"echo '===== {header_message} {component_tested} {scenario_running} ====='"
        )

        log_message_to_journal(
            priority="warning", identifier="qecore", invoke=program_to_invoke
        )

    def _log_ending_automation_suite_to_journal(self, scenario):
        """
        Logging end of the automation suite.
        """

        header_message = "Ending an Automation Scenario."
        component_tested = f"Component Tested: {self.component}."
        scenario_running = f"Scenario Running: {scenario.tags[-1]}"

        program_to_invoke = (
            f"echo '===== {header_message} {component_tested} {scenario_running} ====='"
        )

        log_message_to_journal(
            priority="warning", identifier="qecore", invoke=program_to_invoke
        )

    def _log_end_of_automation_suite_handling_to_journal(self):
        """
        Logging TestSandbox initiation to journal.
        """

        header_message = "End of Automation Suite handling by qecore."
        component_tested = f"Component Tested: {self.component}."

        program_to_invoke = f"echo '===== {header_message} {component_tested} ====='"

        log_message_to_journal(
            priority="warning", identifier="qecore", invoke=program_to_invoke
        )
