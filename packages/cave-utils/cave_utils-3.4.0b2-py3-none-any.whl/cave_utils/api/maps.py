"""
Configure the style and UI elements of your application's maps.
"""

from cave_utils.api_utils.validator_utils import ApiValidator, CustomKeyValidator
import type_enforced


@type_enforced.Enforcer
class maps(ApiValidator):
    """
    The maps are located under the path `maps`.
    """

    @staticmethod
    def spec(additionalMapStyles: dict = dict(), data: dict = dict(), **kwargs):
        """
        Arguments:

        * **`additionalMapStyles`**: `[dict]` = `{}` &rarr;
            * A dictionary of map specifications that define alternative visual appearances of a map.
        * **`data`**: `[dict]` = `{}` &rarr; The data to pass to `maps.data.*`.
        """
        return {"kwargs": kwargs, "accepted_values": {}}

    def __extend_spec__(self, **kwargs):
        data = self.data.get("data", {})
        CustomKeyValidator(
            data=self.data.get("additionalMapStyles", {}),
            log=self.log,
            prepend_path=["additionalMapStyles"],
            validator=maps_additionalMapStyles_star,
            **kwargs,
        )
        available_styles = list(self.data.get("additionalMapStyles", {}).keys()) + [
            "mapboxDark",
            "mapboxLight",
            "mapboxStreets",
            "mapboxSatellite",
            "mapboxNavDay",
            "mapboxNavNight",
            "cartoDarkMatter",
            "cartoPositron",
            "openStreetMap",
        ]
        CustomKeyValidator(
            data=data,
            log=self.log,
            prepend_path=["data"],
            validator=maps_data_star,
            available_styles=available_styles,
            **kwargs,
        )


@type_enforced.Enforcer
class maps_additionalMapStyles_star(ApiValidator):
    """
    The additional map styles are located under the path `maps.additionalMapStyles.*`.
    """

    @staticmethod
    def spec(
        name: str,
        spec: dict | str,
        fog: dict | None = None,
        icon: str = "md/MdMap",
        mapbox: bool = False,
        light: bool = False,
        sky: dict | None = None,
        **kwargs,
    ):
        """
        Arguments:

        * **`name`**: `[str]` &rarr; The name of the map style.
        * **`icon`**: `[str]` = `"md/MdMap"` &rarr; The icon to show in the map selection menu.
        * **`spec\u200b`**: `[dict | str]` &rarr; The spec to generate the map
            * **Notes**:
                * If `spec\u200b` is a string, it will be treated as a URL to a JSON spec file.
                * `spec\u200b` is only validated for its type, which can be either a `dict` or a `str`.
            * **See**:
                * Mapbox: https://docs.mapbox.com/api/maps/styles/
                * Carto: https://github.com/CartoDB/basemap-styles/blob/master/docs/basemap_styles.json
                * Raster: https://docs.mapbox.com/mapbox-gl-js/example/map-tiles/
        * **`fog`**: `[dict]` = `None` &rarr; The fog to show in the map selection menu.
            * **Notes**:
                * `fog` is only validated for its type (`dict`).
                * This is only used for when Mapbox is rendering the map.
                * When not using Mapbox, use the `sky` property instead.
                * **See**: https://docs.mapbox.com/mapbox-gl-js/api/map/#map#setfog
        * **`mapbox`**: `[bool]` = `False` &rarr; Enforces Mapbox rendering engine for this map style, even if using non-Mapbox tile sources.
        * **`light`**: `[bool]` = `False` &rarr; Enforces a light theme for map properties, root styling, and controls to improve visualization on light maps.
        * **`sky`**: `[dict | None]` = `None` &rarr; The sky settings for the map style.
            * **Notes**:
                * This is only used for when Mapbox is not rendering the map. This allows for sky rendering when using maplibre globe rendering.
                * When using Mapbox, use the `fog` property instead.
                * `sky` is only validated for its type `dict` and not its contents.
                * **See**: https://maplibre.org/maplibre-style-spec/sky/

        """
        return {"kwargs": kwargs, "accepted_values": {}}

    def __extend_spec__(self, **kwargs):
        pass
        # TODO: Validate icon
        # TODO: Possibly validate spec and fog


@type_enforced.Enforcer
class maps_data_star(ApiValidator):
    """
    The maps are located under the path `maps.data.*`.
    """

    @staticmethod
    def spec(
        name: str,
        currentStyle: str | None = None,
        lockStyle: bool | None = None,
        currentProjection: str | None = None,
        lockProjection: bool | None = None,
        defaultViewport: dict | None = None,
        optionalViewports: dict | None = None,
        legendGroups: dict | None = None,
        legendView: str | None = None,
        showLegendGroupNames: bool | None = None,
        legendLayout: str | None = None,
        legendWidth: str | None = None,
        **kwargs,
    ):
        """
        Arguments:

        * **`name`**: `[str]` &rarr; The name of the map.
        * **`currentStyle`**: `[str]` = `None` &rarr; The map's style id applied when the map is first loaded.
        * **`lockStyle`**: `[bool]` = `None` &rarr; Whether the map's style should lock to `currentStyle`. Ideal for custom raster tile maps.
            * **Note**: If left unspecified (i.e., `None`), it will default to `False`.
        * **`currentProjection`**: `[str]` = `None` &rarr; The map's projection id applied when the map is first loaded.
            * **Accepted Values**:
                * `"mercator"`: The [Mercator projection][]
                * `"globe"`: The map is displayed as a 3D globe
        * **`lockProjection`**: `[bool]` = `None` &rarr; Whether the map's projection should lock to `currentProjection`. Ideal for custom raster tile maps.
            * **Note**: If left unspecified (i.e., `None`), it will default to `False`.
        * **`defaultViewport`**: `[dict]` = `None` &rarr; The default viewport to use.
            * **Note**: The value of this attribute should match the structure of a viewport object.
            * **See**: `cave_utils.api.maps.viewport`
        * **`optionalViewports`**: `[dict]` = `None` &rarr; The optional viewports that can be selected by the end user.
            * **Note**: The value of this attribute should match the structure of a dictionary of viewport objects.
            * **See**: `cave_utils.api.maps.viewport`
        * **`legendGroups`**: `[dict]` = `None` &rarr; The legend groups to show in the map selection menu.
        * **`legendView`**: `[str]` = `None` &rarr; The view to show in the map selection menu.
            * **Accepted Values**:
                * `"compact"`: Display the legend in a compact format.
                * `"full"`: Display the full legend.
        * **`showLegendGroupNames`**: `[bool]` = `None` &rarr; Whether or not to show the legend group names in the map selection menu.
        * **`legendLayout`**: `[str]` = `None` &rarr; The layout of the legend.
            * **Accepted Values**:
                * `"auto"`: Sets the layout to column when legedView is full and row when legendView is compact.
                * `"column"`: Display the legend attributes per column (side by side).
                * `"row"`: Display the legend attributes per row (stacked vertically).
        * **`legendWidth`**: `[str]` = `None` &rarr; The width of the legend.
            * **Accepted Values**:
                * `"auto"`: Sets the width to `wide` when legendView is full and `slim` when legendView is compact.
                * `"slim"`: Sets teh legend witdth to 400px.
                * `"wide"`: Sets the legend width to 700px.

        [Mercator projection]: https://en.wikipedia.org/wiki/Mercator_projection
        """
        return {
            "kwargs": kwargs,
            "accepted_values": {
                "currentProjection": ["mercator", "globe"],
                "legendView": ["compact", "full"],
                "legendLayout": ["auto", "column", "row"],
                "legendWidth": ["auto", "slim", "wide"],
            },
        }

    def __extend_spec__(self, **kwargs):
        # Validate current style
        current_style = self.data.get("currentStyle")
        available_styles = kwargs.get("available_styles", [])
        if current_style is not None and current_style not in available_styles:
            self.__error__(
                msg=f"Invalid `currentStyle` ({current_style}) must be one of {available_styles}"
            )
        # Validate the default viewport
        viewport(
            data=self.data.get("defaultViewport", {}),
            log=self.log,
            prepend_path=["defaultViewport"],
            is_optional_viewport=False,
        )
        # Validate the optional viewports
        CustomKeyValidator(
            data=self.data.get("optionalViewports", {}),
            log=self.log,
            prepend_path=["optionalViewports"],
            validator=viewport,
            is_optional_viewport=True,
        )
        # Validate legend groups
        CustomKeyValidator(
            data=self.data.get("legendGroups", {}),
            log=self.log,
            prepend_path=["legendGroups"],
            validator=maps_data_star_legendGroups_star,
            **kwargs,
        )


@type_enforced.Enforcer
class viewport(ApiValidator):
    """
    The viewports can be located at the paths `maps.data.*.defaultViewport` and `maps.data.*.optionalViewports.*`.
    """

    @staticmethod
    def spec(
        latitude: int | float,
        longitude: int | float,
        zoom: int | float,
        bearing: int | float | None = None,
        pitch: int | float | None = None,
        maxZoom: int | float | None = None,
        minZoom: int | float | None = None,
        icon: str | None = None,
        name: str | None = None,
        **kwargs,
    ):
        """
        Arguments:

        * **`latitude`**: `[float | int]` &rarr; The latitude of the viewport.
            * **Note**: The value must be between -90 and 90.
        * **`longitude`**: `[float | int]` &rarr; The longitude of the viewport.
            * **Note**: The value must be between -180 and 180.
        * **`zoom`**: `[float | int]` &rarr; The zoom of the viewport.
            * **Note**: The value must be between 0 and 22.
        * **`bearing`**: `[float | int]` = `None` &rarr; The bearing of the viewport.
            * **Note**: The value must be between 0 and 360.
        * **`pitch`**: `[float | int]` = `None` &rarr; The pitch of the viewport.
            * **Note**: The value must be between 0 and 60.
        * **`maxZoom`**: `[float | int]` = `None` &rarr; The maximum zoom of the viewport.
            * **Note**: The value must be between 0 and 22.
        * **`minZoom`**: `[float | int]` = `None` &rarr; The minimum zoom of the viewport.
            * **Note**: The value must be between 0 and 22.
        * **`icon`**: `[str]` = `"md/MdGpsFixed"` &rarr; The icon to use for the viewport.
        * **`name`**: `[str]` = `None` &rarr; The name of the viewport.
            * **Note**: Only used for optional viewports.
        """
        return {
            "kwargs": kwargs,
            "accepted_values": {},
        }

    def __extend_spec__(self, **kwargs):
        field_validation = {
            "latitude": (-90, 90),
            "longitude": (-180, 180),
            "zoom": (0, 22),
            "bearing": (0, 360),
            "pitch": (0, 60),
            "maxZoom": (0, 22),
            "minZoom": (0, 22),
        }
        if kwargs.get("is_optional_viewport"):
            if self.data.get("name") is None:
                self.__error__(msg="`name` must be specified for optional viewports")
            if self.data.get("icon") is None:
                self.__error__(msg="`icon` must be specified for optional viewports")
        for field in ["latitude", "longitude", "zoom", "bearing", "pitch", "maxZoom", "minZoom"]:
            value = self.data.get(field)
            if value is not None:
                if not isinstance(value, (int, float)):
                    continue
                if value < field_validation[field][0] or value > field_validation[field][1]:
                    self.__error__(
                        msg=f"`{field} = {value}` but it should be between {field_validation[field][0]} and {field_validation[field][1]}"
                    )
                    continue
        # TODO: Validate Icons
        # if self.data.get("icon") is not None:
        #     self.__check_url_valid__(url=self.data.get("icon"), prepend_path=["icon"])


@type_enforced.Enforcer
class maps_data_star_legendGroups_star(ApiValidator):
    """
    The legend groups are located under the path `maps.data.*.legendGroups.*`.
    """

    @staticmethod
    def spec(
        name: str,
        data: dict,
        **kwargs,
    ):
        """
        Arguments:

        * **`name`**: `[str]` &rarr; The name of the legend group as displayed in the Map Legend.
        * **`data`**: `[dict]` &rarr; The relevant `data` dictionary for this legend group.
            * **See**: `cave_utils.api.maps.maps_data_star_legendGroups_star_data_star`
        """
        return {"kwargs": kwargs, "accepted_values": {}}

    def __extend_spec__(self, **kwargs):
        CustomKeyValidator(
            data=self.data.get("data", {}),
            log=self.log,
            prepend_path=["data"],
            validator=maps_data_star_legendGroups_star_data_star,
            **kwargs,
        )


@type_enforced.Enforcer
class maps_data_star_legendGroups_star_data_star(ApiValidator):
    """
    The legend group data is located under the path `maps.data.*.legendGroups.*.data.*`.
    """

    @staticmethod
    def spec(
        value: bool,
        sizeBy: str | None = None,
        colorBy: str | None = None,
        lineStyle: str | None = None,
        allowGrouping: bool = False,
        group: bool | None = False,
        groupCalcBySize: str | None = None,
        groupCalcByColor: str | None = None,
        groupScaleWithZoom: bool = False,
        groupScale: int | float | None = None,
        colorByOptions: list | None = None,
        sizeByOptions: list | None = None,
        icon: str | None = None,
        **kwargs,
    ):
        """
        Arguments:

        * **`value`**: `[bool]` &rarr; Whether or not to show this data layer on the map.
        * **`sizeBy`**: `[str]` = `None` &rarr; The prop id to use for sizing the data layer.
            * **Notes**:
                * If `None`, the data layer will not be sized
                * Does not apply to shape layers
        * **`colorBy`**: `[str]` = `None` &rarr; The prop id to use for coloring the data layer.
            * **Note**: If `None`, the data layer will not be colored
        * **`lineStyle`**: `[str]` = `"solid"` &rarr; The type of line to use for the data layer.
            * **Accepted Values**:
                * `"solid"`: Represents a single continuous line.
                * `"dashed"`: A series of dashes or line segments
                * `"dotted"`: A dotted line
            * **Note**: This attribute applies exclusively to `arc` layers.
        * **`allowGrouping`**: `[bool]` = `False` &rarr; Whether or not to allow grouping of the data layer.
            * **Note**: This attribute applies exclusively to `node` layers.
        * **`group`**: `[bool]` = `False` &rarr; Whether or not to group the data layer.
            * **Notes**:
                * If `False`, the data layer will not be grouped
                * This attribute applies exclusively to `node` layers
        * **`groupCalcBySize`**: `[str]` = `"count"` | `"mode"` &rarr; The aggregation function to use on the prop specified in `sizeBy`.
            * **Accepted Values**:
                * When **`sizeBy`** prop's **`type`** == `"num"`:
                    * `"count"`: Total number of nodes in the cluster
                    * `"sum"`: Total sum of values within the cluster
                    * `"mean"`: Average value within the cluster
                    * `"median"`: Median value within the cluster
                    * `"mode"`: Most frequently occurring value within the cluster
                    * `"max"`: Maximum value within the cluster
                    * `"min"`: Minimum value within the cluster
                * When **`sizeBy`** prop's **`type`** == `"toggle"`:
                    * `"mode"`: Most frequently occurring value within the cluster
                    * `"and"`: Determine if all values in the cluster are `True`
                    * `"or"`: Determine if at least one value in the cluster is `True`
                * When **`sizeBy`** prop's **`type`** == `"selector"`:
                    * `"mode"`: Most frequently occurring value within the cluster
            * **Notes**:
                * If `None`, the data layer will not be grouped
                * The calculation is based on the values of the prop specified in `sizeBy`
                * The default value for a `sizeBy` prop of type `"num"` is `"count"`. For other types, the default value is `"mode"`.
                * This attribute applies exclusively to `node` layers
        * **`groupCalcByColor`**: `[str]` = `"count"` | `"mode"` &rarr; The aggregation function to use on the prop specified in `colorBy`.
            * **Accepted Values**:
                * When **`colorBy`** prop's **`type`** == `"num"`:
                    * `"count"`: Total number of nodes in the cluster
                    * `"sum"`: Total sum of values within the cluster
                    * `"mean"`: Average value within the cluster
                    * `"median"`: Median value within the cluster
                    * `"mode"`: Most frequently occurring value within the cluster
                    * `"max"`: Maximum value within the cluster
                    * `"min"`: Minimum value within the cluster
                * When **`colorBy`** prop's **`type`** == `"toggle"`:
                    * `"mode"`: Total number of nodes in the cluster
                    * `"and"`: Determine if all values in the cluster are `True`
                    * `"or"`: Determine if at least one value in the cluster is `True`
                * When **`colorBy`** prop's **`type`** == `"selector"`:
                    * `"mode"`: Most frequently occurring value within the cluster
            * **Notes**:
                * If `None`, the data layer will not be grouped
                * The calculation is based on the prop specified in `colorBy`
                * The default value for a `colorBy` prop of type `"num"` is `"count"`. For other types, the default value is `"mode"`.
                * This attribute applies exclusively to `node` layers
        * **`groupScaleWithZoom`**: `[bool]` = `False` &rarr; Whether or not to scale the group size with zoom.
            * **Notes**:
                * If `False`, the group size will be constant as set by `groupScale`
                * This attribute applies exclusively to `node` layers
        * **`groupScale`**: `[float | int]` = `None` &rarr; The zoom level at which to conduct grouping of the nodes.
            * **Notes**:
                * If `None`, the group scale will be determined by the map zoom.
                * This attribute applies exclusively to `node` layers
        * **`colorByOptions`**: `[list]` = `None` &rarr; The allowed props to color the data layer.
            * **Notes**:
                * If `None`, the data layer will not be colored.
                * Only props of type `"num"`, `"toggle"`, `"selector"` and `"text"` can be colored.
            * **Example**:
                ```py
                "colorByOptions": ["numericPropExample", "selectorPropExample"]
                ```
            * **See**: `cave_utils.api.maps.colorByOptions`
        * **`sizeByOptions`**: `[list]` = `None` &rarr; The allowed props for sizing the data layer.
            * **Notes**:
                * If `None`, the data layer will not be sized.
                * Does not apply to shape layers
                * Only props of type `"num"`, `"toggle"`, `"selector"` and `"text"` can be sized.
            * **Example**:
                ```py
                "sizeByOptions": ["numericPropExample", "selectorPropExample"]
                ```
            * **See**: `cave_utils.api.maps.sizeByOptions`
        * **`icon`**: `[str]` = `None` &rarr; The icon to use for the data layer.
            * **Notes**:
                * Arc layer icons are determined by `lineStyle`.
                * Shape layer icons are always the default icon.
                * This attribute applies exclusively to `node` layers
        """
        return {
            "kwargs": kwargs,
            "accepted_values": {
                "lineStyle": ["solid", "dashed", "dotted"],
                "groupCalcBySize": [
                    "sum",
                    "mean",
                    "median",
                    "mode",
                    "min",
                    "max",
                    "count",
                    "and",
                    "or",
                ],
                "groupCalcByColor": [
                    "sum",
                    "mean",
                    "median",
                    "mode",
                    "min",
                    "max",
                    "count",
                    "and",
                    "or",
                ],
            },
        }

    def __extend_spec__(self, **kwargs):
        mapFeatures_feature_props = kwargs.get("mapFeatures_feature_props", {})
        field_id = kwargs.get("CustomKeyValidatorFieldId")
        if not self.__check_subset_valid__(
            subset=[field_id],
            valid_values=list(mapFeatures_feature_props.keys()),
            prepend_path=[],
        ):
            return
        available_props = mapFeatures_feature_props.get(field_id)
        colorBy_availableProps = {
            k: v
            for k, v in available_props.items()
            if (
                v.get("type") in ["num", "toggle", "selector", "text"]
                and (v.get("gradient") is not None or v.get("options") is not None)
            )
        }
        sizeBy_availableProps = {
            k: v
            for k, v in available_props.items()
            if (
                v.get("type") in ["num", "toggle", "selector", "text"]
                and (v.get("gradient") is not None or v.get("options") is not None)
            )
        }

        passed_colorByOptions = self.data.get("colorByOptions", {})
        passed_sizeByOptions = self.data.get("sizeByOptions", {})
        if not self.__check_subset_valid__(
            subset=list(passed_colorByOptions),
            valid_values=list(colorBy_availableProps.keys()),
            prepend_path=["colorByOptions"],
        ) or not self.__check_subset_valid__(
            subset=list(passed_sizeByOptions),
            valid_values=list(sizeBy_availableProps.keys()),
            prepend_path=["sizeByOptions"],
        ):
            return
        for by in ["colorBy", "sizeBy"]:
            by_value = self.data.get(by)
            if by_value is not None:
                available_options = self.data.get(f"{by}Options", {})
                if by_value not in available_options:
                    self.__error__(
                        msg=f"Invalid `{by}` ({by_value}) must be one of {available_options}"
                    )
        # TODO: Validate Icons
