#!/usr/bin/env python3
"""
Common steps part with definition of pre-coded decorator steps for behave usage.
"""

# pylint: disable=broad-exception-caught
# pylint: disable=import-outside-toplevel
# pylint: disable=import-error
# pylint: disable=invalid-name
# pylint: disable=no-name-in-module
# pylint: disable=line-too-long
# ruff: noqa: E501
# ruff: noqa: E402

from time import sleep
import subprocess

from behave import step

from qecore.utility import AUTOMATIC_LOGIN_IN_EFFECT

try:
    from dogtail.rawinput import (
        click,
        keyCombo,
        pressKey,
        typeText,
        absoluteMotion,
    )

except Exception as error:
    if not AUTOMATIC_LOGIN_IN_EFFECT:
        print(f"Expected issues in Common Steps: '{error}'")
    else:
        raise Exception from error

from qecore.utility import get_application, keyboard_character_input, keyboard_key_input, keyboard_key_combo_input
from qecore.get_node import GetNode
from qecore.step_matcher import use_step_matcher


__author__ = """
Filip Pokryvka <fpokryvk@redhat.com>,
Michal Odehnal <modehnal@redhat.com>,
Bohdan Milar <bmilar@redhat.com>
"""

# To stop using "qecore" matcher use matcher "parse".
use_step_matcher("qecore")

HELP = """
This allows multiple decorator definitions on one line separated by ' | '
EXAMPLE:
This decorator:
    @step('Item "{name}" "{role_name}" | with description "{description}" | that is "{attr}"')

matches for example the following steps:
    * Item "foo" "push button"
    * Item "foo" "push button" with description "something useful"
    * Item "foo" "push button" with description "something useful" that is "visible"
    * Item "foo" "push button" that is "visible"

And also any permutation of decorator parts except the first part, so this is also valid step:
    * Item "foo" "push button" that is "visible" with description "something useful"

WARNING:
"qecore" matcher does not work well with unquoted decorator arguments, use "parse" instead
"""

SIZE_DEC = "".join([' | has size at least "{size_low}"',
                    ' | has size at most "{size_high}"'])
POS_DEC = "".join([' | that is at least "{position_low}" from top left',
                   ' | that is at most "{position_high}" from top left'])
SIZE_POS_DEC = SIZE_DEC + POS_DEC

DESC = ' | with description "{description}"'
ACTION = ' | with action "{action}"'
ATTR = ' | that is "{attr}" | is "{attr}"'
ROOT = ' | in "{a11y_root_name}"'
TEXT = ' | has text "{text}"'

NOT_ATTR = ' | that is not "{attr}" | is not "{attr}"'
NOT_TEXT = ' | does not have text "{text}"'
NOT_DESC = ' | does not have description "{description}"'

START_OPTIONS = ' | via "{start_via}" | via command "{command}" | via command | in "{session}" | with env "{environ}"'

# Format ' | with offset "(0,0)"'
OFFSET = ' | with offset "{offset}"'


@step('{m_btn} click "{name}" "{role_name}"' + DESC + ACTION + OFFSET + ATTR + ROOT + SIZE_POS_DEC)
def mouse_click(context, retry=True, expect_positive=True, **kwargs) -> None:
    """
    Mouse clicking function to be used by behave feature files.

    This step will always use raw click.
    """

    with GetNode(context, **kwargs, retry=retry, expect_positive=expect_positive) as (data, node):
        try:
            # Newer dogtail has window_id.
            click(
                x=data.x_node_center,
                y=data.y_node_center,
                button=data.m_btn,
                window_id=node.window_id
            )
        except (AttributeError, TypeError):
            # Older dogtail does not have window_id.
            click(x=data.x_node_center, y=data.y_node_center, button=data.m_btn)


@step('Mouse over "{name}" "{role_name}"' + DESC + ACTION + OFFSET + ATTR + ROOT + SIZE_POS_DEC)
def mouse_over(context, retry=True, expect_positive=True, **kwargs) -> None:
    """
    Mouse over function to be used by behave feature files.
    """

    with GetNode(context, **kwargs, retry=retry, expect_positive=expect_positive) as (data, node):
        try:
            # Newer dogtail has window_id.
            absoluteMotion(
                x=data.x_node_center,
                y=data.y_node_center,
                window_id=node.window_id
            )
        except (AttributeError, TypeError):
            # Older dogtail does not have window_id.
            absoluteMotion(x=data.x_node_center,y=data.y_node_center)


@step('Make an action "{action}" for "{name}" "{role_name}"' + DESC + ACTION + ATTR + ROOT + SIZE_POS_DEC)
def make_action(context, action, retry=True, expect_positive=True, **kwargs) -> None:
    """
    Accessibility action function to be used by behave feature files.
    """

    with GetNode(context, **kwargs, retry=retry, expect_positive=expect_positive) as (_, node):
        node.doActionNamed(action)


@step('Item "{name}" "{role_name}" | found |' + DESC + ACTION + ATTR + ROOT + SIZE_POS_DEC)
def node_attribute(context, retry=True, expect_positive=True, **kwargs) -> None:
    """
    Verification function to be used by behave feature files.
    """

    with GetNode(context, **kwargs, retry=retry, expect_positive=expect_positive) as (_, node):
        assert node is not None, "Node was not found, it should be!"


@step('Item "{name}" "{role_name}" | was not found |' + DESC + ACTION + NOT_ATTR + ROOT + SIZE_POS_DEC)
def node_not_attribute(context, retry=False, expect_positive=False, **kwargs) -> None:
    """
    Verification function negated to be used by behave feature files.
    """

    with GetNode(context, **kwargs, retry=retry, expect_positive=expect_positive) as (_, node):
        assert node is None, "Node was found, it should not be!"


@step('Item "{name}" "{role_name}"' + DESC + ACTION + TEXT + ROOT + SIZE_POS_DEC)
def node_with_text(context, text, retry=True, expect_positive=True, **kwargs) -> None:
    """
    Verification function for text attribute to be used by behave feature files.
    """

    with GetNode(context, **kwargs, retry=retry, expect_positive=expect_positive) as (_, node):
        assert text in node.text, "".join((
            f"Found node should have text: {text}\n",
            f"Instead the node has text: {node.text}",
        ))


@step('Item "{name}" "{role_name}"' + DESC + ACTION + NOT_TEXT + ROOT + SIZE_POS_DEC)
def node_without_text(context, text, retry=True, expect_positive=True, **kwargs) -> None:
    """
    Verification function for text attribute negated to be used by behave feature files.
    """

    with GetNode(context, **kwargs, retry=retry, expect_positive=expect_positive) as (_, node):
        assert text not in node.text, "".join((
            f"Found node should have text: {text}\n",
            f"Node was found with text: {node.text}"
        ))


@step('Item "{name}" "{role_name}"' + NOT_DESC + ACTION + ATTR + ROOT + SIZE_POS_DEC)
def node_without_description(context, description, retry=True, expect_positive=True, **kwargs) -> None:
    """
    Verification function for description attribute negated to be used by behave feature files.
    """

    with GetNode(context, **kwargs, retry=retry, expect_positive=expect_positive) as (_, node):
        assert description not in node.description, "".join((
            f"Found node should not have description: {description}\n",
            f"Instead the node has description: {node.description}"
        ))


@step('Wait until "{name}" "{role_name}"' + DESC + ACTION + ATTR + ROOT + SIZE_POS_DEC)
def wait_until_attr(context, retry=True, expect_positive=True, **kwargs) -> None:
    """
    Wait until accessibility attribute becomes true function to be used by behave feature files.
    """

    with GetNode(context, **kwargs, retry=retry, expect_positive=expect_positive) as (_, node):
        for _ in range(30):
            if not getattr(node, kwargs.get("attr", "sensitive")):
                sleep(0.2)
            else:
                return


@step('Wait until "{name}" "{role_name}" | appears' + DESC + ACTION + ROOT + SIZE_POS_DEC)
def wait_until_in_root(context, retry=True, expect_positive=True, **kwargs) -> None:
    """
    Wait until accessibility object appears function to be used by behave feature files.
    """

    with GetNode(context, **kwargs, retry=retry, expect_positive=expect_positive) as (_, node):
        if node is not None:
            return


@step('Wait until "{name}" "{role_name}" | disappears' + DESC + ACTION + NOT_ATTR + ROOT + SIZE_POS_DEC)
def wait_until_not_in_root(context, retry=False, expect_positive=False, **kwargs) -> None:
    """
    Wait until accessibility object disappears function to be used by behave feature files.
    """

    for _ in range(10):
        with GetNode(context, **kwargs, retry=retry, expect_positive=expect_positive) as (_, node):
            if node is None:
                return
        sleep(1)

    with GetNode(context, **kwargs, retry=retry, expect_positive=expect_positive) as (_, node):
        assert node is None, "Node still found in a11y tree."


@step('Start another instance of "{application_name}"' + START_OPTIONS)
def start_another_instance_of_application(
    context,
    application_name=None,
    start_via="command",
    command=None,
    session=None,
    kill=False
) -> None:
    """
    Start another application instance function to be used by behave feature files.
    """

    start_application(context, application_name, start_via, command, session, kill)


@step('Start application "{application_name}"' + START_OPTIONS)
def start_application(
    context,
    application_name=None,
    start_via="command",
    command=None,
    session=None,
    environ=None,
    kill=True
) -> None:
    """
    Start application function to be used by behave feature files.
    """

    application = get_application(context, application_name)
    if start_via == "menu":
        try:
            application.start_via_menu(kill=kill)
        except Exception:  # pylint: disable=broad-except
            application.start_via_menu(kill=kill)
    elif start_via == "command":
        try:
            application.start_via_command(command=command, in_session=session, kill=kill, environ=environ)
        except RuntimeError as error:
            assert False, error
        except Exception:  # pylint: disable=broad-except
            application.start_via_command(command=command, in_session=session, kill=kill, environ=environ)
    else:
        raise AssertionError("Only defined options are 'command' and 'menu'.")


# Stop using qecore matcher.
use_step_matcher("parse")


@step('Commentary')
def commentary_step(context) -> None:
    """
    Commentary step for usage in behave feature files - html-pretty only.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>
    """

    # Defined only for html-pretty formatter.
    # This will return an instance of PrettyHTMLFormatter.
    formatter_instance = getattr(context, "html_formatter", None)
    if formatter_instance is not None and formatter_instance.name == "html-pretty":
        # Get the correct step to override.
        scenario = formatter_instance.current_scenario
        # Current scenario is never none, as this step is being executed.
        scenario_step = scenario.current_step

        # Override the step, this will prevent the decorator to be generated and only
        # the text will show.
        scenario_step.set_commentary(True)


@step('Close application "{application_name}" via "{close_via}"')
def application_in_not_running(context, application_name=None, close_via="gnome panel") -> None:
    """
    Close application function to be used by behave feature files.
    """

    application = get_application(context, application_name)

    if close_via == "gnome panel":
        # Menu is not in GNOME panel from rhel-10.
        if "10." in context.sandbox.distribution_version:
            assert False, "Application is not present in gnome panel on rhel-10."

        gnome_panel = context.sandbox.shell.child(application.name, "menu")
        for _ in range(10):
            gnome_panel.click()
            sleep(0.5)
            gnome_menu = context.sandbox.shell.findChildren(
                lambda x: x.name == "Quit" and x.roleName == "label"
            )
            if gnome_menu != []:
                gnome_menu[0].click()
                return
            pressKey("Esc")

        assert False, f"Unable to close '{application_name}' via '{close_via}' in 10 tries."

    elif close_via == "gnome panel with workaround":
        # Menu is not in GNOME panel from rhel-10.
        if "10." in context.sandbox.distribution_version:
            assert False, "Application is not present in gnome panel on rhel-10."

        gnome_panel = context.sandbox.shell.child(application.name, "menu")
        for _ in range(10):
            gnome_panel.click()
            sleep(0.5)
            gnome_menu = context.sandbox.shell.findChildren(
                lambda x: x.name == "Quit" and x.roleName == "label"
            )
            if gnome_menu != []:
                gnome_menu[0].point()
                sleep(0.5)
                pressKey("Enter")
                return
            pressKey("Esc")

        assert False, f"Unable to close '{application_name}' via '{close_via}' in 10 tries."

    elif (close_via == "application panel menu") or (
        close_via == "application menu" and context.sandbox.distribution == "Fedora"
    ):
        application_panel = application.instance.children[0][0]
        for _ in range(10):
            application_panel.click(3)
            sleep(0.5)
            application_panel_menu = context.sandbox.shell.findChildren(
                lambda x: x.name == "Close" and x.roleName == "label"
            )
            if application_panel_menu != []:
                application_panel_menu[0].click()
                return
            pressKey("Esc")

        assert False, f"Unable to close '{application_name}' via '{close_via}' in 10 tries."

    elif close_via in ("application file menu", "application menu"):
        for _ in range(10):
            context.execute_steps(f'* Left click "File" "menu" in "{application.component}"')
            sleep(0.5)
            application_file_menu = application.instance.findChildren(
                lambda x:
                ("Close" in x.name or "Quit" in x.name)
                and x.roleName == "menu item" and x.sensitive
            )
            if application_file_menu != []:
                application_file_menu[0].click()
                return
            pressKey("Esc")

        assert False, f"Unable to close '{application_name}' via '{close_via}' in 10 tries."

    elif close_via == "application toggle menu":
        for _ in range(10):
            context.execute_steps(f'* Left click "Application menu" "toggle button" in "{application.component}"')
            sleep(0.5)
            try:
                context.execute_steps(f'* Left click "Quit" "push button" in "{application.component}"')
                return
            except Exception:  # pylint: disable=broad-except
                pressKey("Esc")

        assert False, f"Unable to close '{application_name}' via '{close_via}' in 10 tries."

    elif "menu:" in close_via:
        menu_name = None
        menu_item_name = None
        try:
            _, menu_name, menu_item_name = close_via.split(":")
        except Exception as error:
            raise UserWarning(
                f"Expected format of specific close via menu is 'menu:<menu>:<menu_item>\n{error}"
            ) from error

        for _ in range(10):
            application.instance.child(menu_name, "menu").click()
            sleep(0.5)
            try:
                application.instance.child(menu_item_name, "menu item").click()
                return
            except Exception:  # pylint: disable=broad-except
                pressKey("Esc")

        assert False, f"Unable to close '{application_name}' via '{close_via}' in 10 tries."

    elif close_via == "shortcut":
        application.close_via_shortcut()

    elif close_via == "kill command":
        application.kill_application()

    else:
        raise AssertionError("".join((
            "Only defined options are:\n",
            "'gnome panel', 'application menu', 'shortcut', 'kill command', \n",
            "'application file menu', 'application toggle menu' and 'application panel menu'."
        )))


@step('Application "{application_name}" is no longer running')
def application_is_not_running(context, application_name) -> None:
    """
    Application is not running function to be used by behave feature files.
    """

    application = get_application(context, application_name)
    if application.is_running():
        application.wait_before_app_closes(15)


@step('Application "{application_name}" is running')
def application_is_running(context, application_name) -> None:
    """
    Application is running function to be used by behave feature files.
    """

    application = get_application(context, application_name)
    application.already_running()
    if not application.is_running():
        application.wait_before_app_starts(15)


@step('Run and save command output: "{command}"')
def run_and_save(context, command) -> None:
    """
    Run a shell command and store its returncode, stdout and stderr to context.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :type command: str
    :param command: Command line to be executed and result stored.
    """

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        encoding="utf-8",
    )
    try:
        stdout, stderr = process.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        process.terminate()
        stdout, stderr = process.communicate()

    context.command = command
    context.command_stdout = stdout
    context.command_stderr = stderr
    context.command_return_code = process.returncode


@step('Last command output "{operand}" "{expected_output}"')
def verify_content_in_output(context, operand, expected_output) -> None:
    """
    Verify that the result of last command has a certain data as a result.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :type operand: str
    :param operand: String specifying what operation to do.

    :type expected_output: str
    :param expected_output: Expected data to be compared to the command output.
    """

    assert hasattr(context, "command_stdout"), "".join((
        "\nYou have not saved a command output to be checked.",
        "\nTo do that use '* Run and save command output: \"<command>\"'"
    ))

    valid_operands = ("is", "is not", "contains", "does not contain", "begins with",
                      "does not begin with", "ends with", "does not end with")
    assert operand in valid_operands, "".join((
        f"You have attempted to use operand: '{operand}'",
        f"But only defined operands are:\n'{valid_operands}'"
    ))

    command_output = context.command_stdout
    if operand == "is":
        assert expected_output == command_output, "".join((
            f"\nWanted output: '{expected_output}'",
            f"\nActual output: '{command_output}'"
        ))

    if operand == "is not":
        assert expected_output != command_output, "".join((
            f"\nNot Wanted output: '{expected_output}'",
            f"\nActual output: '{command_output}'"
        ))

    if operand == "contains":
        assert expected_output in command_output, "".join((
            f"\nOutput should contain: '{expected_output}'",
            f"\nBut it does not: '{command_output}'"
        ))

    if operand == "does not contain":
        assert expected_output not in command_output, "".join((
            f"\nOutput should not contain: '{expected_output}'",
            f"\nBut it does: '{command_output}'"
        ))

    if operand == "begins with":
        assert command_output.startswith(expected_output), "".join((
            f"\nOutput should begin with: '{expected_output}'",
            f"\nBut it does not: '{command_output}'"
        ))

    if operand == "does not begin with":
        assert not command_output.startswith(expected_output), "".join((
            f"\nOutput should not begin with: '{expected_output}'",
            f"\nBut it does: '{command_output}'"
        ))

    if operand == "ends with":
        assert command_output.endswith(expected_output), "".join((
            f"\nOutput should end with: '{expected_output}'",
            f"\nBut it does not: '{command_output}'"
        ))

    if operand == "does not end with":
        assert not command_output.endswith(expected_output), "".join((
            f"\nOutput should not end with: '{expected_output}'",
            f"\nBut it does: '{command_output}'"
        ))


@step('Return code of last command output "{operand}" "{expected_return_code}"')
def verify_return_code_of_command(context, operand, expected_return_code) -> None:
    """
    Verify the return code of last command.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :type operand: str
    :param operand: String specifying what operation to do.

    :type expected_return_code: str
    :param expected_return_code: Expected data to be compared to the command output.
    """

    assert hasattr(context, "command_stdout"), "".join((
        "\nYou have not saved a command output to be checked.",
        "\nTo do that use '* Run and save command output: \"<command>\"'"
    ))

    valid_operands = ("is", "is not")
    assert operand in valid_operands, "".join((
        f"You have attempted to use operand: '{operand}'",
        f"But only defined operands are:\n'{valid_operands}'"
    ))

    return_code = context.command_return_code
    if operand == "is":
        assert int(expected_return_code) == int(return_code), "".join((
            f"\nWanted return code: '{expected_return_code}'",
            f"\nActual return code: '{return_code}'"
        ))

    if operand == "is not":
        assert int(expected_return_code) != int(return_code), "".join((
            f"\nNot Wanted return code: '{expected_return_code}'",
            f"\nActual return code: '{return_code}'"
        ))


@step('Type text: "{text}"')
def type_text_step(context, text) -> None:  # pylint: disable=unused-argument
    """
    Typing text function to be used by behave feature files.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param text: Text to type.
    :type text: str
    """

    typeText(text)


@step('Press key: "{key_name}"')
def press_key_step(context, key_name) -> None:  # pylint: disable=unused-argument
    """
    Press key function to be used by behave feature files.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param key_name: Key to press.
    :type key_name: str
    """

    pressKey(key_name)


@step('Type text: "{text}" with uinput')
def type_text_uinput_step(context, text) -> None:  # pylint: disable=unused-argument
    """
    Typing text via uinput function to be used by behave feature files.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param text: Text to type.
    :type text: str
    """

    keyboard_character_input(text)


@step('Press key: "{key_name}" with uinput')
def press_key_uinput_step(context, key_name) -> None:  # pylint: disable=unused-argument
    """
    Press key via uinput function to be used by behave feature files.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param key_name: Key to press.
    :type key_name: str
    """

    keyboard_key_input(key_name)


@step('Key combo: "{combo_name}" with uinput')
def key_combo_uinput_step(context, combo_name) -> None:  # pylint: disable=unused-argument
    """
    Press key via uinput function to be used by behave feature files.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param key_name: Key to press.
    :type key_name: str
    """

    keyboard_key_combo_input(combo_name)


@step('Key combo: "{combo_name}"')
def key_combo_step(context, combo_name) -> None:  # pylint: disable=unused-argument
    """
    Key combo function to be used by behave feature files.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param combo_name: Combo to execute.
    :type combo_name: str
    """

    keyCombo(combo_name)


@step('Wait {number} second before action')
@step('Wait {number} seconds before action')
def wait_up(context, number) -> None:  # pylint: disable=unused-argument
    """
    Sleep function to be used by behave feature files.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param number: Numeric value for sleep.
    :type number: str
    """

    sleep(int(number))


@step('Move mouse to: x: "{position_x}", y: "{position_y}"')
def absolute_motion_step(context, position_x, position_y) -> None:  # pylint: disable=unused-argument
    """
    Move mouse to coordinates function to be used by behave feature files.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param position_x: Position X to move mouse
    :type position_x: str

    :param position_y: Position Y to move mouse to.
    :type position_y: str
    """

    absoluteMotion(int(position_x), int(position_y))


@step('{button} click on: x: "{position_x}", y: "{position_y}"')
def click_on_position(context, button, position_x, position_y) -> None:  # pylint: disable=unused-argument
    """
    Mouse click to coordinates function to be used by behave feature files.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param button: Mouse button to press.
    :type button: str

    :param position_x: Position X to click.
    :type position_x: str

    :param position_y: Position Y to click.
    :type position_y: str
    """

    buttons = {"Left": 1, "Middle": 2, "Right": 3}
    click(int(position_x), int(position_y), buttons[button])


@step('Dummy pass')
def dummy_pass(context):  # pylint: disable=unused-argument
    """
    Dummy step to always PASS.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>
    """

    assert True, "This step always passes."


@step('Dummy fail')
def dummy_fail(context):  # pylint: disable=unused-argument
    """
    Dummy step to always FAIL.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>
    """

    assert False, "This test always fails."
