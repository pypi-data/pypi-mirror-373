"""
Create grouped outputs for building generalized charts and tables.
"""

from cave_utils.api_utils.validator_utils import ApiValidator, CustomKeyValidator
import type_enforced
from pamda import pamda


@type_enforced.Enforcer
class groupedOutputs(ApiValidator):
    """
    The grouped outputs are located under the path **`groupedOutputs`**.
    """

    @staticmethod
    def spec(groupings: dict, data: dict, **kwargs):
        """
        Arguments:

        * **`groupings`**: `[dict]` &rarr; A dictionary of groupings that are available for the data.
            * **See**: `groupedOutputs.groupings`
        * **`data`**: `[dict]` &rarr; The data to be grouped.
            * **See**: `groupedOutputs.data`
        """
        return {"kwargs": kwargs, "accepted_values": {}}

    def __extend_spec__(self, **kwargs):
        groupedOutputs_groupings = self.data.get("groupings", {})
        CustomKeyValidator(
            data=groupedOutputs_groupings,
            log=self.log,
            prepend_path=["groupings"],
            validator=groupedOutputs_groupings_star,
            **kwargs,
        )
        groupedOutputs_data = self.data.get("data", {})
        CustomKeyValidator(
            data=groupedOutputs_data,
            log=self.log,
            prepend_path=["data"],
            validator=groupedOutputs_data_star,
            available_groups={
                k: v.get("data", {}).get("id", []) for k, v in groupedOutputs_groupings.items()
            },
            **kwargs,
        )


@type_enforced.Enforcer
class groupedOutputs_data_star(ApiValidator):
    """
    The grouped outputs data is located under the path **`groupedOutputs.data.*`**.
    """

    @staticmethod
    def spec(stats: dict, valueLists: dict, groupLists: dict, **kwargs):
        """
        Arguments:

        * **`stats`**: `[dict]` &rarr; A dictionary of stats that are available for the data.
            * **See**: `cave_utils.api.groupedOutputs.groupedOutputs_data_star_stats`
        **`valueLists`**: `[dict]` &rarr; A dictionary of lists that make up the stats for the data.
            * **See**: `cave_utils.api.groupedOutputs.groupedOutputs_data_star_valueLists`
            * **Note**: Each key must also be a key in `groupedOutputs.data.*.stats`.
        **`groupLists`**: `[dict]` &rarr; A dictionary of lists that make up the groupings for the data.
        """
        return {"kwargs": kwargs, "accepted_values": {}}

    def __extend_spec__(self, **kwargs):
        stats_data = self.data.get("stats", {})
        CustomKeyValidator(
            data=stats_data,
            log=self.log,
            prepend_path=["stats"],
            validator=groupedOutputs_data_star_stats,
            **kwargs,
        )
        # Ensure Valid Value Lists
        valueLists_data = self.data.get("valueLists", {})
        groupedOutputs_data_star_valueLists(
            data=valueLists_data,
            log=self.log,
            prepend_path=["valueLists"],
            stat_keys=[k for k in stats_data.keys()],
            **kwargs,
        )
        # Ensure Valid Group Lists
        groupLists_data = self.data.get("groupLists", {})
        groupedOutputs_data_star_groupLists(
            data=groupLists_data,
            log=self.log,
            prepend_path=["groupLists"],
            **kwargs,
        )

        # Ensure that all lists are the same length
        try:
            if (
                len(
                    set(
                        [len(v) for v in valueLists_data.values()]
                        + [len(v) for v in groupLists_data.values()]
                    )
                )
                != 1
            ):
                raise Exception
        except:
            self.__error__(
                msg="All values in groupedOutputs.data.*.groupLists and groupedOutputs.data.*.valueLists must be lists of the same length.",
            )


@type_enforced.Enforcer
class groupedOutputs_data_star_stats(ApiValidator):
    """
    The grouped output stats are located under the path **`groupedOutputs.data.*.stats`**.
    """

    @staticmethod
    def spec(
        name: str,
        unit: str | None = None,
        unitPlacement: str | None = None,
        precision: int | None = None,
        trailingZeros: bool | None = None,
        notation: str | None = None,
        notationDisplay: str | None = None,
        **kwargs,
    ):
        """
        Arguments:

        * **`name`**: `[str]` &rarr; The name of the stat.
        * **`unit`**: `[str]` &rarr; The unit to use for the stat.
            * **Note**: If left unspecified (i.e., `None`), it will default to `settings.defaults.unit`.
        * **`unitPlacement`**: `[str]` = `None` &rarr; The position of the `unit` symbol relative to the value.
            * **Accepted Values**:
                * `"after"`: The `unit` appears after the value.
                * `"afterWithSpace"`: The `unit` appears after the value, separated by a space.
                * `"before"`: The `unit` appears before the value.
                * `"beforeWithSpace"`: The unit is placed before the value, with a space in between.
            * **Note**: If left unspecified (i.e., `None`), it will default to `settings.defaults.unitPlacement`.
        * **`precision`**: `[int]` = `None` &rarr; The number of decimal places to display.
            * **Notes**:
                * Set the precision to `0` to attach an integer constraint.
                * If left unspecified (i.e., `None`), it will default to `settings.defaults.precision`.
        * **`trailingZeros`**: `[bool]` = `None` &rarr; If `True`, trailing zeros will be displayed.
            * **Notes**:
                * This ensures that all precision digits are shown. For example: `1.5` &rarr; `1.500` when precision is `3`.
                * If left unspecified (i.e., `None`), it will default to `settings.defaults.trailingZeros`.
        * **`notation`**: `[str]` = `"standard"` &rarr; The formatting style of a numeric value.
        * **`notationDisplay`**: `[str]` = `"e+"` | `"short"` | `None` &rarr; Further customize the formatting within the selected `notation`.
            * **Notes**:
                * No `notationDisplay` option is provided for a `"standard"` notation
                * The options `"short"` and `"long"` are only provided for the `"compact"` notation
                * The options `"e"`, `"e+"`, `"E"`, `"E+"`, `"x10^"`, and `"x10^+"` are provided for the `"scientific"`, `"engineering"` and `"precision"` notations
                * If `None`, it defaults to `"short"` for `"compact"` notation, and to `"e+"` for `"scientific"`, `"engineering"` or `"precision"` notations; if the option is set to `"standard"`, its value remains `None`.

        [metric prefix]: https://en.wikipedia.org/wiki/Metric_prefix
        [Scientific notation]: https://en.wikipedia.org/wiki/Scientific_notation
        [Engineering notation]: https://en.wikipedia.org/wiki/Engineering_notation
        [Number.prototype.toPrecision]: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/toPrecision
        """
        passed_values = {k: v for k, v in locals().items() if (v is not None) and k != "kwargs"}
        if notationDisplay and not notation:
            raise Exception(f"Missing required fields: notation")
        notation = passed_values.get("notation", "standard")

        return {
            "kwargs": kwargs,
            "accepted_values": {
                "unitPlacement": ["after", "afterWithSpace", "before", "beforeWithSpace"],
                "notation": ["standard", "compact", "scientific", "engineering", "precision"],
                "notationDisplay": {
                    "compact": ["short", "long"],
                    "scientific": ["e", "e+", "E", "E+", "x10^", "x10^+"],
                    "engineering": ["e", "e+", "E", "E+", "x10^", "x10^+"],
                    "precision": ["e", "e+", "E", "E+", "x10^", "x10^+"],
                    "standard": [],
                }.get(notation, []),
            },
        }


@type_enforced.Enforcer
class groupedOutputs_data_star_valueLists(ApiValidator):
    """
    The value lists are located under the path **`groupedOutputs.data.*.valueLists`**.
    """

    @staticmethod
    def spec(**kwargs):
        """
        Arguments:

        - **`yourCustomKeyHere`**: `[list]` &rarr;
            - * **Note**: Each custom key passed must also be a key in `groupedOutputs.data.*.stats`.
            - * **Note**: Each value must be a list of integers or floats.
        """
        return {"kwargs": {}, "accepted_values": {}}

    def __extend_spec__(self, **kwargs):
        # Custom Validation to ensure that all keys are in calculation strings
        valid_values = kwargs.get("stat_keys", [])
        invalid_values = [
            i for i in list(self.data.keys()) if not any([i in j for j in valid_values])
        ]
        if len(invalid_values) > 0:
            valid_values = valid_values[:10] + ["..."] if len(valid_values) > 10 else valid_values
            self.__error__(
                path=[],
                msg=f"Invalid keys(s) selected: {str(invalid_values)}. Accepted keys are substrings of your calculations: {valid_values}",
            )
            return
        # End Custom Validation
        for key, value in self.data.items():
            if self.__check_type__(value=value, check_type=(list,), prepend_path=[key]):
                self.__check_type_list__(data=value, types=(int, float), prepend_path=[key])


@type_enforced.Enforcer
class groupedOutputs_data_star_groupLists(ApiValidator):
    """
    The group lists are located under the path **`groupedOutputs.data.*.groupLists`**.
    """

    @staticmethod
    def spec(**kwargs):
        """
        Arguments:

        - **`yourCustomKeyHere`**: `[list]` &rarr;
            - * **Note**: Each value must be a list of strings or ints.
            - * **Note**: Each item in the passed value must also be found in `groupedOutputs.groupings.{yourCustomKeyHere}.data.id`.
        """
        return {"kwargs": {}, "accepted_values": {}}

    def __extend_spec__(self, **kwargs):
        available_groups = kwargs.get("available_groups", {})
        if self.__check_subset_valid__(
            subset=list(self.data.keys()),
            valid_values=list(available_groups.keys()),
            prepend_path=[],
        ):
            for key, value in self.data.items():
                if self.__check_type__(value=value, check_type=(list,), prepend_path=[key]):
                    self.__check_type_list__(data=value, types=(str, int), prepend_path=[key])
                    self.__check_subset_valid__(
                        subset=value,
                        valid_values=available_groups.get(key, []),
                        prepend_path=[key],
                    )


@type_enforced.Enforcer
class groupedOutputs_groupings_star(ApiValidator):
    """
    The groupings are located under the path **`groupedOutputs.groupings.*`**.
    """

    @staticmethod
    def spec(
        levels: dict,
        data: dict,
        name: str,
        layoutDirection: str = "vertical",
        grouping: str | None = None,
        **kwargs,
    ):
        """
        Arguments:

        * **`levels`**: `[dict]` &rarr;
            * A dictionary of levels that are available for the grouping.
            * **See**: `groupedOutputs_groupings_star_levels_star`
        * **`data`**: `[dict]` &rarr; The data to be grouped.
            * **See**: `groupedOutputs_groupings_star_data`
        * **`name`**: `[str]` &rarr; The name of the grouping.
        * **`layoutDirection`**: `[str]` = `"vertical"` &rarr; The direction of the grouping levels in the layout.
            * **Accepted Values**:
                * `"horizontal"`: Plain number formatting
                * `"vertical"`: Resembles the [metric prefix][] system
                * `"scientific"`: [Scientific notation][]
                * `"engineering"`: [Engineering notation][]
        * **`grouping`**: `[str]` = `None` &rarr;
            * A group that is created to put similar groupings together in the UI dropdowns when selecting groupings.
            * **Note**: If `None`, the grouping will be placed in the root of the UI dropdowns.

        [metric prefix]: https://en.wikipedia.org/wiki/Metric_prefix
        [Scientific notation]: https://en.wikipedia.org/wiki/Scientific_notation
        [Engineering notation]: https://en.wikipedia.org/wiki/Engineering_notation
        """
        return {
            "kwargs": kwargs,
            "accepted_values": {
                "layoutDirection": ["horizontal", "vertical"],
            },
        }

    def __extend_spec__(self, **kwargs):
        levels_data = self.data.get("levels", {})
        levels_data_keys = list(levels_data.keys())
        data_data = self.data.get("data", {})
        CustomKeyValidator(
            data=levels_data,
            log=self.log,
            prepend_path=["levels"],
            validator=groupedOutputs_groupings_star_levels_star,
            acceptable_parents=levels_data_keys,
            acceptable_data_levels=data_data,
            **kwargs,
        )
        groupedOutputs_groupings_star_data(
            data=data_data,
            log=self.log,
            prepend_path=["data"],
            acceptable_data_keys=levels_data_keys,
            **kwargs,
        )


@type_enforced.Enforcer
class groupedOutputs_groupings_star_data(ApiValidator):
    """
    The groupings data is located under the path **`groupedOutputs.groupings.*.data`**.
    """

    @staticmethod
    def spec(id: list, **kwargs):
        """
        Arguments:

        * **`id`**: `[list]` &rarr; The id of the data to be grouped.
            * **Note**: This can be a list of strings or ints.
        * **`customKeyHere`**: `[list]` &rarr;
            * The names of the data to be grouped for this feature/level.
            * **Note**: Each key listed here must be in `groupedOutputs.groupings.*.levels.*`
            * **Note**: Each value must be a list of strings or ints.
        """
        return {"kwargs": {}, "accepted_values": {}}

    def __extend_spec__(self, **kwargs):
        keys = list(self.data.keys())
        expected_keys = kwargs.get("acceptable_data_keys", []) + ["id"]
        missing_keys = pamda.difference(expected_keys, keys)
        # Ensure that all keys are present
        if len(missing_keys) > 0:
            self.__error__(
                msg=f"The following keys: {str(missing_keys)} are required in groupedOutputs.groupings.*.data",
            )
        # Ensure that all keys are valid
        self.__check_subset_valid__(subset=keys, valid_values=expected_keys, prepend_path=[])
        # Ensure that all values are lists
        self.__check_type_dict__(data=self.data, types=(list,), prepend_path=[])
        # Ensure that all values are lists of strings
        for key, value in self.data.items():
            if isinstance(value, list):
                self.__check_type_list__(data=value, types=(str, int), prepend_path=[key])
        # Ensure that all lists are the same length
        if len(set([len(v) for v in self.data.values()])) != 1:
            self.__error__(
                msg="All values must be lists of the same length.",
            )


@type_enforced.Enforcer
class groupedOutputs_groupings_star_levels_star(ApiValidator):
    """
    The level data is located under the path **`groupedOutputs.groupings.*.levels.*`**.
    """

    @staticmethod
    def spec(
        name: str,
        parent: str | None = None,
        ordering: list | None = None,
        orderWithParent: bool = True,
        coloring: dict | None = None,
        **kwargs,
    ):
        """
        Arguments:

        * **`name`**: `[str]` &rarr; The name of the level.
        * **`parent`**: `[str]` &rarr;
            * The key of the parent level. This is used to create a hierarchy of levels.
            * **Notes**:
                * The parent level key must be defined in `groupedOutputs.groupings.*.levels.*`
                * If `None`, this will be considered to be the root of the hierarchy.
        * **`ordering`**: `[list]` &rarr;
            * The ordering of individual values for this level in charts and tables.
            * **Note**: If `None`, the ordering will be alphabetical.
            * **Note**: If a partial ordering is provided, the provided values will be placed first in order.
            * **Note**: If a partial ordering is provided, the remaining values will be placed in alphabetical order.
            * **Note**: All items in this list must be defined in `groupedOutputs.groupings.*.levels.*.values.*`
        * **`orderWithParent`**: `[bool]` = `True` &rarr;
            * Whether or not to order this level based on the parent level.
            * If `True`, the ordering of this level will also be based on the parent level.
            * If `False`, the ordering will be based on the ordering of this level only.
        * **`coloring`**: `[dict]` &rarr;
            * A dictionary of colors to be used for the level.
            * Each key in this dictionary is a value in the level.
            * Each value in this dictionary is an rgba string.
            * **See**: `cave_utils.api.groupedOutputs.groupedOutputs_groupings_star_levels_star_coloring`
        """
        return {"kwargs": kwargs, "accepted_values": {}}

    def __extend_spec__(self, **kwargs):
        parent = self.data.get("parent")
        if parent is not None:
            self.__check_subset_valid__(
                subset=[parent],
                valid_values=kwargs.get("acceptable_parents", []),
                prepend_path=["parent"],
            )
        ordering = self.data.get("ordering")
        if ordering is not None:
            self.__check_subset_valid__(
                subset=ordering,
                valid_values=kwargs.get("acceptable_data_levels", {}).get(
                    kwargs.get("CustomKeyValidatorFieldId"), []
                ),
                prepend_path=["ordering"],
            )

        coloring = self.data.get("coloring")
        if coloring is not None:
            self.__check_subset_valid__(
                subset=list(coloring.keys()),
                valid_values=kwargs.get("acceptable_data_levels", {}).get(
                    kwargs.get("CustomKeyValidatorFieldId"), []
                ),
                prepend_path=["coloring"],
            )
            for key, value in coloring.items():
                self.__check_color_string_valid__(
                    color_string=value, prepend_path=["coloring", key]
                )
