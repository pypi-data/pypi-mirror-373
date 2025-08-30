"""
Panes serve as main containers for UI controls such as toggles, text
and number fields, sliders, etc. They can also contain buttons that
facilitate interaction with actionable data.
"""

from cave_utils.api_utils.validator_utils import ApiValidator, CustomKeyValidator
from cave_utils.api_utils.general import props, values, layout
import type_enforced


@type_enforced.Enforcer
class panes(ApiValidator):
    """
    The panes are located under the path **`panes`**.
    """

    @staticmethod
    def spec(data: dict = dict(), paneState: dict = dict(), **kwargs):
        """
        Arguments:
        * **`data`**: `[dict]` &rarr; The data to pass to `panes.data.*`.
        * **`paneState`**: `[dict]` &rarr;
            * A dictionary of pane states per their location in the `appBar` object.
            * **Accepted Values**:
                * `"left"`: The state of a pane triggered from the left-side app bar.
                * `"center"`: The pane state of a centered modal.
                * `"right"`: The state of a pane triggered from the right-side app bar.
            * **Note**: In the vast majority of use cases, the `paneState` dictionary is not relevant to the design of the CAVE App, as its primary purpose is to store temporary UI state during user interactions. Nevertheless, a CAVE App designer has the option to prepopulate it if required.
        """
        return {"kwargs": kwargs, "accepted_values": {"paneState": ["left", "center", "right"]}}

    def __extend_spec__(self, **kwargs):
        data = self.data.get("data", {})
        CustomKeyValidator(
            data=data, log=self.log, prepend_path=["data"], validator=panes_data_star, **kwargs
        )
        pane_keys = list(data.keys())
        paneState = self.data.get("paneState", {})
        allowedPaneStateKeys = ["left", "center", "right"]
        for key in paneState.keys():
            if key not in allowedPaneStateKeys:
                self.__warn__(
                    f"Invalid key '{key}' found in 'paneState'. Valid keys are: {allowedPaneStateKeys}"
                )
        CustomKeyValidator(
            data=paneState,
            log=self.log,
            prepend_path=["paneState"],
            validator=panes_paneState_star,
            pane_keys=pane_keys,
            **kwargs,
        )


@type_enforced.Enforcer
class panes_data_star(ApiValidator):
    """
    The pane data is located under the path **`panes.data.*`**.
    """

    @staticmethod
    def spec(
        name: str, props: dict, values: dict | None = None, layout: dict | None = None, **kwargs
    ):
        """
        Arguments:

        * **`name`**: `[str]` &rarr; The name of the pane.
        * **`props`**: `[dict]` &rarr; The props that will be rendered in the pane.
            * **See**: `cave_utils.api_utils.general.props`
        * **`values`**: `[dict]` = `None` &rarr;
            * The values to be assigned to the respective props. Each value is associated with its corresponding prop based on the key name used in `props`.
            * **See**: `cave_utils.api_utils.general.values`
        * **`layout`**: `[dict]` =`{"type": "grid", "numColumns": "auto", "numRows": "auto"}` &rarr;
            * The layout of the pane.
            * **See**: `cave_utils.api_utils.general.layout`
        """
        return {"kwargs": kwargs, "accepted_values": {}}

    def __extend_spec__(self, **kwargs):
        # Validate Props
        props_data = self.data.get("props", {})
        CustomKeyValidator(
            data=props_data,
            log=self.log,
            prepend_path=["props"],
            validator=props,
            **kwargs,
        )
        values(
            data=self.data.get("values", {}),
            log=self.log,
            prepend_path=["values"],
            props_data=props_data,
            **kwargs,
        )
        layout_data = self.data.get("layout")
        if layout_data is not None:
            layout(
                data=layout_data,
                log=self.log,
                prepend_path=["layout"],
                prop_id_list=list(props_data.keys()),
                **kwargs,
            )


@type_enforced.Enforcer
class panes_paneState_star(ApiValidator):
    """
    The pane state data is located under the path **`panes.paneState.*.*`**.
    """

    @staticmethod
    def spec(type: str = "pane", open: str | dict | None = None, pin: bool = False, **kwargs):
        """
        Arguments:

        * **`pin`**: `[bool]` = `False` &rarr; Whether or not the pane is pinned.
            * **Note**: Only used for panes located on `"left"` or `"right"` side app bars.
        * **`type`**: `[str]` = `"pane"` &rarr; The context that activated the current visible pane.
            * **Accepted Values**:
                * `"pane"`: A pane triggered from the `"left"` or `"right"` side app bars.
                * `"feature"`: Map feature data is displayed in the `"center"` of the screen.
            * **Note**: In the vast majority of use cases, the `type` attribute is not relevant to the design of the CAVE App, as its primary purpose is to store temporary UI state during user interactions. Nevertheless, a CAVE App designer has the option to prepopulate it if required.
        * **`open`**: `[str | dict]` = `None` &rarr;
            * The id of the open pane or a dictionary containing data related to a specific datapoint of a map feature.
            * **Notes**:
                * In the vast majority of use cases, the `open` attribute is not relevant to the design of the CAVE App, as its primary purpose is to store temporary UI state during user interactions. Nevertheless, a CAVE App designer has the option to prepopulate it if required.
                * For validation purposes or in advanced use cases, this attribute must correspond with the id (i.e., the dictionary key) of a pane located under `panes.data` when `type` is set to `"pane"`.
        """
        return {
            "kwargs": kwargs,
            "accepted_values": {
                "type": ["pane", "feature"],
            },
        }

    def __extend_spec__(self, **kwargs):
        open = self.data.get("open")
        if open is not None:
            if self.data.get("type") == "pane":
                self.__check_subset_valid__(
                    subset=[open],
                    valid_values=kwargs.get("pane_keys"),
                    prepend_path=["open"],
                )
            elif self.data.get("type") == "feature":
                self.__check_type__(value=open, check_type=dict, prepend_path=["open"])
