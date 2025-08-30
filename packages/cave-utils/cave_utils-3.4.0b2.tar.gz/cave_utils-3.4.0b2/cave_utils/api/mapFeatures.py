"""
Create visualizations for your map, including `arc`s, `node`s, and `geo`s, and customize their appearance.
"""

from cave_utils.api_utils.validator_utils import ApiValidator, CustomKeyValidator
from cave_utils.api_utils.general import props, valueLists, layout
import type_enforced
from pamda import pamda


@type_enforced.Enforcer
class mapFeatures(ApiValidator):
    """
    The map features are located under the path **`mapFeatures`**.
    """

    @staticmethod
    def spec(data: dict = dict(), **kwargs):
        """
        Arguments:

        * **`data`**: `[dict]` = `{}` &rarr; The data to pass to `mapFeatures.data.*`.
        """
        return {"kwargs": kwargs, "accepted_values": {}}

    def __extend_spec__(self, **kwargs):
        data = self.data.get("data", {})
        CustomKeyValidator(
            data=data,
            log=self.log,
            prepend_path=["data"],
            validator=mapFeatures_data_star,
            **kwargs,
        )


@type_enforced.Enforcer
class mapFeatures_data_star(ApiValidator):
    """
    The map features data is located under the path **`mapFeatures.data.*`**.
    """

    @staticmethod
    def spec(
        type: str,
        name: str,
        props: dict,
        data: dict,
        layout: dict | None = None,
        geoJson: dict | None = None,
        **kwargs,
    ):
        """
        Arguments:

        * **`type`**: `[str]` &rarr; The type of the map feature.
            * **Accepted Values**:
                * `"arc"`: An `arc` layer
                * `"node"`: A `node` layer
                * `"geo"`: A `geo` layer
        * **`name`**: `[str]` &rarr; The name of the map feature.
        * **`props`**: `[dict]` &rarr; The props that will be rendered in the map feature.
            * **See**: `cave_utils.api_utils.general.props`
        * **`data`**: `[dict]` &rarr; The data that will be passed to the props.
            * **See**: `cave_utils.api_utils.general.values`
        * **`layout`**: `[dict]` =`{"type": "grid", "numColumns": "auto", "numRows": "auto"}` &rarr;
            * The layout of the map feature data presented in a map modal.
            * **See**: `cave_utils.api_utils.general.layout`
        * **`geoJson`**: `[dict]` =`{}` &rarr; A dictionary specifying the GeoJSON data to use.
            * **See**: `cave_utils.api.mapFeatures.mapFeatures_data_star_geoJson`
        """
        if type not in ["geo", "arc"]:
            if geoJson is not None:
                kwargs["geoJson"] = None
        return {"kwargs": kwargs, "accepted_values": {"type": ["arc", "node", "geo"]}}

    def __extend_spec__(self, **kwargs):
        props_data = self.data.get("props", {})
        CustomKeyValidator(
            data=props_data,
            log=self.log,
            prepend_path=["props"],
            validator=props,
            **kwargs,
        )
        data_data = self.data.get("data")
        if data_data is not None:
            mapFeatures_data_star_data(
                data=data_data,
                log=self.log,
                prepend_path=["data"],
                # Special Kwargs for passing props_data to valueLists
                props_data=props_data,
                # Special Kwargs for passing type and geoJson to location
                layer_type=self.data.get("type"),
                layer_geoJson=self.data.get("geoJson"),
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
        if self.data.get("type") in ["geo", "arc"]:
            geoJson_data = self.data.get("geoJson")
            if geoJson_data is not None:
                mapFeatures_data_star_geoJson(
                    data=geoJson_data,
                    log=self.log,
                    prepend_path=["geoJson"],
                    **kwargs,
                )


@type_enforced.Enforcer
class mapFeatures_data_star_data(ApiValidator):
    """
    The map features data is located under the path **`mapFeatures.data.*.data`**.
    """

    @staticmethod
    def spec(location: dict, valueLists: dict, **kwargs):
        """
        Arguments:

        * **`location`**: `[dict]` &rarr; The location lists of the map feature.
            * **See**: `cave_utils.api.mapFeatures.mapFeatures_data_star_data_location`
        * **`valueLists`**: `[dict]` &rarr; The value lists of the map feature.
            * **See**: `cave_utils.api_utils.general.valueLists`
        """
        return {"kwargs": kwargs, "accepted_values": {}}

    def __extend_spec__(self, **kwargs):
        valueLists_data = self.data.get("valueLists", {})
        valueLists(
            data=valueLists_data,
            log=self.log,
            prepend_path=["valueLists"],
            **kwargs,
        )
        location_data = self.data.get("location", {})
        mapFeatures_data_star_data_location(
            data=location_data,
            log=self.log,
            prepend_path=["location"],
            **kwargs,
        )
        # Validate that all lengths are the same
        lengths = [len(v) for k, v in location_data.items() if k not in ["timeValues", "order"]] + [
            len(v) for k, v in valueLists_data.items() if k not in ["timeValues", "order"]
        ]
        if len(set(lengths)) > 1:
            self.__error__(msg=f"location and valueLists keys must have the same length.", path=[])


@type_enforced.Enforcer
class mapFeatures_data_star_data_location(ApiValidator):
    """
    The map features data is located under the path **`mapFeatures.data.*.data.location`**.
    """

    @staticmethod
    def spec(
        latitude: list[list[float | int]] | None = None,
        longitude: list[list[float | int]] | None = None,
        altitude: list[list[float | int]] | None = None,
        path: list[list[list[float | int]]] | None = None,
        geoJsonValue: list[str] | None = None,
        **kwargs,
    ):
        """
        Arguments:

        * **`latitude`**: `list[list[float | int]]` = `None` &rarr; A list of latitudes for each node.
            * ** Example **: `[45.34, 46.27, 47.34, 48.34]`
            * ** Notes **: Used for `node` layers
        * **`longitude`**: `list[list[float | int]]` = `None` &rarr; A list of longitudes for each node.
            * ** Example **: `[120.34, 121.27, 122.34, 123.34]`
            * ** Note **: Used for `node` layers
        * **`altitude`**: `list[list[float | int]]` = `None` &rarr; The altitude for each node / geo in kilometers.
            * ** Example **: `[0, 1000, 2000, 3000]`
            * ** Notes **:
                * Used for `node` and `geo` layers
                * This is currently ignored but is planned to be supported in the future.
        * **`path`**: `list[list[list[float | int]]]` = `None` &rarr; A path for each arc in the format `[[long1,lat1,(optional alt1)],[long2,lat2,(optional alt2)],...]`.
            * ** Example **: `[[[0,0],[1,1]],[[2,2],[3,3],[4,4],[5,5]]]`
            * ** Example with Altitude **: `[[[0,0,0],[1,1,1000]],[[2,2,2000],[3,3,3000],[4,4,4000],[5,5,5000]]]`
            * ** Note **: Used for `arc` layers
        * **`geoJsonValue`**: `[list[str]]` = `None` &rarr; A list of geoJsonValue keys that correspond to the `properties` key specified as geoJsonProp in `mapFeatures.data.*.geoJson`.
            * ** Note **: Used for `arc`, `node`, and `geo` layers
        """
        return {
            "kwargs": {},
            "accepted_values": {},
        }

    def __extend_spec__(self, **kwargs):
        layer_type = kwargs.get("layer_type")
        layer_geoJson = kwargs.get("layer_geoJson")
        passed_keys = {k: v for k, v in self.data.items() if v is not None}
        optional_keys = []
        if layer_type in ["geo", "arc"]:
            if layer_geoJson is not None:
                required_keys = ["geoJsonValue"]
            else:
                required_keys = ["path"]
        else:
            required_keys = ["latitude", "longitude"]
            optional_keys += ["altitude"]
        missing_keys = pamda.difference(required_keys, list(passed_keys.keys()))
        if len(missing_keys) > 0:
            self.__error__(msg=f"Missing required keys: {missing_keys}", path=[])
            return
        for key, value_list in passed_keys.items():
            if key not in required_keys + optional_keys:
                self.__warn__(
                    msg=f"`{key}` is not a valid key for location with this configuration of layer type `{layer_type}`. Allowed keys are: {required_keys + optional_keys}",
                    path=[],
                )
                continue
            if key == "geoJsonValue":
                if len(value_list) != len(set(value_list)):
                    self.__warn__(
                        msg=f"`geoJsonValue` should be a list of unique values. Otherwise, the corresponding map feature may not render correctly.",
                        path=[key],
                    )
                continue

            latitudes = None
            longitudes = None
            altitudes = None
            if "path" in key.lower():
                try:
                    longitudes = [y[0] for x in value_list for y in x]
                    latitudes = [y[1] for x in value_list for y in x]
                    try:
                        altitudes = [y[2] for x in value_list for y in x]
                    except:
                        altitudes = None
                except:
                    self.__error__(
                        msg=f"`path` must be a list of lists of lists of length 2 [long,lat] or 3 [long,lat,alt]. EG: `[[[0,0],[1,1]],[[2,2],[3,3],[4,4],[5,5]]]`",
                        path=[key],
                    )
                    continue
            elif "latitude" in key.lower():
                latitudes = [i[0] for i in value_list]
            elif "longitude" in key.lower():
                longitudes = [i[0] for i in value_list]
            elif "altitude" in key.lower():
                altitudes = [i[0] for i in value_list]

            if latitudes is not None:
                if max(latitudes) > 90 or min(latitudes) < -90:
                    self.__error__(
                        msg=f"`{key}` has a latitude that is greater than 90 or less than -90.",
                        path=[key],
                    )
            if longitudes is not None:
                if max(longitudes) > 180 or min(longitudes) < -180:
                    self.__error__(
                        msg=f"`{key}` has a longitude that is greater than 180 or less than -180.",
                        path=[key],
                    )
            if altitudes is not None:
                if max(altitudes) > 10000 or min(altitudes) < 0:
                    self.__error__(
                        msg=f"`{key}` has an altitude that is greater than 10000 or less than 0",
                        path=[key],
                    )


@type_enforced.Enforcer
class mapFeatures_data_star_geoJson(ApiValidator):
    """
    The map feature GeoJSON data is located under the path **`mapFeatures.data.*.geoJson`**.
    """

    @staticmethod
    def spec(geoJsonLayer: str, geoJsonProp: str, **kwargs):
        """
        Arguments:

        * **`geoJsonLayer`**: `[str]` &rarr; The URL of the GeoJSON layer to use.
        * **`geoJsonProp`**: `[str]` &rarr;
            * The `properties` key (from the object fetched from the `geoJsonLayer` URL) to match with the value at `mapFeatures.data.*.data.location.geoJsonValue.*`.
        """
        return {"kwargs": kwargs, "accepted_values": {}}

    def __extend_spec__(self, **kwargs):
        self.__check_url_valid__(url=self.data.get("geoJsonLayer"), prepend_path=["geoJsonLayer"])
