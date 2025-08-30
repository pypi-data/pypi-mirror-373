"""
General API Spec items that are found in multiple places. This is not a key that should be passed as part of your `session_data`.
"""

from pamda import pamda
import type_enforced
from cave_utils.api_utils.validator_utils import ApiValidator, CustomKeyValidator


@type_enforced.Enforcer
class props(ApiValidator):
    @staticmethod
    def spec(
        name: str,
        type: str,
        subtitle: str | None = None,
        help: str | None = None,
        helperText: str | None = None,
        variant: str | None = None,
        display: bool | None = None,
        enabled: bool | None = None,
        container: str | None = None,
        apiCommand: str | None = None,
        apiCommandKeys: list[str] | None = None,
        options: dict | None = None,
        valueOptions: list[int | float] | None = None,
        label: str | None = None,
        labelPlacement: str | None = None,
        activeLabel: str | None = None,
        placeholder: str | None = None,
        maxValue: float | int | None = None,
        minValue: float | int | None = None,
        gradient: dict | None = None,
        fallback: dict | None = None,
        maxRows: int | None = None,
        minRows: int | None = None,
        rows: int | None = None,
        notation: str | None = None,
        precision: int | None = None,
        notationDisplay: str | None = None,
        unit: str | None = None,
        unitPlacement: str | None = None,
        views: list[str] | None = None,
        legendNotation: str | None = None,
        legendPrecision: int | None = None,
        legendNotationDisplay: str | None = None,
        legendMinLabel: str | None = None,
        legendMaxLabel: str | None = None,
        icon: str | None = None,
        activeIcon: str | None = None,
        startIcon: str | None = None,
        endIcon: str | None = None,
        color: str | None = None,
        activeColor: str | None = None,
        size: str | None = None,
        activeSize: str | None = None,
        placement: str | None = None,
        fullWidth: bool | None = None,
        url: str | None = None,
        scaleMode: str | None = None,
        propStyle: dict | None = None,
        readOnly: bool | None = None,
        marks: dict[str, dict[str, str]] | None = None,
        trailingZeros: bool | None = None,
        locale: str | None = None,
        fallbackValue: str | None = None,
        draggable: bool | None = None,
        allowNone: bool | None = None,
        **kwargs,
    ):
        """
        Arguments:

        * **`name`**: `[str]` &rarr; The name of the prop.
        * **`type`**: `[str]` &rarr; The type of the prop.
            * **Accepted Values**:
                * `"head"`: A header for an individual section, containing a `title` and a `help` message
                * `"num"`: A numeric input field
                * `"toggle"`: A switch button to enable or disable a single setting
                * `"button"`: A regular button
                * `"text"`: A text input field
                * `"selector"`: Select options from a set
                * `"date"`: Select a date and/or time
                * `"media"`: View various media formats
                    * Note: A variant is required when using the `media` type
                * `"coordinate"`: A coordinate input field
        * **`subtitle`**: `[str]` = `None` &rarr; An optional subtitle for the prop.
        * **`help`**: `[str]` = `None` &rarr; The help text to display.
            * **Notes**:
                - This is displayed when the user clicks on the help icon next to the prop.
                - This can be regular text or markdown.
        * **`helperText`**: `[str]` = `None` &rarr; Additional help text to display below the prop without requiring a click on the help icon.
        * **`display`**: `[bool]` = `None` &rarr; Whether or not the prop will be displayed.
        * **`variant`**: `[str]` = `None` &rarr; The variant of the prop.
            * **Accepted Values**:
                * When **`type`** == `"head"`:
                    * `"column"`: A header for a column of related prop items
                    * `"row"`: A header for a row of related prop items
                    * `"icon"`: Same as `"column"`, accompanied by a related icon.
                    * `"iconRow"`: Same as `"row"`, accompanied by a related icon.
                * When **`type`** == `"text"`:
                    * `"single"`: A single-line text input field
                    * `"textarea"`: A multi-line text input field
                * When **`type`** == `"num"`:
                    * `"field"`: A numeric input field
                    * `"slider"`: A range of values along a bar, from which users may select a single value
                    * `"icon"`: A fixed numerical value presented alongside a corresponding icon.
                    * `"iconCompact"`: Similar to `"icon"`, but designed in a compact format for appropriate rendering within a draggable pad.
                    * `"incslider"`: A range of values along a bar, from which users may select a single value, with a predefined set of options.
                * When **`type`** == `"selector"`:
                    * `"checkbox"`: Select one or more items from a set of checkboxes
                    * `"combobox"`: A dropdown with a search bar allowing users to filter and select a single option by typing
                    * `"comboboxMulti"`: A dropdown with a search bar, enabling users to filter and select multiple options. Selected items are displayed as tags within the input field.
                    * `"dropdown"`: Show multiple options that appear when the element is clicked
                    * `"nested"`: Select one or more options from a set of nested checkboxes
                    * `"radio"`: Select one option from a set of mutually exclusive options
                    * `"hradio"`: A set of `"radio"`s placed horizontally
                    * `"hstepper"`: Select a unique option along a horizontal slider
                    * `"vstepper"`: Select a unique option along a vertical slider
                * When **`type`** == `"date"`:
                    * `"date"`: Select a date via a calendar pop-up that appears when the element is clicked (default)
                        * **Note**: Passed as `YYYY-MM-DD`
                    * `"time"`: Select a time via a clock pop-up that appears when the element is clicked
                        * **Note**: Passed as `HH:MM:SS`
                    * `"datetime"`: Select date and time via a pop-up with calendar and clock tabs that appear when the element is clicked
                        * **Note**: Passed as `YYYY-MM-DDTHH:MM:SS`
                * When **`type`** == `"media"`:
                    * `"picture"`: Show a PNG or JPG image
                    * `"video"`: Display a YouTube, Vimeo, or Dailymotion video clip
                * When **`type`** == `"coordinate"`:
                    * `"latLngInput"`: A latitude and longitude input field
                    * `"latLngMap"`: A clickable map to select a latitude and longitude
                    * `"latLngPath"`: A clickable map to select a path of latitude and longitude points
        * **`container`**: `[str]` = `"vertical"` | `"none"` &rarr;
            * Specifies the type of prop container by selecting from predefined styles.
            * **Accepted Values**:
                * `"vertical"`: A vertical layout where the prop `name` appears at the top inside the container.
                * `"horizontal"`: A horizontal layout where the prop `name` is on the left, followed by the actionable prop on the right.
                * `"titled"`: Similar to the vertical container but without a background color, removing the embossed appearance of the prop.
                * `"untitled"`: A slim container version without the prop `name` or `unit` label.
                * `"none"`: Removes the prop container entirely, disabling the display of the prop `name`, `help` button and `unit` label. Only the actionable prop is displayed.
            * **Notes**:
                * This attribute applies to all props except the `"icon"` and `"iconCompact"` variants of the `"num"` prop.
                * If left unspecified (i.e., `None`), the default is `"none"` for `"head"` props, and `"vertical"` for all others. As stated, the `"icon"` and `"iconCompact"` variants of the `"num"` prop are always set to `"none"`, regardless of this attribute.
                * When the container is set to `"none"`, the `style` prop used at the `"item"` level of the `layout` becomes ineffective.
        * **`enabled`**: `[bool]` = `True` &rarr; Whether or not the prop will be enabled.
            * **Note**: This attribute applies to all props except `"head"` props.
        * **`apiCommand`**: `[str]` = `None` &rarr; The name of the API command to trigger.
            * **Note**: If `None`, no `apiCommand` is triggered.
            * **Note**: This attribute applies to all props except `"head"` props.
        * **`apiCommandKeys`**: `[list[str]]` = `None` &rarr;
            * The root API keys to pass to your `execute_command` function if an `apiCommand` is provided.
            * **Note**: If `None`, all API keys are passed to your `execute_command`.
            * **Note**: This attribute applies to all props except `"head"` props.
        * **`icon`**: `[str]` = `None` &rarr; The icon to use for the prop.
            * **Notes**:
                * It must be a valid icon name from the [react-icons][] bundle, preceded by the abbreviated name of the icon library source.
                * This attribute applies exclusively to `"head"` props.
        * **`options`**: `[dict]` = `None` &rarr;
            * The options to be displayed on the UI element mapped to their display properties.
            * **Notes**:
                * Only options provided here are valid for the prop value
                * This attribute applies to only `"selector"` props
        * **`numVisibleTags`**: `[int]` = `None` &rarr;
            * The maximum number of tags visible in a `"comboboxMulti"` variant of a `"selector"` prop when it is not focused.
            * **Notes**:
                * If `None`, all tags will be displayed
                * This attribute applies exclusively to `"selector"` props using the `"comboboxMulti"` variant
        * **`valueOptions`**: `[list[int|float]]` = `None` &rarr;
            * **Notes**:
                * Only valueOptions provided here can be selected for the prop value
                * This attribute applies to `"num"` props with the `"incslider"` variant.
        * **`label`**: `[str]` = `None` &rarr; The label to display above the input field when the prop is focused.
            * **Note**: This attribute applies to `"num"`, `"text"`, and `"coordinate"` props.
        * **`labelPlacement`**: `[str]` = `None` &rarr; The placement of the label relative to the input field.
            * **Accepted Values**: ['start', 'end', "top", "bottom"]
        * **`activeLabel`**: `[str]` = `None` &rarr; The label to display when the prop value is True.
            * **Notes**: This attribute applies exclusively to `"toggle"` props.
        * **`placeholder`**: `[str]` = `None` &rarr; The placeholder text to display.
            * **Note**: This attribute applies exclusively to `"text"` props.
        * **`maxValue`**: `[float | int]` = `None` &rarr; The maximum value for the prop.
            * **Note**: This attribute applies exclusively to `"num"` props.
        * **`minValue`**: `[float | int]` = `None` &rarr; The minimum value for the prop.
            * **Note**: This attribute applies exclusively to `"num"` props.
        * **`gradient`**: `[dict]` = `None` &rarr; The gradient to apply to the prop.
            * **Note**: See the `props_gradient` function for more information.
        * **`fallback`**: `[dict]` = `None` &rarr; The fallback dict for color and sizing props with missing or invalid values.
            * **Note**: See the `props_fallback` function for more information.
        * **`maxRows`**: `[int]` = `None` &rarr;
            * The maximum number of rows to show for a `"textarea"` variant.
            * **Note**: This attribute applies exclusively to `"text"` props.
        * **`minRows`**: `[int]` = `None` &rarr;
            * The minimum number of rows to show for a `"textarea"` variant.
            * **Note**: This attribute applies exclusively to `"text"` props.
        * **`rows`**: `[int]` = `None` &rarr;
            * The fixed number of rows to show for a `"textarea"` variant.
            * **Note**: This attribute applies exclusively to `"text"` props.
        * **`views`**: `[list[str]]` &rarr;
            * The available time units for the represented date and/or time.
            * **Default Value**:
                * When **`variant`** == `"date"`: `["year", "day"]`
                * When **`variant`** == `"time"`: `["hours", "minutes"]`
                * When **`variant`** == `"datetime"`: `["year", "day", "hours", "minutes"]`
            * **Accepted Values**:
                * When **`variant`** == `"date"`:
                    * `"year"`: The year view
                    * `"month"`: The month view
                    * `"day"`: The day view
                * When **`variant`** == `"time"`:
                    * `"hours"`: The hours view
                    * `"minutes"`: The minutes view
                    * `"seconds"`: The seconds view
                * When **`variant`** == `"datetime"`:
                    * `"year"`: The year view
                    * `"month"`: The month view
                    * `"day"`: The day view
                    * `"hours"`: The hours view
                    * `"minutes"`: The minutes view
                    * `"seconds"`: The seconds view
            * **Notes**:
                * The views will be presented in the order specified in the `views` array.
                * This attribute applies exclusively to `"date"` props.
        * **`locale`**: `[str]` = `None` &rarr;
            * Format numeric values based on language and regional conventions.
            * **Notes**:
                * If left unspecified (i.e., `None`), it will default to `settings.defaults.locale`.
                * This attribute applies exclusively to `"num"` props.
            * **See**: [Locale identifier][].
        * **`precision`**: `[int]` = `None` &rarr; The number of decimal places to display.
            * **Notes**:
                * Set the precision to `0` to attach an integer constraint.
                * If left unspecified (i.e., `None`), it will default to `settings.defaults.precision`.
                * This attribute applies exclusively to `"num"` props.
        * **`trailingZeros`**: `[bool]` = `None` &rarr; If `True`, trailing zeros will be displayed.
            * **Notes**:
                * This ensures that all precision digits are shown. For example: `1.5` &rarr; `1.500` when precision is `3`.
                * If left unspecified (i.e., `None`), it will default to `settings.defaults.trailingZeros`.
                * This attribute applies exclusively to `"num"` props.
        * **`fallbackValue`**: [str] = `None` &rarr; A value to show when the value is missing or invalid.
            * **Notes**:
                * This is only for display purposes as related to number formatting. It does not affect the actual value or any computations.
                    * For example, if the value passed is `None`, the fallback value will be displayed instead.
                * If left unspecified (i.e., `None`), it will default to `settings.defaults.fallbackValue`.
                * This attribute applies exclusively to `"num"` props.
        * **`unit`**: `[str]` = `None` &rarr; The unit to use for the prop.
            * **Notes**:
                * If left unspecified (i.e., `None`), it will default to `settings.defaults.unit`.
                * This attribute applies exclusively to `"num"` props.
        * **`unitPlacement`**: `[str]` = `None` &rarr; The position of the `unit` symbol relative to the value.
            * **Accepted Values**:
                * `"after"`: The `unit` appears after the value.
                * `"afterWithSpace"`: The `unit` appears after the value, separated by a space.
                * `"before"`: The `unit` appears before the value.
                * `"beforeWithSpace"`: The unit is placed before the value, with a space in between.
            * **Notes**:
                * If left unspecified (i.e., `None`), it will default to `settings.defaults.unitPlacement`.
                * This attribute applies exclusively to `"num"` props.
        * **`notation`**: `[str]` = `"standard"` &rarr; The formatting style of a numeric value.
            * **Accepted Values**:
                * `"standard"`: Plain number formatting
                * `"compact"`: Resembles the [metric prefix][] system
                * `"scientific"`: [Scientific notation][]
                * `"engineering"`: [Engineering notation][]
                * `"precision"`: Emulates the [Number.prototype.toPrecision][] method
            * **Notes**:
                * If left unspecified (i.e., `None`), it will default to `settings.defaults.notation`.
                * This attribute applies exclusively to `"num"` props.
        * **`notationDisplay`**: `[str]` = `"e+"` | `"short"` &rarr; Further customize the formatting within the selected `notation`.
            * **Accepted Values**:
                * When **`notation`** == `"compact"`:
                    * `"short"`: Add symbols `K`, `M`, `B`, and `T` (in `"en-US"`) to denote thousands, millions, billions, and trillions, respectively.
                    * `"long"`: Present numeric values with the informal suffix words `thousand`, `million`, `billion`, and `trillion` (in `"en-US"`).
                * When **`notation`** == `"scientific"`, `"engineering"` or `"precision"`:
                    * `"e"`: Exponent symbol in lowercase as per the chosen `locale` identifier
                    * `"e+"`: Similar to `"e"`, but with a plus sign for positive exponents.
                    * `"E"`: Exponent symbol in uppercase as per the chosen `locale` identifier
                    * `"E+"`: Similar to `"E"`, but with a plus sign for positive exponents.
                    * `"x10^"`: Formal scientific notation representation
                    * `"x10^+"`: Similar to `"x10^"`, with a plus sign for positive exponents.
                * When **`notation`** == `"standard"`:
                    * No `notationDisplay` option is allowed for a `"standard"` notation
            * **Notes**:
                * No `notationDisplay` option is provided for a `"standard"` notation
                * The options `"short"` and `"long"` are only provided for the `"compact"` notation
                * The options `"e"`, `"e+"`, `"E"`, `"E+"`, `"x10^"`, and `"x10^+"` are provided for the `"scientific"`, `"engineering"` and `"precision"` notations
                * If left unspecified (i.e., `None`), it will default to `settings.defaults.notationDisplay`.
                * This attribute applies exclusively to `"num"` props.
        * **`legendPrecision`**: `[int]` = `None` &rarr;
            * The number of decimal places to display in the Map Legend.
            * **Notes**:
                * Set the precision to `0` to attach an integer constraint.
                * If left unspecified (i.e., `None`), it will default to `settings.defaults.legendPrecision`.
                * This attribute applies exclusively to `"num"` props.
        * **`legendNotation`**: `[str]` = `"standard"` &rarr; The formatting style of a numeric value.
            * **Accepted Values**:
                * `"standard"`: Plain number formatting
                * `"compact"`: Resembles the [metric prefix][] system
                * `"scientific"`: [Scientific notation][]
                * `"engineering"`: [Engineering notation][]
                * `"precision"`: Emulates the [Number.prototype.toPrecision][] method
            * **Notes**:
                * If left unspecified (i.e., `None`), it will default to `settings.defaults.legendNotation`.
                * This attribute applies exclusively to `"num"` props.
        * **`legendNotationDisplay`**: `[str]` = `"e+"` | `"short"` &rarr; Further customize the formatting within the selected `legendNotation`.
            * **Accepted Values**:
                * `"short"`: Add symbols `K`, `M`, `B`, and `T` (in `"en-US"`) to denote thousands, millions, billions, and trillions, respectively.
                * `"long"`: Present numeric values with the informal suffix words `thousand`, `million`, `billion`, and `trillion` (in `"en-US"`).
                * `"e"`: Exponent symbol in lowercase as per the chosen `locale` identifier
                * `"e+"`: Similar to `"e"`, but with a plus sign for positive exponents.
                * `"E"`: Exponent symbol in uppercase as per the chosen `locale` identifier
                * `"E+"`: Similar to `"E"`, but with a plus sign for positive exponents.
                * `"x10^"`: Formal scientific notation representation
                * `"x10^+"`: Similar to `"x10^"`, with a plus sign for positive exponents.
            * **Notes**:
                * No `legendNotationDisplay` option is provided for a `"standard"` legend notation
                * The options `"short"` and `"long"` are only provided for the `"compact"` legend notation
                * The options `"e"`, `"e+"`, `"E"`, `"E+"`, `"x10^"`, and `"x10^+"` are provided for the `"scientific"`, `"engineering"` and `"precision"` notations
                * If left unspecified (i.e., `None`), it will default to `settings.defaults.legendNotationDisplay`.
                * This attribute applies exclusively to `"num"` props.
        * **`legendMinLabel`**: `[str]` = `None` &rarr;
            * A custom and descriptive label in the Map Legend used to identify the lowest data point.
            * **Notes**:
                * Takes precedence over other formatting, except when used in a node cluster and the `cave_utils.api.maps.group` attribute is `True`. In this case, the min value within the node cluster is displayed.
                * If left unspecified (i.e., `None`), it will default to `settings.defaults.legendMinLabel`.
                * This attribute applies exclusively to `"num"` props.
        * **`legendMaxLabel`**: `[str]` = `None` &rarr;
            * A custom and descriptive label in the Map Legend used to identify the highest data point.
            * **Notes**:
                * Takes precedence over other formatting, except when used in a node cluster and the `cave_utils.api.maps.group` attribute is `True`. In this case, the max value within the node cluster is displayed.
                * If left unspecified (i.e., `None`), it will default to `settings.defaults.legendMaxLabel`.
                * This attribute applies exclusively to `"num"` props.
        * **`icon`**: `[str]` = `None` &rarr; The icon to use for the prop.
            * **Notes**: Applies to the `icon` variants of various props and also `toggle` and `button` props.
        * **`activeIcon`**: `[str]` = `None` &rarr; The icon to use for the prop when it is active.
            * **Notes**: Applies to the `toggle` and `selector` props.
        * **`startIcon`**: `[str]` = `None` &rarr; The icon to display at the start of the prop.
            * **Notes**: Applies to the `button` prop and offers a way to add an icon to the left side of the button.
        * **`endIcon`**: `[str]` = `None` &rarr; The icon to display at the end of the prop.
            * **Notes**: Applies to the `button` prop and offers a way to add an icon to the right side of the button.
        * **`color`**: `[str]` = `None` &rarr; The color to use for the prop.
            * **Notes**: Applies to the `icon` variants of various props and also `toggle` and `button` props.
        * **`activeColor`**: `[str]` = `None` &rarr; The color to use for the prop when it is active.
            * **Notes**: Applies to the `toggle` and `selector` props.
        * **`size`**: `[str]` = `None` &rarr; The size of the icon in the prop.
            * **Notes**: Applies to the `icon` variants of various props and also `toggle` and `button` props.
        * **`activeSize`**: `[str]` = `None` &rarr; The size of the icon in the prop when it is active.
            * **Notes**: Applies to the `toggle` and `selector` props.
        * **`placement`**: `[str]` = `None` &rarr; The placement of the prop.
            * **Accepted Values**:
                * `"start"`: The prop is placed at the start of the container.
                * `"end"`: The prop is placed at the end of the container.
                * `"top"`: The prop is placed at the top of the container.
                * `"bottom"`: The prop is placed at the bottom of the container.
                * `"center"`: The prop is placed at the center of the container.
        * **`fullWidth`**: `[bool]` = `None` &rarr; Whether or not the prop should take the full width of the container.
        * **`url`**: `[str]` = `None` &rarr; The URL to navigate to when the button is clicked.
            * **Notes**: Applies to `button` props.
        * **`scaleMode`**: `[str]` = `None` &rarr; The scale mode to use for the prop.
            * **Accepted Values**: ['fitWidth', 'fitHeight', 'fitContainer']
            * **Notes**: Applies only to `media` props with a `variant` of `video`.
        * **`propStyle`**: `[dict]` = `None` &rarr; A dictionary of css styles to apply to the prop.
            * **Note**: This will not be validated as part of the API spec, so use with caution.
        * **`readOnly`**: `[bool]` = `False` &rarr; Whether or not the prop is read-only.
            * **Notes**:
                - Only applies to 'text' props.
                - Essentially operates an enabled without making the prop darkened.
        * **`marks`**: `[dict[str, dict[str, str]]]` = `None` &rarr; A dictionary of marks to display on the slider.
            * **Notes**:
                - Only applies to `"num"` props with the `"incslider"` variant.
                - Contains key-value pairs for each mark, where the key is the mark value and the value is a dictionary of properties for the mark (e.g., label, color).
                - TODO: Add more details and validation for the `marks` dictionary.
        * **`draggable`**: `[bool]` = `None` &rarr;
            * If `True`, the prop will be rendered within the draggable global outputs pad.
            * **Notes**:
                * The prop's `variant` is enforced to `iconCompact` to accommodate it within the draggable pad.
                * This attribute applies exclusively to `"num"` props defined within `cave_utils.api.globalOutputs`.
        * **`allowNone`**: `[bool]` = `False` &rarr;
            * Whether or not to allow `None` as a valid value for the prop. This is primarily used to help when validating `values` and `valueLists`.
            * **Notes**:
                * If `True`, `None` will be a valid value for the prop.
                    * `None` values will be treated differently in the front end
                        * For map display purposes: `None` values will be shown as a different color or ignored.
                            * See `nullColor` in: `/cave_utils/cave_utils/api/maps.html#colorByOptions`
                        * For prop purposes: `None` values will be left blank.
                * If `False`, `None` will not be a valid value for the prop.
                * This attribute applies to all props except `"head"` props.

        [react-icons]: https://react-icons.github.io/react-icons/search
        [metric prefix]: https://en.wikipedia.org/wiki/Metric_prefix
        [Scientific notation]: https://en.wikipedia.org/wiki/Scientific_notation
        [Engineering notation]: https://en.wikipedia.org/wiki/Engineering_notation
        [Number.prototype.toPrecision]: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/toPrecision
        """
        passed_values = {k: v for k, v in locals().items() if (v is not None) and k != "kwargs"}
        required_fields = ["name", "type"]
        optional_fields = [
            "subtitle",
            "help",
            "helperText",
            "variant",
            "display",
            "container",
            "propStyle",
            "fullWidth",
            "placement",
            "labelPlacement",
        ]
        if type == "head":
            if variant == "icon" or variant == "iconRow":
                required_fields += ["icon"]
                optional_fields += ["color", "size"]
        else:
            optional_fields += ["enabled", "apiCommand", "apiCommandKeys", "allowNone"]

        if type == "text":
            optional_fields += [
                "minRows",
                "maxRows",
                "rows",
                "label",
                "placeholder",
                "options",
                "readOnly",
            ]
        elif type == "num":
            optional_fields += ["color"]
            if variant == "slider":
                required_fields += ["maxValue", "minValue"]
            elif variant == "incslider":
                required_fields += ["valueOptions"]
                optional_fields += ["marks"]
            else:
                optional_fields += ["maxValue", "minValue"]
                if variant is None or variant == "field":
                    optional_fields += ["label", "placeholder"]
            if variant == "icon" or variant == "iconCompact":
                required_fields += ["icon"]
                optional_fields += ["color", "size"]
            if notationDisplay:
                required_fields += ["notation"]
            if legendNotationDisplay:
                required_fields += ["legendNotation"]
            optional_fields += [
                "unit",
                "notation",
                "precision",
                "notationDisplay",
                "legendNotation",
                "legendPrecision",
                "legendNotationDisplay",
                "legendMinLabel",
                "legendMaxLabel",
                "trailingZeros",
                "unitPlacement",
                "draggable",
                "gradient",
            ]
        elif type == "selector":
            required_fields += ["options"]
            optional_fields += [
                "placeholder",
                "color",
                "activeColor",
                "size",
                "activeSize",
                "icon",
                "activeIcon",
            ]
            if variant == "comboboxMulti":
                optional_fields += ["numVisibleTags"]
        elif type == "date":
            optional_fields += ["views"]
        elif type == "coordinate":
            optional_fields += ["label", "placeholder", "precision"]
        elif type == "toggle":
            optional_fields += [
                "options",
                "icon",
                "color",
                "size",
                "label",
                "activeColor",
                "activeSize",
                "activeLabel",
                "activeIcon",
            ]
        elif type == "button":
            optional_fields += ["icon", "color", "size", "startIcon", "endIcon", "url"]
        elif type == "media":
            required_fields += ["variant"]
            optional_fields = [i for i in optional_fields if i != "variant"]
            if variant == "video":
                optional_fields += ["scaleMode"]
        if type in ["selector", "num", "toggle", "text"]:
            optional_fields += ["fallback"]

        missing_required = pamda.difference(required_fields, list(passed_values.keys()))
        if len(missing_required) > 0:
            raise Exception(f"Missing required fields: {str(missing_required)}")

        for k, v in passed_values.items():
            if k not in required_fields + optional_fields:
                kwargs[k] = v
        notationDisplay_options_dict = {
            "compact": ["short", "long"],
            "scientific": ["e", "e+", "E", "E+", "x10^", "x10^+"],
            "engineering": ["e", "e+", "E", "E+", "x10^", "x10^+"],
            "precision": ["e", "e+", "E", "E+", "x10^", "x10^+"],
            "standard": [],
        }
        notation = passed_values.get("notation", "standard")
        legendNotation = passed_values.get("legendNotation", "standard")
        view_options_dict = {
            "date": ["year", "month", "day"],
            "time": ["hours", "minutes", "seconds"],
            "datetime": ["year", "month", "day", "hours", "minutes", "seconds"],
        }
        variant = passed_values.get("variant", None)
        return {
            "kwargs": kwargs,
            "accepted_values": {
                "type": [
                    "head",
                    "num",
                    "toggle",
                    "button",
                    "text",
                    "selector",
                    "date",
                    "media",
                    "coordinate",
                ],
                "container": ["vertical", "horizontal", "titled", "untitled", "none"],
                "views": view_options_dict.get(variant, []),
                "unitPlacement": ["after", "afterWithSpace", "before", "beforeWithSpace"],
                "notation": ["standard", "compact", "scientific", "engineering", "precision"],
                "notationDisplay": notationDisplay_options_dict.get(notation, []),
                "legendNotation": ["standard", "compact", "scientific", "engineering", "precision"],
                "legendNotationDisplay": notationDisplay_options_dict.get(legendNotation, []),
                "placement": [
                    "topLeft",
                    "topCenter",
                    "topRight",
                    "left",
                    "center",
                    "right",
                    "bottomLeft",
                    "bottomCenter",
                    "bottomRight",
                ],
                "variant": {
                    "head": ["column", "row", "icon", "iconRow"],
                    "text": ["single", "textarea"],
                    "num": ["field", "slider", "icon", "iconCompact", "incslider"],
                    "selector": [
                        "dropdown",
                        "checkbox",
                        "radio",
                        "combobox",
                        "comboboxMulti",
                        "hstepper",
                        "vstepper",
                        "hradio",
                        "hcheckbox",
                        "nested",
                    ],
                    "date": ["date", "time", "datetime"],
                    "media": ["picture", "video"],
                    "coordinate": ["latLngInput", "latLngMap", "latLngPath"],
                    "toggle": ["switch", "button", "checkbox"],
                    "button": ["outlined", "text", "icon", "filled"],
                }.get(type, []),
            },
        }

    def __extend_spec__(self, **kwargs):
        if self.data.get("type") == "selector":
            CustomKeyValidator(
                data=self.data.get("options", {}),
                log=self.log,
                prepend_path=["options"],
                validator=props_options,
                variant=self.data.get("variant"),
                **kwargs,
            )
        if self.data.get("gradient"):
            props_gradient(
                data=self.data.get("gradient"), log=self.log, prepend_path=["gradient"], **kwargs
            )
        if self.data.get("fallback"):
            props_fallback(
                data=self.data.get("fallback"), log=self.log, prepend_path=["fallback"], **kwargs
            )
        if self.data.get("color"):
            self.__check_color_string_valid__(color_string=self.data.get("color"))
        if self.data.get("activeColor"):
            self.__check_color_string_valid__(color_string=self.data.get("activeColor"))
        if self.data.get("size"):
            self.__check_pixel_string_valid__(pixel_string=self.data.get("size"))
        if self.data.get("activeSize"):
            self.__check_pixel_string_valid__(pixel_string=self.data.get("activeSize"))


@type_enforced.Enforcer
class props_options(ApiValidator):
    @staticmethod
    def spec(
        name: str,
        activeName: str | None = None,
        path: list[str] | None = None,
        help: str | None = None,
        helperText: str | None = None,
        color: str | None = None,
        activeColor: str | None = None,
        size: str | None = None,
        activeSize: str | None = None,
        icon: str | None = None,
        activeIcon: str | None = None,
        enabled: bool | None = True,
        **kwargs,
    ):
        """
        Arguments:

        * **`name`**: `[str]` &rarr; The name of the option.
        * **`activeName`**: `[str]` = `None` &rarr; The name of the option when it is active.
            * **Note**: If not set, the `name` will be used regardless of the active state.
        * **`path`**: `[list[str]]` = `None` &rarr; The path to an option.
            * **Notes**:
                * If `None`, the option will not be selectable
                * This attribute applies exclusively to `"nested"` props
        * **`help`**: `[str]` = `None` &rarr; The help text to display for this option.
            * **Note**: This can be raw text or markdown formatted text.
        * **`helperText`**: `[str]` = `None` &rarr; The helper text to display for this option.
        * **`color`**: `[str]` = `None` &rarr; The color to use for this option.
            * **Note**: A valid color string (EG: "RGBA(0,0,0,1)")
        * **`activeColor`**: `[str]` = `None` &rarr; The color to use for this option when it is active.
            * **Note**: If not set the `color` will be used regardless of the active state.
        * **`size`**: `[str]` = `None` &rarr; The size to use for this option.
            * **Note**: A valid size string (EG: "5px")
        * **`activeSize`**: `[str]` = `None` &rarr; The size to use for this option when it is active.
            * **Note**: If not set the `size` will be used regardless of the active state.
        * **`icon`**: `[str]` = `None` &rarr; The icon to use for this option.
        * **`activeIcon`**: `[str]` = `None` &rarr; The icon to use for this option when it is active.
            * **Note**: If not set the `icon` will be used regardless of the active state.
        * **`enabled`**: `[bool]` = `True` &rarr; Whether or not the option will be enabled.
        """
        variant = kwargs.get("variant")
        kwargs = {k: v for k, v in kwargs.items() if k != "variant"}
        if variant == "nested":
            if path is None:
                raise Exception("Must provide a path for nested options")
        return {
            "kwargs": kwargs,
            "accepted_values": {},
        }

    def __extend_spec__(self, **kwargs):
        if kwargs.get("variant") == "nested":
            if not isinstance(self.data.get("path"), list):
                self.__error__(
                    msg="`path` must be specified and a list of strings for nested options"
                )
                return
        if self.data.get("color"):
            self.__check_color_string_valid__(color_string=self.data.get("color"))
        if self.data.get("activeColor"):
            self.__check_color_string_valid__(color_string=self.data.get("activeColor"))
        if self.data.get("size"):
            self.__check_pixel_string_valid__(pixel_string=self.data.get("size"))
        if self.data.get("activeSize"):
            self.__check_pixel_string_valid__(pixel_string=self.data.get("activeSize"))


@type_enforced.Enforcer
class props_fallback(ApiValidator):
    @staticmethod
    def spec(
        name: str | None = None,
        color: str | None = None,
        size: str | None = None,
        **kwargs,
    ):
        """
        Arguments:

        * **`name`**: `[str]` = `None` &rarr; The name of the fallback.
        * **`color`**: `[str]` = `None` &rarr; The color to use for this fallback.
            * **Note**: A valid color string (EG: "RGBA(0,0,0,1)")
        * **`size`**: `[str]` = `None` &rarr; The size to use for this fallback.
            * **Note**: A valid size string (EG: "5px")
        """
        return {
            "kwargs": kwargs,
            "accepted_values": {},
        }

    def __extend_spec__(self, **kwargs):
        if self.data.get("color"):
            self.__check_color_string_valid__(color_string=self.data.get("color"))
        if self.data.get("size"):
            self.__check_pixel_string_valid__(pixel_string=self.data.get("size"))


@type_enforced.Enforcer
class props_gradient(ApiValidator):
    @staticmethod
    def spec(
        scale: str | None = None,
        scaleParams: dict | None = None,
        notation: str | None = None,
        notationDisplay: str | None = None,
        precision: int | None = None,
        data: list | None = None,
        **kwargs,
    ):
        """
        Arguments:

        * **`scale`**: `[str]` = `None` &rarr; The scale to use for the gradient.
            * **Accepted Values**:
                * `"linear"`: A linear gradient
                * `"log"`: A logarithmic gradient
                * `"pow"`: A power gradient
                * `"step"`: A step gradient
        * **`scaleParams`**: `[dict]` = `None` &rarr; The parameters for the scale.
            * **Note**: See `props_gradient_scaleParams` for more information.
        * **`notation`**: `[str]` = `None` &rarr; The notation to use for the gradient.
            * **Accepted Values**:
                * `"standard"`: Plain number formatting
                * `"compact"`: Resembles the [metric prefix][] system
                * `"scientific"`: [Scientific notation][]
                * `"engineering"`: [Engineering notation][]
                * `"precision"`: Emulates the [Number.prototype.toPrecision][] method
        * **`notationDisplay`**: `[str]` = `"e+"` | `"short"` &rarr; Further customize the formatting within the selected `notation` when shown next to the gradient.
            * **Accepted Values**:
                * When **`notation`** == `"compact"`:
                    * `"short"`: Add symbols `K`, `M`, `B`, and `T` (in `"en-US"`) to denote thousands, millions, billions, and trillions, respectively.
                    * `"long"`: Present numeric values with the informal suffix words `thousand`, `million`, `billion`, and `trillion` (in `"en-US"`).
                * When **`notation`** == `"scientific"`, `"engineering"` or `"precision"`:
                    * `"e"`: Exponent symbol in lowercase as per the chosen `locale` identifier
                    * `"e+"`: Similar to `"e"`, but with a plus sign for positive exponents.
                    * `"E"`: Exponent symbol in uppercase as per the chosen `locale` identifier
                    * `"E+"`: Similar to `"E"`, but with a plus sign for positive exponents.
                    * `"x10^"`: Formal scientific notation representation
                    * `"x10^+"`: Similar to `"x10^"`, with a plus sign for positive exponents.
                * When **`notation`** == `"standard"`:
                    * No `notationDisplay` option is allowed for a `"standard"` notation
            * **Notes**:
                * If left unspecified (i.e., `None`), it will default to `settings.defaults.notationDisplay`.
        * **`precision`**: `[int]` = `None` &rarr; The number of decimal places to display next to the gradient.
        * **`data`**: `[list]` = `None` &rarr; The data for the gradient as a list of dicts.
            * **Note**: See `props_gradient_data` for more information.
        """
        notationDisplay_options_dict = {
            "compact": ["short", "long"],
            "scientific": ["e", "e+", "E", "E+", "x10^", "x10^+"],
            "engineering": ["e", "e+", "E", "E+", "x10^", "x10^+"],
            "precision": ["e", "e+", "E", "E+", "x10^", "x10^+"],
            "standard": [],
        }
        return {
            "kwargs": kwargs,
            "accepted_values": {
                "scale": ["linear", "log", "pow", "step"],
                "notation": ["standard", "compact", "scientific", "engineering", "precision"],
                "notationDisplay": notationDisplay_options_dict.get(notation, []),
                "notation": ["standard", "compact", "scientific", "engineering", "precision"],
            },
        }

    def __extend_spec__(self, **kwargs):
        props_gradient_scaleParams(
            data=self.data.get("scaleParams", {}),
            log=self.log,
            prepend_path=["scaleParams"],
            gradient_scale_type=self.data.get("scale"),
        )
        if self.data.get("data"):
            for idx, gradient_data in enumerate(self.data.get("data")):
                props_gradient_data(
                    data=gradient_data,
                    log=self.log,
                    prepend_path=["data", idx],
                    **kwargs,
                )


@type_enforced.Enforcer
class props_gradient_scaleParams(ApiValidator):
    @staticmethod
    def spec(
        exponent: float | int | None = None,
        **kwargs,
    ):
        """
        Arguments:

        * **`exponent`**: `[float | int]` = `None` &rarr; The exponent for the scale if using a power gradient.
        """
        return {
            "kwargs": kwargs,
            "accepted_values": {},
        }

    def __extend_spec__(self, **kwargs):
        if self.data.get("exponent") is not None:
            if self.data.get("exponent") <= 0:
                self.__error__(msg="`exponent` must be greater than 0 for a power gradient")
        if kwargs.get("gradient_scale_type") == "pow":
            if not self.data.get("exponent"):
                self.__error__(msg="`exponent` must be specified for a power gradient")


@type_enforced.Enforcer
class props_gradient_data(ApiValidator):
    @staticmethod
    def spec(
        value: int | float | str,
        color: str | None = None,
        size: str | None = None,
        label: str | None = None,
        **kwargs,
    ):
        """
        Arguments:

        * **`value`**: `[int | float | str]` &rarr; The value for the split point in the gradient.
        * **`color`**: `[str]` = `None` &rarr; The color string to use for the split point.
            * **Note**: A valid color string (EG: "RGBA(0,0,0,1)")
        * **`size`**: `[str]` = `None` &rarr; The size string to use for the split point.
            * **Note**: A valid size string (EG: "5px")
        * **`label`**: `[str]` = `None` &rarr; The label to use for the split point.
        """
        accepted_values = {}
        if isinstance(value, str):
            accepted_values = {
                "value": ["min", "max"],
            }
        return {
            "kwargs": kwargs,
            "accepted_values": accepted_values,
        }

    def __extend_spec__(self, **kwargs):
        if self.data.get("color"):
            self.__check_color_string_valid__(color_string=self.data.get("color"))
        if self.data.get("size"):
            self.__check_pixel_string_valid__(pixel_string=self.data.get("size"))


@type_enforced.Enforcer
class layout(ApiValidator):
    @staticmethod
    def spec(
        type: str,
        numColumns: str | int | None = None,
        numRows: str | int | None = None,
        data: dict | None = None,
        itemId: str | None = None,
        column: int | None = None,
        row: int | None = None,
        style: dict | None = None,
        **kwargs,
    ):
        """
        Arguments:

        * **`type`**: `[str]` = `None` &rarr; The type of the layout.
            * **Accepted Values**:
                * `"grid"`: A layout element that can contain other layout elements.
                * `"item"`: A layout element where a prop is located.
        * **`numColumns`**: `[str | int]` = `"auto"` &rarr; The number of columns for the grid layout.
            * **Notes**:
                * If `"auto"`, the number of columns will be calculated based on the number of items.
                * This attribute applies exclusively to `"grid"` layouts.
        * **`numRows`**: `[str | int]` = `"auto"` &rarr; The number of rows for the grid layout.
            * **Notes**:
                * If `"auto"`, the number of rows will be calculated based on the number of items.
                * This attribute applies exclusively to `"grid"` layouts.
        * **`data`**: `[dict]` = `None` &rarr; The data for the layout.
            * **Note**: This attribute applies exclusively to `"grid"` layouts.
        * **`itemId`**: `[str]` = `None` &rarr; The id of the prop placed in the layout
            * **Note**: This attribute applies exclusively to `"item"` layouts.
        * **`column`**: `[int]` = `None` &rarr; The column in which to place the prop in the current grid.
        * **`row`**: `[int]` = `None` &rarr; The row in which to place the prop in the current grid.
        * **`style`**: `[dict | None]` = `None` &rarr; Provides an escape hatch for specifying CSS rules.
            * **Note**: In `"item"` layouts, the `style` is applied to the root of the prop container, while in `"grid"` layouts, it targets the CSS Grid layout level.
        """
        passed_values = {k: v for k, v in locals().items() if (v is not None) and k != "kwargs"}
        required_fields = ["type"]
        optional_fields = ["style"]
        if type == "grid":
            required_fields += ["data"]
            optional_fields += ["numColumns", "numRows", "column", "row"]
        elif type == "item":
            required_fields += ["itemId"]
            optional_fields += ["column", "row"]
        missing_required = pamda.difference(required_fields, list(passed_values.keys()))
        if len(missing_required) > 0:
            raise Exception(f"Missing required fields: {str(missing_required)}")
        for k, v in passed_values.items():
            if k not in required_fields + optional_fields:
                kwargs[k] = v
        accepted_values = {
            "type": ["grid", "item"],
        }
        if isinstance(numRows, str):
            accepted_values["numRows"] = ["auto"]
        if isinstance(numColumns, str):
            accepted_values["numColumns"] = ["auto"]
        return {
            "kwargs": kwargs,
            "accepted_values": accepted_values,
        }

    def __extend_spec__(self, **kwargs):
        layout_type = self.data.get("type", None)
        if layout_type == "grid":
            for field, value in self.data.get("data", {}).items():
                layout(data=value, log=self.log, prepend_path=["data", field], **kwargs)
        if layout_type == "item":
            item_id = self.data.get("itemId", None)
            prop_id_list = kwargs.get("prop_id_list", [])
            if item_id not in prop_id_list:
                self.__error__(
                    msg=f"`itemId` ({item_id}) does not match any valid prop ids {prop_id_list}"
                )


@type_enforced.Enforcer
class values(ApiValidator):
    @staticmethod
    def spec(**kwargs):
        """
        Accepts all arbitrary values depending on what you have in your props as part of the API spec.

        The values you pass will be validated against the props in your API spec.
        """
        return {
            "kwargs": {},
            "accepted_values": {},
        }

    def __extend_spec__(self, **kwargs):
        props_data = kwargs.get("props_data", {})
        for prop_key, prop_value in self.data.items():
            prop_spec = props_data.get(prop_key, {})
            if not prop_spec:
                self.__error__(
                    msg=f"`{prop_key}` does not match any valid prop ids {list(props_data.keys())}"
                )
                continue
            prop_type = prop_spec.get("type", None)
            if prop_type == "head":
                self.__error__(
                    msg=f"`{prop_key}` with the prop type of `{prop_type}` can not have an associated value."
                )
                continue
            acceptable_types = {
                "num": (int, float),
                "toggle": (bool,),
                "button": (str,),
                "text": (str,),
                "selector": (list,),
                "date": (str,),
                "media": (str,),
                "coordinate": (list,),
            }.get(prop_type, tuple())
            # Add None to acceptable types if allowed
            if prop_spec.get("allowNone", False):
                acceptable_types += (type(None),)
            # Validate types and continue if invalid
            if not self.__check_type__(prop_value, acceptable_types, prepend_path=[prop_key]):
                continue
            # Continue if the value is None
            if prop_value is None:
                continue
            if prop_type == "num":
                min_value = prop_spec.get("minValue", float("-inf"))
                max_value = prop_spec.get("maxValue", float("inf"))
                if prop_value < min_value or prop_value > max_value:
                    self.__error__(
                        msg=f"`{prop_key}` with the prop type of `{prop_type}` must be between {min_value} and {max_value} as defined by the API spec."
                    )
            elif prop_type == "selector":
                options = list(prop_spec.get("options", {}).keys())
                self.__check_subset_valid__(prop_value, options, prepend_path=[prop_key])
            elif prop_type == "date":
                self.__check_date_valid__(
                    prop_value,
                    date_variant=prop_spec.get("variant", "date"),
                    prepend_path=[prop_key],
                )
            elif prop_type == "media":
                self.__check_url_valid__(prop_value, prepend_path=[prop_key])
            elif prop_type == "coordinate":
                coord_variant = prop_spec.get("variant", "latLngInput")
                self.__check_coord_path_valid__(prop_value, coord_variant, prepend_path=[prop_key])


@type_enforced.Enforcer
class valueLists(ApiValidator):
    @staticmethod
    def spec(**kwargs):
        """
        Accepts all arbitrary values depending on what you have in your props as part of the API spec.

        The valueLists you pass will be validated against the `props` from your API spec.
        """
        return {
            "kwargs": {},
            "accepted_values": {},
        }

    def __extend_spec__(self, **kwargs):
        props_data = kwargs.get("props_data", {})
        for prop_key, prop_value_list in self.data.items():
            if not isinstance(prop_value_list, list):
                self.__error__(
                    msg=f"`{prop_key}` must be a list of values for valueLists", path=[prop_key]
                )
                continue
            prop_spec = props_data.get(prop_key, {})
            if not prop_spec:
                self.__error__(
                    msg=f"`{prop_key}` does not match any valid prop ids {list(props_data.keys())}"
                )
                continue
            prop_type = prop_spec.get("type", None)
            if prop_type == "head":
                self.__error__(
                    msg=f"`{prop_key}` with the prop type of `{prop_type}` can not have an associated value."
                )
                continue
            acceptable_types = {
                "num": (int, float),
                "toggle": (bool,),
                "button": (str,),
                "text": (str,),
                "selector": (list,),
                "date": (str,),
                "media": (str,),
            }.get(prop_type, tuple())
            # Add None to acceptable types if allowed
            if prop_spec.get("allowNone", False):
                acceptable_types += (type(None),)
            if not self.__check_type_list__(
                data=prop_value_list, types=acceptable_types, prepend_path=[prop_key]
            ):
                continue
            if prop_spec.get("allowNone", False):
                prop_value_list = [v for v in prop_value_list if v is not None]
            if prop_type == "num":
                # Validate minimum is met
                min_value = prop_spec.get("minValue")
                if min_value is not None:
                    prop_value_list_min = min(prop_value_list)
                    if prop_value_list_min < min_value:
                        self.__error__(
                            msg=f"`{prop_key}` has a value that is less than {min_value} as defined by the API spec."
                        )
                # Validate maximum is met
                max_value = prop_spec.get("maxValue")
                if max_value is not None:
                    prop_value_list_max = max(prop_value_list)
                    if prop_value_list_max > max_value:
                        self.__error__(
                            msg=f"`{prop_key}` has a value that is greater than {max_value} as defined by the API spec."
                        )
            elif prop_type == "selector":
                options = list(prop_spec.get("options", {}).keys())
                prop_value_list_set = list(set(pamda.flatten(prop_value_list)))
                self.__check_subset_valid__(prop_value_list_set, options, prepend_path=[prop_key])
            elif prop_type == "head":
                self.__error__(
                    msg=f"`{prop_key}` with the prop type of `{prop_type}` can not have an associated value."
                )
            elif prop_type == "date":
                prop_value_list_set = list(set(prop_value_list))
                date_variant = prop_spec.get("variant", "date")
                for prop_value in prop_value_list:
                    if not self.__check_date_valid__(
                        prop_value, date_variant=date_variant, prepend_path=[prop_key]
                    ):
                        continue
            elif prop_type == "media":
                for prop_value in prop_value_list:
                    if not self.__check_url_valid__(prop_value, prepend_path=[prop_key]):
                        continue
