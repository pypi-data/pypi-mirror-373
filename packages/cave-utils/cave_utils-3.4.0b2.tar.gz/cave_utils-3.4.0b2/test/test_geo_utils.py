from scgraph.geographs.us_freeway import us_freeway_geograph

from cave_utils import GeoUtils
import random

random.seed(42)

try:
    bounding_box = [[33, -117], [42, -79]]
    grid_size = [100, 100]

    num_routes = 100

    min_latitude = min(bounding_box[0][0], bounding_box[1][0])
    min_longitude = min(bounding_box[0][1], bounding_box[1][1])
    latitude_increment = abs(bounding_box[1][0] - bounding_box[0][0]) / grid_size[0]
    longitude_increment = abs(bounding_box[1][1] - bounding_box[0][1]) / grid_size[1]

    latitude_options = [
        round(min_latitude + i * latitude_increment, 2) for i in range(grid_size[0])
    ]
    longitude_options = [
        round(min_longitude + i * longitude_increment, 2) for i in range(grid_size[1])
    ]

    origin_latitudes = []
    origin_longitudes = []
    destination_latitudes = []
    destination_longitudes = []
    ids = []

    for idx in range(num_routes):
        origin_lat_id = random.randint(0, grid_size[0] - 1)
        origin_lon_id = random.randint(0, grid_size[1] - 1)
        destination_lat_id = random.randint(0, grid_size[0] - 1)
        destination_lon_id = random.randint(0, grid_size[1] - 1)

        origin_latitudes.append(latitude_options[origin_lat_id])
        origin_longitudes.append(longitude_options[origin_lon_id])
        destination_latitudes.append(latitude_options[destination_lat_id])
        destination_longitudes.append(longitude_options[destination_lon_id])
        ids.append(f"{origin_lat_id}_{origin_lon_id}_{destination_lat_id}_{destination_lon_id}")

    out = GeoUtils.create_shortest_paths_geojson(
        geoGraph=us_freeway_geograph,
        ids=ids,
        origin_latitudes=origin_latitudes,
        origin_longitudes=origin_longitudes,
        destination_latitudes=destination_latitudes,
        destination_longitudes=destination_longitudes,
        show_progress=False,
        # filename="test.geojson"
    )
    print("GeoUtils Tests: Passed!")
except Exception as e:
    print("GeoUtils Tests: Failed!")
    print(f"Error: {e}")
    raise e
