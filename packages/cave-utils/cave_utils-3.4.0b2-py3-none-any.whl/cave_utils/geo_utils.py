from pamda import pamda
import type_enforced


class GeoUtils:
    @type_enforced.Enforcer
    @staticmethod
    def create_shortest_paths_geojson(
        geoGraph,
        ids: list[int | str],
        origin_latitudes: list[int | float],
        origin_longitudes: list[int | float],
        destination_latitudes: list[int | float],
        destination_longitudes: list[int | float],
        additional_properties: list[dict] | None = None,
        show_progress: bool = False,
        filename: str | None = None,
        **kwargs,
    ):
        """
        Creates a geoJson output with the shortest paths between a list of
        origin and destination points.

        Arguments:

        * **`geoGraph`**: `[geoGraph]` &rarr; A geoGraph object from scgraph.
        * **`ids`**: `[list[int | str]]` &rarr; A list of identifiers for each path.
            * Note: These are imputed into the output GeoJSON as an id property.
        * **`origin_latitudes`**: `[list[int | float]]` &rarr;
            * A list of latitudes for the origin points.
        * **`origin_longitudes`**: `[list[int | float]]` &rarr;
            * A list of longitudes for the origin points.
        * **`destination_latitudes`**: `[list[int | float]]` &rarr;
            * A list of latitudes for the destination points.
        * **`destination_longitudes`**: `[list[int | float]]` &rarr;
            * A list of longitudes for the destination points.
        * **`additional_properties`**: `[list[dict] | None]` &rarr;
            * A list of dictionaries with additional properties for each path.
            * Note: The dictionaries must have the same length as the input lists.
            * Note: The dictionaries are imputed into the output GeoJSON as properties.
        * **`show_progress`**: `[bool]` = `False` &rarr;
            * If `True`, shows the progress of the calculations.
        * **`filename`**: `[str | None]` = `None` &rarr;
            * If provided, saves the output GeoJSON to the specified filename.

        Returns:

        * **`output`**: `[dict]` &rarr; A GeoJSON dictionary with the shortest paths given the input data.
        """
        if not hasattr(geoGraph, "get_shortest_path"):
            raise ValueError("`geoGraph` must be a geoGraph object from scgraph")
        len_items = len(ids)
        if additional_properties is None:
            additional_properties = [{} for i in range(len_items)]
        data = {
            "ids": ids,
            "origin_latitudes": origin_latitudes,
            "origin_longitudes": origin_longitudes,
            "destination_latitudes": destination_latitudes,
            "destination_longitudes": destination_longitudes,
            "additional_properties": additional_properties,
        }
        # Check that all the lists have at least one element
        if len_items == 0:
            raise ValueError("All input lists must have at least one element")
        # Check that all the lists have the same length
        if len(set(map(len, data.values()))) != 1:
            raise ValueError("All input lists must have the same length")
        features = []
        # Iterate over the data and calculate the shortest path for
        # each origin and destination pair
        for idx, item in enumerate(pamda.pivot(data)):
            item = dict(item)
            shortest_path_output = geoGraph.get_shortest_path(
                origin_node={
                    "latitude": item["origin_latitudes"],
                    "longitude": item["origin_longitudes"],
                },
                destination_node={
                    "latitude": item["destination_latitudes"],
                    "longitude": item["destination_longitudes"],
                },
                output_coordinate_path="list_of_lists_long_first",
                cache=True,
                **kwargs,
            )
            # Append the calculated path to the features list in GeoJSON format
            features.append(
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": shortest_path_output["coordinate_path"],
                    },
                    "properties": {
                        "id": item["ids"],
                        "length": shortest_path_output["length"],
                        **item["additional_properties"],
                    },
                }
            )
            if show_progress:
                print(f"Paths Calculated: {idx}/{len_items}", end="\r")
        if show_progress:
            print(f"Paths Calculated: {len_items}/{len_items}")
        # Create the GeoJSON output
        output = {"type": "FeatureCollection", "features": features}
        if filename is not None:
            pamda.write_json(data=output, filename=filename)
        return output
