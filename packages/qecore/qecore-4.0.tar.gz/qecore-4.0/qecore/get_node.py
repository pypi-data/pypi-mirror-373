#!/usr/bin/env python3
"""
Get Node class to be used for common_steps.
"""

# pylint: disable=broad-exception-caught
# pylint: disable=import-outside-toplevel
# pylint: disable=import-error
# ruff: noqa: E501

import sys
import traceback
import re

from qecore.logger import Logging
from qecore.utility import Tuple

logging_class = Logging()
LOGGING = logging_class.logger


# For python 3.6.
if not hasattr(re, "Pattern"):
    re.Pattern = re._pattern_type  # pylint: disable=protected-access

__author__ = """
Filip Pokryvka <fpokryvk@redhat.com>,
Michal Odehnal <modehnal@redhat.com>
"""


class GetNode:
    """
    Get Node class for common_steps usage.
    """

    def __init__(self, context, **kwargs) -> None:
        """
        Initiate GetNode instance.
        Workhorse for most of the :py:mod:`common_steps`.

        :type context: <behave.runner.Context>
        :param context: Context object that is passed from common steps.

        :type name: str
        :param name: Node.name

        :type role_name: str
        :param role_name: Node.roleName

        :type description: str
        :param description: Node.description

        :type action: str
        :param action: Node.actions

        :type offset: str
        :param offset: Offset to use before click is executed.

        :type m_btn: str
        :param m_btn: Mouse click after node identification.
            Accepted values are "Left", "Middle" and "Right".

        :type attr: str
        :param attr: Node identification: attribute.
            The most used options are: ["showing", "visible", "checked", "focused", "sensitive"]

        :type size_low: string
        :param size_low: minimum node size
            Should be formatted "width,height", where width and height are integers

        :type size_high: string
        :param size_high: maximum node size
            Should be formatted "width,height", where width and height are integers

        :type position_low: string
        :param position_low: minimum distance from top left corner
            Should be formatted "x,y", where x and y are integers

        :type position_high: string
        :param position_high: maximum distance from top left corner
            Should be formatted "x,y", where x and y are integers

        :type a11y_root_name: str
        :param a11y_root_name: Application name.
            Application name to be found in context.<app_name> or in accessibility tree.
            If search of accessibility tree fails the context object will be examined
            for Application instance.

        :type retry: bool
        :param retry: Option to give search function to look again a few times if search fails.
            Used for slower applications. User might want to click right away but window can
            have a few seconds delay.

        :type expect_positive: bool
        :param expect_positive: Option to pass the common step call if the node is not found.
            Some steps might want the node not to be found.

        .. note::

            This class serves only for the purposes of the :py:mod:`common_steps` implementation.
        """

        # Importing here to prevent earlier import error when session is not ready yet.
        from dogtail.tree import root

        name = kwargs.get("name", None)
        role_name = kwargs.get("role_name", None)
        m_btn = kwargs.get("m_btn", None)
        attr = kwargs.get("attr", None)
        description = kwargs.get("description", None)
        action = kwargs.get("action", None)

        offset = kwargs.get("offset", "0,0")

        self.x_node_center = 0
        self.y_node_center = 0

        def string_to_int_tuple(arg) -> Tuple:
            return Tuple((int(x) for x in arg.split(",")))

        self.size_low = string_to_int_tuple(kwargs.get("size_low", "1,0"))
        self.size_high = string_to_int_tuple(kwargs.get("size_high", "1000000,1000000"))
        self.position_low = string_to_int_tuple(kwargs.get("position_low", "-20,-20"))
        self.position_high = string_to_int_tuple(kwargs.get("position_high", "1000000,1000000"))

        a11y_root_name = kwargs.get("a11y_root_name", None)
        retry = kwargs.get("retry", False)
        expect_positive = kwargs.get("expect_positive", False)

        # Root accessibility object's name is given.
        if a11y_root_name is not None:
            # Try to find root application name in context.
            if hasattr(context, a11y_root_name):
                # If the user runs action on application lets assume it is running.
                # Save the application class instance.
                application_class_instance = getattr(context, a11y_root_name)
                # The a11y instance does not have to be loaded right away, try to load it.
                if not application_class_instance.instance:
                    # This is needed to get a11y root if
                    # application was not started by common steps.
                    application_class_instance.already_running()
                # Instance should be loaded so we can load the root.
                self.root = application_class_instance.instance
            # Try to find root application name in accessibility tree.
            else:
                try:
                    self.root = root.application(a11y_root_name)
                except Exception as error:
                    raise UserWarning(
                        "".join(
                            (
                                f"You are attempting to use '{a11y_root_name}' ",
                                f"as root application.\n{error}",
                            )
                        )
                    ) from error

        # Root accessibility object's name is not given.
        else:
            # Only option for not having the name is to have default application set.
            try:
                # If the user runs action on application lets assume it is running.
                default_application_class_instance = context.sandbox.default_application
                # The a11y instance does not have to be loaded right away, try to load it.
                if not default_application_class_instance.instance:
                    # This is needed to get a11y root if
                    # application was not started by common steps.
                    default_application_class_instance.already_running()
                # Instance should be loaded so we can load the root.
                self.root = default_application_class_instance.instance
            except AttributeError:
                traceback.print_exc(file=sys.stdout)
                assert False, "".join(
                    (
                        "\nYou need to define a default application ",
                        "if you are using steps without root.",
                    )
                )

        # Attempt to prevent the following error when loading the application.
        # GLib.GError: atspi_error: The application no longer exists (0)
        # Variable for all application names.
        application_list = []
        # Variable for all accessibility objects for name loading later.
        application_objects = []
        # Set a flag to not spam console in positive cases.
        exception_occurred = False
        for _ in range(5):
            try:
                # Load all application objects.
                application_objects = root.applications()
            except Exception as error:
                # Log to the console right away proving the error comes from this part.
                LOGGING.debug(
                    f"Exception thrown when loading all applications: '{error}'"
                )
            else:
                # Execute only when the exception is not thrown.
                # Break the cycle if the application objects are loaded.
                break

        # Iterate over all application objects and load application names to the list.
        for _ in range(5):
            for application in application_objects:
                try:
                    # Load the name of the object to the list.
                    application_list.append(application.name)
                except Exception as error:
                    exception_occurred = True
                    LOGGING.debug(
                        f"Exception thrown while getting object name: '{error}'"
                    )
                    # Append dummy string to show something went wrong.
                    application_list.append("<exception_occurrence>")

            # Break the cycle if the application names are loaded.
            break

        # Log the final application list only when error occurred when loading names.
        if exception_occurred:
            LOGGING.debug(f"Final application list: '{application_list}'")

        # Check if the root of our application is in the list.
        if self.root.name not in application_list:
            assert False, "".join(
                (
                    f"You are trying to do action in application: '{self.root.name}' ",
                    "which is not detected running.\n",
                    f"Detected applications are: '{application_list}'",
                )
            )

        # Validate various options.
        mouse_map = {"Left": 1, "Middle": 2, "Right": 3, "None": None}
        try:
            self.m_btn = mouse_map[str(m_btn)]
        except KeyError:
            traceback.print_exc(file=sys.stdout)
            assert False, "\nUnknown mouse button! Check your feature file!\n"

        def string_to_regex(arg, flags=0):
            if arg is None or arg == "None":
                return None
            if arg == "Empty":
                return ""
            if arg.startswith("r:"):
                return re.compile(arg[2:], flags=flags)
            return "".join(arg)

        self.name = string_to_regex(name, flags=re.DOTALL | re.MULTILINE)
        self.role_name = string_to_regex(role_name)
        self.description = string_to_regex(description, flags=re.DOTALL | re.MULTILINE)
        self.action = string_to_regex(action, flags=re.DOTALL | re.MULTILINE)

        try:
            # Expected format is "(X,Y)" but for example "X, Y" will work too.
            self.offset = offset.lstrip("(").rstrip(")").replace(" ", "").split(",")
            self.offset_x = int(self.offset[0])
            self.offset_y = int(self.offset[1])

        except Exception as error:
            self.offset = [0, 0]
            self.offset_x = 0
            self.offset_y = 0

            LOGGING.debug(f"Offset provided in unexpected format: '{error}'")
            LOGGING.debug("Expected format is '(X,Y)'.")

        defined_attributes = [
            "showing",
            "visible",
            "checked",
            "focused",
            "focusable",
            "sensitive",
        ]
        self.attr = (
            attr if attr in defined_attributes else None if attr is None else False
        )
        assert self.attr is not False, "".join(
            (
                "\nUnknown attribute. Check your feature file!",
                f"\nAttributes defined are '{str(defined_attributes)}'. ",
                f"You tried to use: '{self.attr}'",
            )
        )

        self.retry = retry if isinstance(retry, bool) else None
        assert self.retry is not None, "\n".join(
            (
                "\nUnknown retry state. Check your feature file!",
                f"Expected attribute is 'True' or 'False'. You tried to use: '{self.attr}'",
            )
        )

        self.expect_positive = (
            expect_positive if isinstance(expect_positive, bool) else None
        )
        assert self.expect_positive is not None, "".join(
            (
                "\nUnknown expect_positive state. Check your feature file!"
                "\nExpected attribute is 'True' or 'False'. ",
                f"You tried to use: '{self.expect_positive}'",
            )
        )

    def __enter__(self):
        try:
            found_node = self.root.findChild(
                lambda x: (
                    (not isinstance(self.name, str)) or self.name in repr(x.name)
                )
                and (
                    (not isinstance(self.name, re.Pattern))
                    or re.fullmatch(self.name, x.name)
                )
                and (
                    (not isinstance(self.role_name, str))
                    or (
                        (self.role_name != "push button" and self.role_name == x.roleName)
                        or
                        (self.role_name == "push button" and x.roleName in ("button", "push button"))
                    )
                )
                and (
                    (not isinstance(self.role_name, re.Pattern))
                    or re.fullmatch(self.role_name, x.roleName)
                )
                and (
                    (not isinstance(self.description, str))
                    or self.description in repr(x.description)
                )
                and (
                    (not isinstance(self.description, re.Pattern))
                    or re.fullmatch(self.description, x.description)
                )
                and ((not isinstance(self.action, str)) or self.action in x.actions)
                and ((self.attr is None) or getattr(x, self.attr))
                and Tuple(x.position) >= self.position_low
                and Tuple(x.position) <= self.position_high
                and Tuple(x.size) >= self.size_low
                and Tuple(x.size) <= self.size_high,
                retry=self.retry,
            )
        except Exception as error:
            if self.expect_positive:
                assert False, self.get_error_message(self, error)
            else:
                # When not expecting positives, lets return the result right away.
                return (self, None)

        # Once the Node is found lets get the center with offset for better manipulation later.
        self.x_node_center = int(
            found_node.position[0] + found_node.size[0] / 2 + self.offset_x
        )
        self.y_node_center = int(
            found_node.position[1] + found_node.size[1] / 2 + self.offset_y
        )

        return (self, found_node)

    def __exit__(self, exc_type, exc_value, trace_b) -> bool:
        if exc_type is not None:
            return False
        return True

    def get_formatted_duplicates(self, list_size, list_of_duplicates, attr) -> str:
        """
        Take list of duplicates and format them for error message.

        :type list_size: int
        :param list_size: Size of the list_of_duplicates.

        :type list_of_duplicates: list
        :param list_of_duplicates: List of Nodes to handle for error message.

        :type attr: string
        :param attr: Node passed to the function.

        :rtype: string
        :return: Formatted string output.

        .. note::

            This serves only for the purpose of formatted error message upon search fail.
            Used by :py:func:`get_error_message`.
        """

        tab_space = " " * 4

        return (
            "".join(
                sorted(
                    {
                        "".join(
                            (
                                tab_space,
                                f"{'name'}: {repr(node.name)} ",
                                f"{'roleName'}: '{node.roleName}' ",
                                f"{'position'}: '{node.position}' ",
                                f"{'size'}: '{node.size}' ",
                                f"{attr if attr else 'attribute'}: ",
                                f"'{getattr(node, attr) if attr else 'None'}'",
                                "\n",
                            )
                        )
                        for node in list_of_duplicates
                    },
                    key=str.lower,
                )
            )
            if list_size != 0
            else tab_space + "None\n"
        )

    def get_formatted_error_message(
        self, error, node_name, same_name_items, node_role_name, same_role_name_items
    ) -> str:
        """
        Take lists of duplicates with name and roleName and format them for error message.

        :type error: string
        :param error: Error - reason why the search for Node failed.

        :type node_name: string
        :param node_name: Node.name that was searched for.

        :type same_name_items: list
        :param same_name_items: List of all items with the name node_name.

        :type node_role_name: string
        :param node_role_name: Node.roleName that was searched for.

        :type same_role_name_items: list
        :param same_role_name_items: List of all items with the roleName node_role_name.

        :rtype: string
        :return: Formatted string output of all :py:func:`get_formatted_duplicates`

        .. note::

            This serves only for the purpose of formatted error message upon search fail.
            Used by :py:func:`get_error_message`.
        """

        return "".join(
            (
                "\n\n",
                f"Item was not found: {error}",
                "\n\n",
                f"Items with name: {node_name}:",
                "\n",
                same_name_items,
                "\n",
                f"Items with roleName: {node_role_name}:",
                "\n",
                same_role_name_items,
                "\n",
            )
        )

    def get_error_message(self, node, error) -> str:
        """
        Main handler for error message with :py:func:`get_formatted_error_message` and
        :py:func:`get_formatted_duplicates` being used to get desired result.

        :type node: GetNode
        :param node: Instanced GetNode to have all data needed about the error.

        :type error: string
        :param error: Error message as to why the search failed.

        .. note::

            This serves only for the purpose of formatted error message upon search fail
            when using :py:mod:`common_steps`.
        """

        name = repr(node.name)
        nodes_with_name = []
        if isinstance(node.name, str):
            nodes_with_name = node.root.findChildren(
                lambda x: node.name in x.name
                and (not (node.name != "") or x.name != "")
            )
        elif isinstance(node.name, re.Pattern):
            name = f"REGEX:{repr(node.name.pattern)}"
            nodes_with_name = node.root.findChildren(
                lambda x: re.fullmatch(node.name, x.name)
            )
        nodes_with_name_size = len(nodes_with_name)
        nodes_with_name_formatted = self.get_formatted_duplicates(
            nodes_with_name_size, nodes_with_name, node.attr
        )
        role_name = repr(node.role_name)
        nodes_with_role_name = []

        validated_role_name = node.role_name
        if validated_role_name == "push button":
            validated_role_name = "button"

        if isinstance(node.role_name, str):
            nodes_with_role_name = node.root.findChildren(
                lambda x: validated_role_name in x.roleName
            )
        elif isinstance(node.name, re.Pattern):
            role_name = f"REGEX:{repr(validated_role_name.pattern)}"
            nodes_with_role_name = node.root.findChildren(
                lambda x: re.fullmatch(validated_role_name, x.roleName)
            )
        nodes_with_role_name_size = len(nodes_with_role_name)
        nodes_with_role_name_formatted = self.get_formatted_duplicates(
            nodes_with_role_name_size, nodes_with_role_name, node.attr
        )

        return self.get_formatted_error_message(
            error,
            name,
            nodes_with_name_formatted,
            role_name,
            nodes_with_role_name_formatted,
        )
