"""
The app bar is a key element of the CAVE App, positioned on the left or
right side of the screen. It provides actions that allow users to
navigate between [pages][], launch [panes][], and interact with the
CAVE API through [predefined][] or [custom][] commands.

If specified, both left and right side app bars can be displayed
simultaneously.

[pages]: pages.html
[panes]: panes.html
[predefined]: #appBar_data_star.spec
[custom]: #appBar_data_star.spec
"""

from cave_utils.api_utils.validator_utils import ApiValidator, CustomKeyValidator
import type_enforced


@type_enforced.Enforcer
class appBar(ApiValidator):
    """
    The app bar is located under the path **`appBar`**.
    """

    @staticmethod
    def spec(data: dict = dict(), **kwargs):
        """
        @private
        Arguments:

        * **`data`**: `[dict]` = `{}` &rarr; The data to pass to `appBar.data.*`.
        """
        return {"kwargs": kwargs, "accepted_values": {}}

    def __extend_spec__(self, **kwargs):
        data = self.data.get("data", {})
        CustomKeyValidator(
            data=data, log=self.log, prepend_path=["data"], validator=appBar_data_star, **kwargs
        )


@type_enforced.Enforcer
class appBar_data_star(ApiValidator):
    """
    The app bar data is located under the path **`appBar.data`**.
    """

    @staticmethod
    def spec(
        icon: str,
        type: str,
        bar: str,
        variant: str | None = None,
        color: str | None = None,
        apiCommand: str | None = None,
        apiCommandKeys: list[str] | None = None,
        **kwargs,
    ):
        """
        Arguments:

        * **`icon`**: `[str]` &rarr; An icon to display in the center of the action element.
            * **Note**: It must be a valid icon name from the [react-icons][] bundle, preceded by the abbreviated name of the icon library source.
            * **Example**: `"md/MdRocket"`.
        * **`type`**: `[str]` &rarr; The type of object displayed when the action is triggered.
            * **Accepted Values**:
                * `"session"`: The Session Pane
                * `"settings"`: The Application Settings Pane
                * `"button"`: A button that allows you to send a command to the CAVE API
                * `"pane"`: A [custom pane][]
                * `"page"`: A [page][]
        * **`bar`**: `[str]` &rarr; The location of the action element.
            * **Accepted Values**:
                * `"upperLeft"`: Upper section of the left-side bar
                * `"lowerLeft"`: Lower section of the left-side bar
                * `"upperRight"`: Upper section of the right-side bar
                * `"lowerRight"`: Lower section of the right-side bar
        * **`variant`**: `[str]` = `None` &rarr; The variant of the button.
            * **Accepted Values**:
                * When **`type`** == `"pane"`:
                    * `"modal"`: A [modal pane][]
                    * `"wall"`: A [wall pane][]
                * Otherwise:
                    * `None`
        * **`color`**: `[str]` = `<system-default-value>` &rarr;
            * The color of the button. If omitted, the default value is set by the system.
            * **Note**: It must be a valid RGBA string.
            * **Example**: `"rgba(255, 255, 255, 1)"`.
        * **`apiCommand`**: `[str]` = `None` &rarr; The name of the [API command][] to trigger.
        * **`apiCommandKeys`**: `[list[str]]` = `None` &rarr;
            * The root API keys to pass to your `execute_command` function if an
            `apiCommand` is provided. If omitted, all API keys are
            passed to `execute_command`.

        [page]: pages.html
        [pane]: panes.html
        [modal pane]: panes.html
        [wall pane]: panes.html
        [API command]: #appBar_data_star.spec
        [react-icons]: https://react-icons.github.io/react-icons/search
        """
        return {
            "kwargs": kwargs,
            "accepted_values": {
                "type": ["session", "settings", "button", "pane", "page"],
                "variant": ["modal", "wall"] if type == "pane" else [],
                "bar": ["upperLeft", "lowerLeft", "upperRight", "lowerRight"],
            },
        }

    def __extend_spec__(self, **kwargs):
        color = self.data.get("color")
        if color:
            self.__check_color_string_valid__(color_string=color, prepend_path=["color"])
        # Validate pageIds
        bar_type = self.data.get("type")
        if bar_type == "page":
            self.__check_subset_valid__(
                subset=[kwargs.get("CustomKeyValidatorFieldId")],
                valid_values=kwargs.get("page_validPageIds", []),
                prepend_path=[],
            )
        if bar_type == "pane":
            self.__check_subset_valid__(
                subset=[kwargs.get("CustomKeyValidatorFieldId")],
                valid_values=kwargs.get("pane_validPaneIds", []),
                prepend_path=[],
            )
