#!/usr/bin/env python3
"""
This file provides image matching. Looking for a needle in a haystack.
"""

# pylint: disable=broad-exception-caught
# pylint: disable=import-outside-toplevel
# pylint: disable=import-error
# pylint: disable=line-too-long
# pylint: disable=no-name-in-module
# pylint: disable=protected-access
# ruff: noqa: E402
# ruff: noqa: F403
# ruff: noqa: E501

from os import path
from time import sleep

from behave import step

from qecore.utility import AUTOMATIC_LOGIN_IN_EFFECT

try:
    from dogtail.rawinput import click

except Exception as error:
    if not AUTOMATIC_LOGIN_IN_EFFECT:
        print(f"Expected issues in Image Matching: '{error}'")
    else:
        raise Exception from error

from qecore.utility import RunAndLog, get_func_params_and_values
from qecore.logger import Logging

logging_class = Logging()
LOGGING = logging_class.logger


try:
    import cv2
except ModuleNotFoundError:
    print(
        "You need to install an 'opencv-python' via pip or 'python3-opencv' via yum/dnf."
    )
except ImportError:
    print(
        "A possibility of an error on secondary architecture. Image matching will not be available."
    )

HELP_MESSAGE = """
You are encouraged to build your own step function according to your needs.
Two steps that you see bellow are:
    * General step that just compares and asserts the result.
    * General step that just compares and clicks on the found result.

What is needed for image match:
    * You need to capture an image in which we look for the element you want to find.
        * Provided by capture_image method in Matcher class.
        * This option is True by default.
        * If you have your own, set capture=False and provide self.screen_path in the Matcher class.

    * You need to match the two images, you are looking for a 'needle'.
      So you provide it in function or in step call (.feature file).
        * Provided by match which will return True or False. Lets user react on False return value.
        * Provided by assert_match which will assert the result and terminate the test on False.

    * (Optional) You can draw the result for attachment or
            your own confirmation that matching works.
        * Provided by draw method on Matcher instance to get an image with highlighted needle.
          Highlight is a red rectangle exactly in a place of a match, surrounding provided needle.

    * (Optional) You can click on your found result.
        * Provided by click method in Matcher instance.
        * Requirements are of course success of a match/assert_match.

    * (Optional) You can embed result to test report.
        * For this option the method draw is required.
        * Use method provided in TestSandbox class:
            attach_image_to_report(context, image=image_location, caption="DefaultCaption")
        * Or embed it on your own:
            context.embed("image/png", open(image_location, "rb").read(), caption="DefaultCaption")
        * Remember that result is saved in Matcher instance as
            self.diff_path which equals "/tmp/diff.png"

    * (Optional) You can search only in region of screen
        * Firstly, you have to save the region into context.opencv_region attribute
        * Format of this attribute is tuple (node.position, node.size):
            position and size are (x, y) tuples of integers
"""


@step('Image "{needle}" is shown on screen')
@step('Image "{needle}" is shown on screen with threshold "{threshold:f}"')
@step('Image "{needle}" possibly scaled in range "{scale_range}" is shown on screen with threshold "{threshold:f}"')
def image_match(context, needle, threshold=0.8, scale_range="1,1,1") -> None:
    """
    Function with behave step decorators::

        Image "{needle}" is shown on screen
        Image "{needle}" is shown on screen with threshold "{threshold:f}"
        Image "{needle}" possibly scaled in range "{scale_range}" is shown on screen with threshold "{threshold:f}"

    Explanation:

    * **needle** - location of the file to match.
    * **threshold** - float value of threshold for determination of success/failure.
    * **scale_range** - comma separated triple of numbers: start scale, end scale number of steps, example: "0.8,1.2,21".
    """

    scale = [float(i) for i in scale_range.split(",")]
    scale[-1] = int(scale[-1])
    image_match_instance = Matcher(context)
    image_match_instance.assert_match(needle, threshold, scale=scale)
    image_match_instance.draw()


@step('Image "{needle}" is not shown on screen')
@step('Image "{needle}" is not shown on screen with threshold "{threshold:f}"')
def image_not_match(context, needle, threshold=0.8) -> None:
    """
    Function with behave step decorators::

        Image "{needle}" is not shown on screen
        Image "{needle}" is not shown on screen with threshold "{threshold:f}"

    Explanation:

    * **needle** - location of the file to match.
    * **threshold** - float value of threshold for determination of success/failure.
    """

    image_match_instance = Matcher(context)
    positive_match = image_match_instance.match(needle, threshold)
    if positive_match:
        image_match_instance.draw()
        context.attach_opencv = True
    assert not positive_match, "".join(
        (f"Image '{needle}' was found, that was not supposed to happen.")
    )


@step('Image "{needle}" is shown in region')
@step('Image "{needle}" is shown in region with threshold "{threshold:f}"')
def image_region_match(context, needle, threshold=0.8) -> None:
    """
    Function with behave step decorators::

        Image "{needle}" is shown in region
        Image "{needle}" is shown in region with threshold "{threshold:f}"

    Explanation:

    * **needle** - location of the file to match.
    * **threshold** - float value of threshold for determination of success/failure.
    """

    region = getattr(context, "opencv_region", None)
    assert region is not None, "".join(
        ("No region, you must set context.opencv_region first!")
    )
    image_match_instance = Matcher(context)
    image_match_instance.capture_image()
    image_match_instance.crop_image(region)
    image_match_instance.assert_match(needle, threshold, capture=False)
    image_match_instance.draw()


@step('Image "{needle}" is not shown in region')
@step('Image "{needle}" is not shown in region with threshold "{threshold:f}"')
def image_region_not_match(context, needle, threshold=0.8) -> None:
    """
    Function with behave step decorators::

        Image "{needle}" is not shown in region
        Image "{needle}" is not shown in region with threshold "{threshold:f}"

    Explanation:

    * **needle** - location of the file to match.
    * **threshold** - float value of threshold for determination of success/failure.
    """

    region = getattr(context, "opencv_region", None)
    assert region is not None, "No region, you must set context.opencv_region first!"
    image_match_instance = Matcher(context)
    image_match_instance.capture_image()
    image_match_instance.crop_image(region)
    positive_match = image_match_instance.match(needle, threshold, capture=False)
    if positive_match:
        image_match_instance.draw()
        context.attach_opencv = True
    assert not positive_match, "".join(
        (f"Image '{needle}' was found, that was not supposed to happen.")
    )


@step('Locate and click "{needle}"')
def locate_and_click(context, needle) -> None:
    """
    When used with Wayland, the ponytail will translate the click to the focused window.
    This in effect means the image match found in screenshot will have "global" coordinates.
    Which will be translated by ponytail to the application as a (0,0) instead of the
    screen and when application is not full screen it will be wrong.
    To fix this lets attempt to disconnect the focused window and connect only the monitor.

    With x11 we simply use raw click from dogtail.

    Function with behave step decorator::

        Locate and click "{needle}"

    Explanation:

    * **needle** - location of the file to match.
    """

    LOGGING.debug(get_func_params_and_values())

    image_match_instance = Matcher(context)
    image_match_instance.assert_match(needle)

    # With Wayland lets use ponytail to disconnect focused window as coordinates origin.
    try:
        # Import ponytail to check if it is initiated.
        from dogtail.rawinput import ponytail

        # Checking if ponytail is initiated is a good indicator for Wayland.
        if ponytail is not None:
            LOGGING.debug("Ponytail initiated, coordinates translation not in effect.")

            # Lets disconnect focused window as coordinates origin.
            ponytail.disconnect()
            sleep(1)

            # Lets use the whole screen as coordinates origin.
            ponytail.connectMonitor()

            # Calculate the center for the click.
            match_center_x = (
                image_match_instance.matched_loc[0]
                + int(image_match_instance.needle_width / 2)
                + 5
            )
            match_center_y = (
                image_match_instance.matched_loc[1]
                + int(image_match_instance.needle_height / 2)
                + 5
            )

            # Click with rawinput to exact coordinates (some small offset required).
            LOGGING.debug(
                f"Coordinates for ponytail: ({match_center_x}, {match_center_y})"
            )
            ponytail.generateButtonEvent(1, match_center_x, match_center_y)
            return

    except Exception as error:
        LOGGING.info(f"Unexpected error: '{error}'")

    # With Xorg we do not need to change anything and lets do simple rawinput click.
    LOGGING.debug("Clicking to the needle coordinates.")
    image_match_instance.click()


@step('Left click "{needle}" on screen as root')
@step('Left click "{needle}" on screen as root with threshold "{threshold:f}"')
def left_click_on_screen_as_root(context, needle, threshold=0.8) -> None:
    """
    Using ffmpeg as a screenshot provider and uinput library as a device to click.

    Function with behave step decorator::

        Left click "{needle}" on screen as root

    Explanation:

    * **needle** - location of the file to match.

    Recommendation::

        Use your own decorators for better illustration about what it does. For example.

        @step("Click on the Log Out to confirm")
        def click_logout(context) -> None:
            left_click_on_screen_as_root(context, "data/rhel_10_confirm_logout.png", threshold=0.95)


        @step("Click on the Gear Button")
        def click_gear(context) -> None:
            left_click_on_screen_as_root(context, "data/rhel_10_gear_button.png", threshold=0.95)


        @step("Click on the GNOME Classic")
        def click_gnome_classic(context) -> None:
            left_click_on_screen_as_root(context, "data/rhel_10_gear_button_GNOME_Classic.png", threshold=0.8)

    """

    LOGGING.debug(get_func_params_and_values())

    matcher_instance = Matcher(context, autologin=False)

    # Give the machine 10 attempts before failing.
    for iteration in range(10):
        successful_match = matcher_instance.match(needle, threshold=threshold)
        LOGGING.debug(f"Match ended with a value '{matcher_instance.matched_value}' in iteration: {iteration}.")

        if successful_match:
            if hasattr(context, "sandbox"):
                LOGGING.debug(f"Drawing the successful match to '{matcher_instance.diff_path}'.")
                matcher_instance.draw()

            LOGGING.debug("Clicking in the matched needle.")
            matcher_instance.left_click_as_root()
            return True

        else:
            sleep(1)

    return False


@step('Image "{needle}" is shown')
@step('Image "{needle}" is shown with threshold "{threshold:f}"')
def image_is_shown(context, needle, threshold=0.8) -> None:
    """
    Using ffmpeg as a screenshot provider and uinput library as a device to verify
    presence of an image on the screen.

    Function with behave step decorator::

        Image "{needle}" is shown

    Explanation:

    * **needle** - location of the file to match.
    """

    LOGGING.debug(get_func_params_and_values())

    matcher_instance = Matcher(context, autologin=False)

    # Give the machine 10 attempts before failing.
    for iteration in range(10):
        successful_match = matcher_instance.match(needle, threshold=threshold)
        LOGGING.debug(f"Match ended with a value '{matcher_instance.matched_value}' in iteration: {iteration}.")

        if successful_match:
            if hasattr(context, "sandbox"):
                LOGGING.debug(f"Drawing the successful match to '{matcher_instance.diff_path}'.")
                matcher_instance.draw()
            return

        else:
            sleep(1)

    assert successful_match, f"Match was not successful '{matcher_instance.matched_value}'."


class Matcher:
    """
    Matcher class.
    """

    def __init__(self, context, autologin=True) -> None:
        """
        Initiate Matcher instance.

        :type context: <behave.runner.Context>
        :param context: Context object.
        """

        self.context = context
        self.screen_path = "/tmp/pic.png"
        self.diff_path = "/tmp/diff.png"

        if RunAndLog("which gnome-screenshot").return_code == 0:
            self.capture_image_cmd = "gnome-screenshot -f "
        else:
            self.capture_image_cmd = "qecore_capture_screenshot "

        ffmpeg_run = RunAndLog("which ffmpeg")
        ffmpeg_present = ffmpeg_run.return_code == 0

        if not autologin and ffmpeg_present:
            self.capture_image_cmd = "sudo ffmpeg -hide_banner -y -f kmsgrab -i - -vf hwdownload,format=bgr0 -frames 1 -update 1 "

        elif not autologin and not ffmpeg_present:
            LOGGING.debug(f"The ffmpeg was not detected on the system: '{ffmpeg_run.output}'")
            raise RuntimeError(f"The ffmpeg was not detected: {ffmpeg_run.output}")

        self.needle_width = 0
        self.needle_height = 0
        self.matched_value = 0.0
        self.matched_loc = (0, 0)

        self.ori_img = None
        self.ori_img_gray = None
        self.needle = None
        self.needle_size = None


    def capture_image(self, screen_path=None) -> None:
        """
        Captures the image.

        :type screen_path: Path to store the screenshot.
        :param screen_path: str.
        """

        LOGGING.debug(get_func_params_and_values())

        if screen_path is None:
            screen_path = self.screen_path

        remove_screen_run = RunAndLog(f"rm -rfv {screen_path}")
        LOGGING.debug(f"Image matching remove older image: '{remove_screen_run.output}'")

        capture_image_run = RunAndLog(self.capture_image_cmd + screen_path, timeout=5)
        if capture_image_run.output.startswith("file:"):
            screen_captured = capture_image_run.output.replace("file://", "").strip("\n")
            copy_screen_run = RunAndLog(f"cp {screen_captured} {screen_path}")
            LOGGING.debug(f"Image matching copy captured image: '{copy_screen_run.output}'")

        LOGGING.debug(f"Image matching initial screen capture result: '{capture_image_run.output}'")

        sleep(1)
        assert path.isfile(screen_path)


    def crop_image(self, region) -> None:
        """
        Crops the image.

        :type region: list
        :param region: List with four values: (x, y, w, h)
        """

        LOGGING.debug(get_func_params_and_values())

        self.ori_img = cv2.imread(self.screen_path)
        (x, y), (w, h) = region
        if self.context.sandbox.session_type == "wayland":
            y += self.context.sandbox.shell.child("System", "menu").size[1]
        self.ori_img = self.ori_img[y : y + h, x : x + w]
        cv2.imwrite(self.screen_path, self.ori_img)


    def assert_match(
        self, needle, threshold=0.8, capture=True, scale=(1.0, 1.0, 1)
    ) -> None:
        """
        Calls and asserts the result of :py:func:`match`.

        :type needle: str
        :param needle: Needle location.

        :type threshold: float
        :param threshold: Value of acceptable match.

        :type scale: tuple
        :param scale: Triple representing scale range: (scale start, scale end, step count)

        :type capture: bool
        :param capture: Decides if the image will be captured.
        """

        LOGGING.debug(get_func_params_and_values())

        assert self.match(needle, threshold, capture, scale), "".join(
            (f"Image match value: {self.matched_value}")
        )


    def match(self, needle, threshold=0.8, capture=True, scale=(1.0, 1.0, 1)) -> bool:
        """
        Trying to find the needle image inside the captured image.

        :type needle: str
        :param needle: Needle location.

        :type threshold: float
        :param threshold: Value of acceptable match.

        :type capture: bool
        :param capture: Decides if the image will be captured.

        :type scale: tuple
        :param scale: Triple representing scale range: (scale start, scale end, step count)

        :rtype: bool
        :return: Boolean value of the matching.
        """

        LOGGING.debug(get_func_params_and_values())

        if capture:
            self.capture_image()

        self.ori_img = cv2.imread(self.screen_path)
        _, self.ori_img_width, self.ori_img_height = self.ori_img.shape[::-1]
        self.ori_img_gray = cv2.cvtColor(self.ori_img, cv2.COLOR_BGR2GRAY)
        self.needle = cv2.imread(path.abspath(needle), 0)
        best_match = 0
        scale_start, scale_end, scale_count = scale
        # avoid division by zero
        scale_step = (
            0 if scale_count == 1 else (scale_end - scale_start) / (scale_count - 1)
        )
        for i in range(scale_count):
            scale_factor = scale_start + i * scale_step
            # for some reason, cv2.resize destination size is reversed shape
            new_size = tuple(
                reversed([int(x * scale_factor) for x in self.needle.shape[:2]])
            )
            resized = cv2.resize(self.needle, new_size, interpolation=cv2.INTER_AREA)
            match = cv2.matchTemplate(self.ori_img_gray, resized, cv2.TM_CCOEFF_NORMED)
            _, matched_value, _, matched_loc = cv2.minMaxLoc(match)
            if matched_value > best_match:
                best_match = matched_value
                self.matched_value = matched_value
                self.matched_loc = matched_loc
                self.needle_width, self.needle_height = resized.shape[::-1]

        if hasattr(self.context, "sandbox") and (
            self.context.sandbox.attach_screenshot_on_pass
            or self.context.sandbox._embed_all
        ):
            self.context.sandbox.attach_image_to_report(self.context, needle, "Needle")
            self.context.sandbox.attach_image_to_report(self.context, self.screen_path, "Searching in Screenshot")

        return self.matched_value > threshold


    def draw(self) -> None:
        """
        Draws the result to the original image.
        """

        LOGGING.debug(get_func_params_and_values())

        self.needle_size = (
            self.matched_loc[0] + self.needle_width,
            self.matched_loc[1] + self.needle_height,
        )
        cv2.rectangle(self.ori_img, self.matched_loc, self.needle_size, (0, 0, 255), 2)
        cv2.imwrite(self.diff_path, self.ori_img)
        if hasattr(self.context, "sandbox") and (
            self.context.sandbox.attach_screenshot_on_pass
            or self.context.sandbox._embed_all
        ):
            self.context.sandbox.attach_image_to_report(self.context, self.diff_path, "Matched Screenshot")


    def click(self) -> None:
        """
        Clicks to the center of the result.
        """

        LOGGING.debug(get_func_params_and_values())

        match_center_x = self.matched_loc[0] + int(self.needle_width / 2)
        match_center_y = self.matched_loc[1] + int(self.needle_height / 2)

        LOGGING.debug(f"Clicking at coordinates: ({match_center_x},{match_center_y})")
        click(match_center_x, match_center_y)
        sleep(1)


    def left_click_as_root(self) -> None:
        """
        Click in the Display Manager with different coordinate system.
        """

        LOGGING.debug("Checking availability of uinput library.")
        import importlib
        if not importlib.util.find_spec("uinput"):
            raise RuntimeError("Missing module 'uinput' on the System. Unable to use this function.")

        import uinput

        ABS_MAX = 2**16

        # Initialize the uinput device.
        self.device = uinput.Device((
            uinput.ABS_X + (0, ABS_MAX, 0, 0),
            uinput.ABS_Y + (0, ABS_MAX, 0, 0),
            uinput.BTN_LEFT,
            uinput.BTN_MIDDLE,
            uinput.BTN_RIGHT,
            uinput.REL_WHEEL,
        ))

        # Critical part, without this we emit inputs before the device is initiated.
        sleep(1)

        match_center_x = int (self.matched_loc[0] + self.needle_width / 2)
        match_center_y = int (self.matched_loc[1] + self.needle_height / 2)
        match_center = (match_center_x, match_center_y)
        LOGGING.debug(f"Needle location center: '{match_center}'")

        float_center_x = (match_center_x / self.ori_img_width)
        float_center_y = (match_center_y / self.ori_img_height)
        float_center = (float_center_x, float_center_y)
        LOGGING.debug(f"Calculating needle center in interval <0, 1>: '{float_center}'")

        for uinput_axis, value in [(uinput.ABS_X, float_center_x), (uinput.ABS_Y, float_center_y)]:
            if not (0 <= value <= 1):
                raise ValueError("Values must be floats between 0 and 1.")
            LOGGING.debug(f"Value '{value}' is between 0 and 1.")

            converted = int(value * ABS_MAX)
            LOGGING.debug(f"Emitting mouse movement to converted location: '{converted}'")
            self.device.emit(uinput_axis, converted, syn=False)

        # Both axes move at once
        self.device.syn()
        sleep(0.2)

        # press the button
        LOGGING.debug("Emitting Left mouse button Press.")
        self.device.emit(uinput.BTN_LEFT, 1)

        # Wait a little.
        sleep(0.1)

        # Release the button.
        LOGGING.debug("Emitting Left mouse button Release.")
        self.device.emit(uinput.BTN_LEFT, 0)


def debug_click_via_image(context, atspi_object, click_button=1):
    """
    Debug function to take a screenshot and using opencv insert click position.

    Keep in mind that ponytail will translate coordinates to the focused window on Wayland.

    :param context: Holds contextual information during the running of tests.
    :type context: <behave.runner.Context>

    :param atspi_object: Atspi object to be clicked.
    :type atspi_object: <Accessible...>

    :param click_button: Mouse button to click, defaults to 1
    :type click_button: int
    """

    LOGGING.debug(get_func_params_and_values())
    LOGGING.debug("Ponytail will translate coordinates to the focused window.")

    # Make a screenshot and load base file as base image.
    base_image = "/tmp/test.png"
    # Make a new screenshot.
    Matcher(context).capture_image(base_image)
    sleep(0.5)

    # Load the screenshot as a base.
    grid_image_target = cv2.imread(base_image)
    click_point_image_target = cv2.imread(base_image)

    starting_point = 0

    increment_small = 20
    starting_point_small = 20

    ending_point = 10000

    # Make first debug image, grid of lines over the base image.
    grid_debug_image = "/tmp/grid_debug_image.png"
    LOGGING.debug(f"File for grid debug: '{grid_debug_image}'")

    for i in range(100):
        v_start_point = (starting_point, starting_point_small + increment_small * i)
        v_end_point = (ending_point, starting_point_small + increment_small * i)
        start_point = (starting_point_small + increment_small * i, starting_point)
        end_point = (starting_point_small + increment_small * i, ending_point)

        if (starting_point_small + increment_small * i) % 100 == 0:
            color = (106, 212, 212)
            thickness = 2
        else:
            color = (78, 109, 153)
            thickness = 1

        grid_image_target = cv2.line(
            grid_image_target, start_point, end_point, color, thickness
        )
        grid_image_target = cv2.line(
            grid_image_target, v_start_point, v_end_point, color, thickness
        )

    if not hasattr(context, "grid_shown") or (hasattr(context, "grid_shown") and not context.grid_shown):
        LOGGING.debug("Writing grid_debug_image")
        cv2.imwrite(grid_debug_image, grid_image_target)
        context.grid_shown = True

    # Second debug image based on click position.
    click_point_debug_image = "/tmp/click_point_debug_image.png"
    LOGGING.debug(f"File for click debug: '{click_point_debug_image}'")

    x = int(atspi_object.position[0] + atspi_object.size[0] / 2)
    y = int(atspi_object.position[1] + atspi_object.size[1] / 2)
    cv2.circle(
        click_point_image_target, (x, y), radius=0, color=(0, 0, 255), thickness=8
    )
    cv2.circle(
        click_point_image_target, (x, y), radius=0, color=(255, 255, 255), thickness=5
    )
    cv2.putText(
        click_point_image_target,
        f"({x},{y})",
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (211, 0, 160),
        1,
    )

    LOGGING.debug("Writing click_point_debug_image")
    cv2.imwrite(click_point_debug_image, click_point_image_target)

    LOGGING.debug(f"Clicking at x:'{x}', y:'{y}' to obj {atspi_object.name}")

    try:
        atspi_object.click(click_button)
    except Exception:
        click(x, y, click_button)

    context.embed(
        mime_type="image/png",
        data=grid_debug_image,
        caption="Grid Image",
    )
    cap = f"Click ({x}, {y})"
    context.embed(
        mime_type="image/png",
        data=click_point_debug_image,
        caption=cap,
    )
    sleep(1)
