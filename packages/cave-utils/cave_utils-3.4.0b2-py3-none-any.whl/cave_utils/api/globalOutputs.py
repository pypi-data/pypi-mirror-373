"""Create outputs that allow for simple charts and tables to present some totalization or global outcome of the data.

These outputs should be general to the entire application and they can be compared across sessions.
"""

from cave_utils.api_utils.validator_utils import ApiValidator, CustomKeyValidator
from cave_utils.api_utils.general import props, values, layout
import type_enforced


@type_enforced.Enforcer
class globalOutputs(ApiValidator):
    """
    The global outputs data is located under the path **`globalOutputs`**.
    """

    @staticmethod
    def spec(props: dict, values: dict | None = None, layout: dict | None = None, **kwargs):
        """
        Arguments:

        * **`props`**: `[dict]` &rarr; The props that will be rendered as global outputs.
            * **See**: `cave_utils.api_utils.general.props`
        * **`values`**: `[dict]` = `None` &rarr;
            * The values to be assigned to the respective props. Each value is associated with its corresponding prop based on the key name used in `props`.
            * **See**: `cave_utils.api_utils.general.values`
        * **`layout`**: `[dict]` =`{"type": "grid", "numColumns": "auto", "numRows": "auto"}` &rarr;
            * The layout of the global outputs when the "Overview" chart is selected.
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
