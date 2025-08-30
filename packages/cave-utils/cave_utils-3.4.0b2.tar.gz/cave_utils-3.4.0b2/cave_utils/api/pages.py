"""
Configure your application's pages.
"""

import type_enforced

from cave_utils.api_utils.validator_utils import ApiValidator, CustomKeyValidator


@type_enforced.Enforcer
class pages(ApiValidator):
    """
    The pages are located under the path **`pages`**.
    """

    @staticmethod
    def spec(currentPage: str | None = None, data: dict = dict(), **kwargs):
        """
        Arguments:

        * **`current_page`**: `[str]` = `None` &rarr; The id of the current page that is being rendered.
        * **`data`**: `[dict]` = `{}` &rarr; The data to pass to `pages.data.*`.
        """
        return {"kwargs": kwargs, "accepted_values": {}}

    def __extend_spec__(self, **kwargs):
        data = self.data.get("data", {})
        CustomKeyValidator(
            data=data, log=self.log, prepend_path=["data"], validator=pages_data_star, **kwargs
        )
        currentPage = self.data.get("currentPage")
        if isinstance(currentPage, str):
            self.__check_subset_valid__(
                subset=[currentPage], valid_values=list(data.keys()), prepend_path=["currentPage"]
            )


@type_enforced.Enforcer
class pages_data_star(ApiValidator):
    """
    The pages data are located under the path **`pages.data`**.
    """

    @staticmethod
    def spec(
        charts: dict | None = None,
        pageLayout: list[str | None] | None = None,
        lockedLayout: bool = False,
        **kwargs,
    ):
        """
        Arguments:

        * **`charts`**: `[dict]` = `{}` &rarr; The charts to display on the page.
            * **See**: `cave_utils.api.pages.pages_data_star_charts`.
        * **`pageLayout`**: `[list[str | None]]` = `{}` &rarr; The layout of the page.
            * **Accepted Values**:
                * Any key in the `charts` dict.
                * `"left"`: The chart to the left will be stretched into this chart.
                * `"up"`: The chart above will be stretched into this chart.
                * `None`: An empty slot.
            * **Notes**:
                * This is a single list of strings representing the layout of the page where the grid is read from left to right and top to bottom.
                    * For a 2x2 grid the layout would look like:
                        * [top-left, top-right, bottom-left, bottom-right]
                    * For a 3x3 grid the layout would look like:
                        * [top-left, top-center, top-right, middle-left, middle-center, middle-right, bottom-left, bottom-center, bottom-right]
                * The pageLayout must be of length 4 or 9 representing a 2x2 or 3x3 grid. It can be filled with `None` values if not all slots are used.
                * A `left` item cannot be placed in the leftmost column and must be placed to the right of a valid chart.
                * A `left` item cannot refer to an `up` item.
                * An `up` item cannot be placed in the top row and must be placed below a valid chart or `left` item.
        * **`lockedLayout`**: `[bool]` = `False` &rarr; Whether or not the layout should be locked.
            * **Notes**:
                * If `True`, the page layout will not be able to be modified by users includng modifying chart selections, chart types, and chart layout.
        """
        return {"kwargs": kwargs, "accepted_values": {}}

    def __extend_spec__(self, **kwargs):
        self.__prevent_subset_collision__(
            subset=list(self.data.get("charts").keys()),
            invalid_values=["left", "up"],
            prepend_path=["charts"],
        )
        for chartId, chart in self.data.get("charts", {}).items():
            pages_data_star_charts(
                data=chart,
                log=self.log,
                prepend_path=["charts", chartId],
                **kwargs,
            )
        if self.data.get("pageLayout") is not None:
            page_layout = self.data.get("pageLayout", [])
            self.__check_subset_valid__(
                subset=page_layout,
                valid_values=list(self.data.get("charts", {}).keys()) + ["left", "up", None],
                prepend_path=["pageLayout"],
            )
            if len(page_layout) not in [4, 9]:
                self.__error__(
                    msg="`pageLayout` must be of length 4 or 9 representing a 2x2 or 3x3 grid. It can be filled with None values if not all slots are used.",
                    path=["pageLayout"],
                )
            else:
                if len(page_layout) == 4:
                    page_layout_matrix = [page_layout[:2], page_layout[2:]]
                elif len(page_layout) == 9:
                    page_layout_matrix = [page_layout[:3], page_layout[3:6], page_layout[6:]]
                for row_idx, row in enumerate(page_layout_matrix):
                    for col_idx, item in enumerate(row):
                        if item == "left":
                            if col_idx == 0:
                                self.__error__(
                                    msg="`left` cannot be placed in the leftmost column.",
                                    path=["pageLayout", row_idx * 3 + col_idx],
                                )
                            elif page_layout_matrix[row_idx][col_idx - 1] in [None, "up"]:
                                self.__error__(
                                    msg="`left` must be placed to the left of a valid chart and can not be referring to an `up`.",
                                    path=["pageLayout", row_idx * 3 + col_idx],
                                )
                            else:
                                loop_row_idx = row_idx + 1
                                while loop_row_idx < len(page_layout_matrix):
                                    if page_layout_matrix[loop_row_idx][col_idx - 1] == "up":
                                        if page_layout_matrix[loop_row_idx][col_idx] != "up":
                                            self.__error__(
                                                msg="Something is not quite right with your `up` and `left` chart values.",
                                                path=["pageLayout"],
                                            )
                                    if page_layout_matrix[loop_row_idx][col_idx - 1] != "up":
                                        if page_layout_matrix[loop_row_idx][col_idx] == "up":
                                            self.__error__(
                                                msg="Something is not quite right with your `up` and `left` chart values.",
                                                path=["pageLayout"],
                                            )
                                    loop_row_idx += 1
                        elif item == "up":
                            if row_idx == 0:
                                self.__error__(
                                    msg="`up` cannot be placed in the top row.",
                                    path=["pageLayout", row_idx * 3 + col_idx],
                                )
                            elif page_layout_matrix[row_idx - 1][col_idx] is None:
                                self.__error__(
                                    msg="`up` must be placed below a valid value.",
                                    path=["pageLayout", row_idx * 3 + col_idx],
                                )


@type_enforced.Enforcer
class pages_data_star_charts(ApiValidator):
    """
    The charts are located under the path **`pages.data.*.charts`**.
    """

    @staticmethod
    def spec(
        type: str = "groupedOutput",
        dataset: str | None = None,
        chartType: str = "bar",
        mapId: str | None = None,
        groupingId: list | None = None,
        groupingLevel: list | None = None,
        stats: list | None = None,
        chartOptions: dict | None = None,
        sessions: list | None = None,
        globalOutput: list | None = None,
        lockedLayout: bool = False,
        maximized: bool = False,
        defaultToZero: bool = False,
        distributionType: str | None = None,
        distributionYAxis: str | None = None,
        distributionVariant: str | None = None,
        xAxisOrder: str | None = None,
        showNA: bool = False,
        **kwargs,
    ):
        """
        Arguments:

        * **`type`**: `[str]` = `"groupedOutput"` &rarr; The type of the page layout.
            * **Accepted Values**:
                * `"groupedOutput"`: The `unit` appears after the value.
                * `"globalOutput"`: The `unit` appears after the value, separated by a space.
                * `"map"`: The `unit` appears before the value.
        * **`dataset`**: `[str]` = `None` &rarr; The id/key representing the grouped output data to use.
        * **`chartType`**: `[str]` = `"bar"` &rarr; The chartType of the page layout.
            * Accepted Values:
                * When **`type`** == `"groupedOutput"`:
                    * `"area"`: An [area chart][]
                    * `"bar"`: A [bar chart][]
                    * `"stacked_bar"`: A [stacked bar chart][]
                    * `"box_plot"`: A [box plot chart][]
                    * `"cumulative_line"`: A cumulative line chart
                    * `"gauge"`: A [gauge chart][]
                    * `"heatmap"`: A [heatmap chart][]
                    * `"line"`: A [line chart][]
                    * `"scatter"`: A [scatter chart][]
                    * `"stacked_area"`: An [stacked area chart][]
                    * `"stacked_waterfall"`: An [stacked waterfall chart][]
                    * `"sunburst"`: A [sunburst chart][]
                    * `"table"`: A table showing the aggregated values.
                    * `"treemap"`: A [treemap chart][]
                    * `"waterfall"`: A [waterfall chart][]
                    * `"distribution"`: A [distribution chart][]
                * When **`type`** == `"globalOutput"`:
                    * `"bar"`: A [bar chart][]
                    * `"line"`: A [line chart][]
                    * `"table"`: A [table chart][]
                    * `"overview"`: A summary of the global outputs presented in a KPI-like format
                * Otherwise:
                    * `None`
        * **`mapId`**: `[str]` = `None` &rarr; The id of the map to use.
        * **`groupingId`**: `[list]` = `None` &rarr; The ids of the grouping to use.
        * **`groupingLevel`**: `[list]` = `None` &rarr; The ids of the grouping levels to use.
        * **`stats`**: `[list]` = `None` &rarr; A list of stats to use.
            * **See**: `cave_utils.api.pages.pages_data_star_charts_stats`.
        * **`chartOptions`**: `[dict]` = `None` &rarr; The options to pass to the chart.
            * TODO: Validate chart options
        * **`sessions`**: `[list]` = `None` &rarr; The ids of the sessions to use.
        * **`globalOutput`**: `[list]` = `None` &rarr; The ids of the global outputs to use.
        * **`lockedLayout`**: `[bool]` = `False` &rarr; Whether or not the layout should be locked.
        * **`statAggregation`**: `[str]` = `"sum"` &rarr; A stat aggregation function to apply to the chart data.
            * **Accepted Values**:
                * `"sum"`: Add up aggregated data
                * `"mean"`: Calculate the mean of the aggregated data
                * `"min"`: Find the minimum values within the aggregated data
                * `"max"`: Find the maximum values the aggregated data
        * **`maximized`**: `[bool]` = `False` &rarr; Whether or not the layout should be maximized.
            * **Note**: If more than one chart belonging to the same page layout is set to `True`, the first one found in the list will take precedence.
        * **`defaultToZero`**: `[bool]` = `False` &rarr; Whether or not the chart should default missing values to zero.
        * **`distributionType`**: `[str]` = `None` &rarr; The type of distribution function displayed in distribution charts.
            * Accepted Values:
                * `"pdf"`: Uses the probability density function.
                * `"cdf"`: Uses the cumulative density function.
            * **Notes**:
                * If left unspecified (i.e., `None`), it will default to `"pdf"`.
                * This attribute is applicable exclusively to the `"distribution"` chartType.
        * **`distributionYAxis`**: `[str]` = `None` &rarr; The y-axis metric in distribution charts.
            * Accepted Values:
                * `"counts"`: Displays the y-axis as raw counts of occurrences.
                * `"density"`: Displays the y-axis as proportions of total counts.
            * **Notes**:
                * If left unspecified (i.e., `None`), it will default to `"counts"`.
                * This attribute is applicable exclusively to the `"distribution"` chartType.
        * **`distributionVariant`**: `[str]` = `None` &rarr; The chart type displayed in distribution charts.
            * Accepted Values:
                * `"bar"`: A bar chart.
                * `"line"`: A line chart.
            * **Notes**:
                * If left unspecified (i.e., `None`), it will default to `"bar"`.
                * This attribute is applicable exclusively to the `"distribution"` chartType.
        * **`xAxisOrder`**: `[str]` = `None` &rarr; The order in which values on the x-axis should be ordered in, from left to right.
            * Accepted Values:
                * `"default"`: Does not reorder the x-axis in any way; keeps the default ordering.
                * `"value_ascending"`: Orders the x-axis by increasing numerical value.
                * `"value_descending"`: Orders the x-axis by decreasing numerical value.
                * `"alpha_ascending"`: Orders the x-axis in alphabetical order.
                * `"alpha_descending"`: Orders the x-axis in reverse alphabetical order.
            * **Note**: If left unspecified (i.e., `None`), it will default to `"default"`.
        * **`showNA`**: `[bool]` = `False` &rarr; Whether to display missing or filtered values in both the chart tooltip and the axis.

        [area chart]: https://en.wikipedia.org/wiki/Area_chart
        [bar chart]: https://en.wikipedia.org/wiki/Bar_chart
        [stacked bar chart]: https://en.wikipedia.org/wiki/Bar_chart
        [box plot chart]: https://en.wikipedia.org/wiki/Box_plot
        [cumulative line chart]: #
        [gauge chart]: https://echarts.apache.org/examples/en/index.html#chart-type-gauge
        [heatmap chart]: https://en.wikipedia.org/wiki/Heat_map
        [line chart]: https://en.wikipedia.org/wiki/Line_chart
        [scatter chart]: https://en.wikipedia.org/wiki/Scatter_plot
        [stacked area chart]: https://en.wikipedia.org/wiki/Area_chart
        [stacked waterfall chart]: https://en.wikipedia.org/wiki/Waterfall_chart
        [sunburst chart]: https://en.wikipedia.org/wiki/Pie_chart#Ring_chart,_sunburst_chart,_and_multilevel_pie_chart
        [table chart]: #
        [treemap chart]: https://en.wikipedia.org/wiki/Treemapping
        [waterfall chart]: https://en.wikipedia.org/wiki/Waterfall_chart
        [distribution chart]: https://en.wikipedia.org/wiki/Probability_distribution
        """
        if type == "globalOutput":
            chartType_options = ["bar", "line", "table", "overview"]
        elif type == "groupedOutput":
            chartType_options = [
                "area",
                "bar",
                "stacked_bar",
                "box_plot",
                "cumulative_line",
                "gauge",
                "heatmap",
                "line",
                "scatter",
                "stacked_area",
                "stacked_waterfall",
                "sunburst",
                "table",
                "treemap",
                "waterfall",
                "distribution",
                "mixed",
            ]
        else:
            chartType_options = []
        return {
            "kwargs": kwargs,
            "accepted_values": {
                "type": ["groupedOutput", "globalOutput", "map"],
                "chartType": chartType_options,
                "statAggregation": ["sum", "mean", "min", "max"],
                "distributionType": ["pdf", "cdf"] if chartType == "distribution" else [],
                "distributionYAxis": ["counts", "density"] if chartType == "distribution" else [],
                "distributionVariant": ["bar", "line"] if chartType == "distribution" else [],
                "xAxisOrder": [
                    "default",
                    "value_ascending",
                    "value_descending",
                    "alpha_ascending",
                    "alpha_descending",
                ],
            },
        }

    def __extend_spec__(self, **kwargs):
        pageLayout_type = self.data.get("type", "groupedOutput")
        # Validate globalOutput
        if pageLayout_type == "globalOutput":
            globalOutput = self.data.get("globalOutput")
            if globalOutput is not None:
                self.__check_subset_valid__(
                    subset=globalOutput,
                    valid_values=kwargs.get("globalOuputs_validPropIds", []),
                    prepend_path=["globalOutput"],
                )
            elif self.data.get("chartType") != "overview":
                self.__error__(
                    msg="`globalOutput` is a required key for `globalOutput` type pageLayouts when chartType is not `overview`.",
                    path=[],
                )
        # Validate map
        elif pageLayout_type == "map":
            mapId = self.data.get("mapId")
            if mapId is not None:
                self.__check_subset_valid__(
                    subset=[mapId],
                    valid_values=kwargs.get("maps_validMapIds", []),
                    prepend_path=["mapId"],
                )
            else:
                self.__error__(
                    msg="`mapId` is required for `map` type pageLayouts.",
                    prepend_path=["mapId"],
                )
        # Validate groupedOutput
        else:
            # Validate dataset
            dataset = self.data.get("dataset")
            if dataset is not None:
                # Ensure that the dataset is valid
                self.__check_subset_valid__(
                    subset=[dataset],
                    valid_values=list(kwargs.get("groupedOutputs_validDatasetIds", {}).keys()),
                    prepend_path=["dataset"],
                )
            groupingId = self.data.get("groupingId")
            if groupingId is not None:
                self.__check_type__(groupingId, list, prepend_path=["groupingId"])
                all_valid_group_ids = kwargs.get("groupedOutputs_validDatasetIds", {}).get(
                    dataset, []
                )
                valid_values = list(set(all_valid_group_ids))
                # Ensure that the groupingId is valid
                self.__check_subset_valid__(
                    subset=groupingId,
                    valid_values=valid_values,
                    prepend_path=["groupingId"],
                )
            # Validate groupingLevel
            groupingLevel = self.data.get("groupingLevel")
            if groupingLevel is not None:
                self.__check_type__(groupingLevel, list, prepend_path=["groupingLevel"])
                if len(groupingId) != len(groupingLevel):
                    self.__error__(
                        msg="`groupingId` and `groupingLevel` must be the same length.",
                    )
                    return
                for idx, groupingId_item in enumerate(groupingId):
                    groupingLevel_item = groupingLevel[idx]
                    self.__check_subset_valid__(
                        subset=[groupingLevel_item],
                        valid_values=list(
                            kwargs.get("groupedOutputs_validLevelIds", {}).get(groupingId_item, [])
                        ),
                        prepend_path=["groupingLevel", idx],
                    )
            if self.data.get("stats") is not None:
                for stat in self.data.get("stats"):
                    pages_data_star_charts_stats(
                        data=stat,
                        log=self.log,
                        prepend_path=["stats"],
                        dataset=dataset,
                        **kwargs,
                    )
            if self.data.get("chartOptions") is not None:
                pages_data_star_charts_chartOptions(
                    data=self.data.get("chartOptions"),
                    log=self.log,
                    prepend_path=["chartOptions"],
                    **kwargs,
                )


@type_enforced.Enforcer
class pages_data_star_charts_stats(ApiValidator):
    """
    The chart stats are located under the path **`pages.data.*.charts.stats`**.
    """

    @staticmethod
    def spec(
        statId: str | None = None,
        aggregationType: str | None = None,
        statIdDivisor: str | None = "sum",
        aggregationGroupingId: str | None = None,
        aggregationGroupingLevel: str | None = None,
        distributionType: str | None = None,
        distributionYAxis: str | None = None,
        distributionVariant: str | None = None,
        **kwargs,
    ):
        """
        Arguments:

        * **`statId`**: `[str]` = `None` &rarr; The id corresponding to the stat to be used.
        * **`aggregationType`**: `[str]` = `None` &rarr; The type of aggregation to apply to the stat.
            * Accepted Values:
                * `"sum"`: Sum the values.
                * `"mean"`: Calculate the mean of the values.
                * `"min"`: Find the minimum value.
                * `"max"`: Find the maximum value.
                * `"divisor"`: Divide the values by the `statIdDivisor`.
            * **Notes**:
                * If left unspecified (i.e., `None`), it will default to `"sum"`.
        * ** `aggregationGroupingId`**: `[str]` = `None` &rarr; The id of the grouping to use for aggregation.
            * **Notes**:
                * This is not applicable for the following aggregationTypes ['sum', 'divisor'].
        * ** `aggregationGroupingLevel`**: `[str]` = `None` &rarr; The id of the grouping level to use for aggregation.
            * **Notes**:
                * This is not applicable for the following aggregationTypes ['sum', 'divisor'].
        * **`statIdDivisor`**: `[str]` = `"sum"` &rarr; The id of the stat to use as the divisor.
        """
        return {
            "kwargs": kwargs,
            "accepted_values": {
                "aggregationType": ["sum", "mean", "min", "max", "divisor"],
            },
        }

    def __extend_spec__(self, **kwargs):
        statId = self.data.get("statId")
        if statId is not None:
            self.__check_subset_valid__(
                subset=[statId],
                valid_values=kwargs.get("groupedOutputs_validStatIds", {}).get(
                    kwargs.get("dataset"), []
                ),
                prepend_path=["statId"],
            )
        if self.data.get("aggregationType") == "sum":
            pass
        elif self.data.get("aggregationType") == "divisor":
            statIdDivisor = self.data.get("statIdDivisor")
            if statIdDivisor is not None:
                self.__check_subset_valid__(
                    subset=[statIdDivisor],
                    valid_values=kwargs.get("groupedOutputs_validStatIds", {}).get(
                        kwargs.get("dataset"), []
                    ),
                    prepend_path=["statIdDivisor"],
                )
            else:
                self.__warn__(
                    msg="The `statIdDivisor` key should be passed when `aggregationType='divisor'`."
                )
        else:
            aggregationGroupingId = self.data.get("aggregationGroupingId")
            if aggregationGroupingId is not None:
                is_valid_aggregationGroupingId = self.__check_subset_valid__(
                    subset=[aggregationGroupingId],
                    valid_values=list(kwargs.get("groupedOutputs_validLevelIds", {}).keys()),
                    prepend_path=["aggregationGroupingId"],
                )
                if is_valid_aggregationGroupingId:
                    aggregationGroupingLevel = self.data.get("aggregationGroupingLevel")
                    if aggregationGroupingLevel is not None:
                        self.__check_subset_valid__(
                            subset=[aggregationGroupingLevel],
                            valid_values=kwargs.get("groupedOutputs_validLevelIds", {}).get(
                                aggregationGroupingId, []
                            ),
                            prepend_path=["aggregationGroupingLevel"],
                        )
                    else:
                        self.__warn__(
                            msg="The `aggregationGroupingLevel` key should be passed when `aggregationGroupingId` is passed."
                        )
                else:
                    self.__warn__(
                        msg="The `aggregationGroupingId` key should be passed when `aggregationType` is not 'sum' or 'divisor'."
                    )


@type_enforced.Enforcer
class pages_data_star_charts_chartOptions(ApiValidator):
    """
    The chart options are located under the path **`pages.data.*.charts.chartOptions`**.
    """

    @staticmethod
    def spec(
        leftChartType: str | None = None,
        rightChartType: str | None = None,
        **kwargs,
    ):
        """
        Arguments:

        * ** `leftChartType`**: `[str]` = `None` &rarr; The chart type to use for the left y-axis.
            * **Accepted Values**:
                * `"bar"`: A [bar chart][]
                * `"line"`: A [line chart][]
                * `"cumulative_line"`: A cumulative line chart
        * ** `rightChartType`**: `[str]` = `None` &rarr; The chart type to use for the right y-axis.
            * **Accepted Values**:
                * `"bar"`: A [bar chart][]
                * `"line"`: A [line chart][]
                * `"cumulative_line"`: A cumulative line chart
        * ** `cumulative`**: `[bool]` = `False` &rarr; Whether or not the chart should be cumulative.
        """
        return {
            "kwargs": kwargs,
            "accepted_values": {
                "leftChartType": ["bar", "line", "cumulative_line"],
                "rightChartType": ["bar", "line", "cumulative_line"],
            },
        }

    def __extend_spec__(self, **kwargs):
        pass
