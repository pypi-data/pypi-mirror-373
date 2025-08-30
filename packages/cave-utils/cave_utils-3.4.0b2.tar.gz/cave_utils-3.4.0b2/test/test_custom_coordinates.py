from cave_utils import CustomCoordinateSystem

success = {
    "init": False,
    "bad_init": False,
    "serialize_coordinates": False,
    "serialize_nodes": False,
    "serialize_arcs": False,
    "bad_list_coordinates": False,
    "bad_dict_coordinates": False,
}

TOLERANCE = 0.1  # Expected coordinates are approximate

try:
    # Square (width = height)
    square_coordinate_system = CustomCoordinateSystem(1000, 1000)
    square_coordinates = [[0, 0], [200, 500], [500, 500], [750, 750]]
    expected_square_long_lat = [[-180, -85.05], [-108, 0], [0, 0], [90, 66.513]]
    actual_square_long_lat = square_coordinate_system.serialize_coordinates(square_coordinates)

    for index, actual_coordinate in enumerate(actual_square_long_lat):
        expected_coordinate = expected_square_long_lat[index]
        assert abs(actual_coordinate[0] - expected_coordinate[0]) < TOLERANCE
        assert abs(actual_coordinate[1] - expected_coordinate[1]) < TOLERANCE

    success["serialize_coordinates"] = True

    expected_square_location = {
        "latitude": [[-85.05], [0], [0], [66.513]],
        "longitude": [[-180], [-108], [0], [90]],
    }
    actual_square_location = square_coordinate_system.serialize_nodes(square_coordinates)

    for key in expected_square_location:
        assert key in actual_square_location
        for index, value in enumerate(expected_square_location[key]):
            assert abs(actual_square_location[key][index][0] - value[0]) < TOLERANCE

    # Landscape (width > height)
    landscape_coordinate_system = CustomCoordinateSystem(576, 360, 1000)
    landscape_coordinates = {
        "x": [0, 72, 288, 396, 432, 504, 252],
        "y": [180, 180, 180, 180, 216, 108, 36],
        "z": [0, 1000, 5, 0, 0, 390.5, 123],
    }
    expected_landscape_location = {
        "latitude": [[0], [0], [0], [0], [21.95], [-41], [-66.5]],
        "longitude": [[-180], [-135], [0], [67.5], [90], [135], [-22.5]],
        "altitude": [[0], [10000], [50], [0], [0], [3905], [1230]],
    }
    actual_landscape_location = landscape_coordinate_system.serialize_nodes(landscape_coordinates)

    for key in expected_landscape_location:
        assert key in actual_landscape_location
        for index, value in enumerate(expected_landscape_location[key]):
            assert abs(actual_landscape_location[key][index][0] - value[0]) < TOLERANCE

    success["serialize_nodes"] = True

    # Portrait (height > width)
    portrait_coordinate_system = CustomCoordinateSystem(100, 200, 200)
    success["init"] = True

    ## Test arcs
    portrait_coordinates_list = [
        [[0, 0, 0], [0, 100, 0]],
        [[0, 125, 0], [20, 100, 100], [75, 125, 150]],
    ]
    portrait_coordinates_dict = [
        {"x": [0, 0], "y": [0, 100], "z": [0, 0]},
        {"x": [0, 20, 75], "y": [125, 100, 125], "z": [0, 100, 150]},
    ]
    expected_portrait_location = {
        "path": [[[-90, -85.05, 0], [-90, 0, 0]], [[-90, 41, 0], [-54, 0, 5000], [45, 41, 7500]]]
    }
    actual_portrait_location_list = portrait_coordinate_system.serialize_arcs(
        portrait_coordinates_list
    )
    actual_portrait_location_dict = portrait_coordinate_system.serialize_arcs(
        portrait_coordinates_dict
    )

    assert "path" in actual_portrait_location_list and "path" in actual_portrait_location_dict
    assert (
        len(expected_portrait_location["path"])
        == len(actual_portrait_location_list["path"])
        == len(actual_portrait_location_dict["path"])
    )
    for arc_index, arc in enumerate(expected_portrait_location["path"]):
        assert (
            len(expected_portrait_location["path"][arc_index])
            == len(actual_portrait_location_list["path"][arc_index])
            == len(actual_portrait_location_dict["path"][arc_index])
        )
        for coordinate_index, coordinate in enumerate(arc):
            actual_coordinate_list = actual_portrait_location_list["path"][arc_index][
                coordinate_index
            ]
            actual_coordinate_dict = actual_portrait_location_dict["path"][arc_index][
                coordinate_index
            ]
            for index, expected_value in enumerate(coordinate):
                assert abs(actual_coordinate_list[index] - expected_value) < TOLERANCE
                assert abs(actual_coordinate_dict[index] - expected_value) < TOLERANCE

    success["serialize_arcs"] = True

except Exception as e:
    # raise e
    pass


def bad_init_length():
    CustomCoordinateSystem(0, 100)


def bad_init_width():
    CustomCoordinateSystem(250.05, -10)


def bad_init_height():
    CustomCoordinateSystem(100, 1, 0)


def bad_init_multiple():
    CustomCoordinateSystem(250, 0, -5)


bad_init_tests = [bad_init_length, bad_init_width, bad_init_height, bad_init_multiple]

all_bad_init_tests_failed = True

for test in bad_init_tests:
    try:
        test()
        all_bad_init_tests_failed = False
        # print(f"Test {test.__name__} passed unexpectedly.")
        break
    except ValueError as e:
        continue

if all_bad_init_tests_failed:
    success["bad_init"] = True

coordinate_system = CustomCoordinateSystem(100, 1000, 1000)


def list_missing_altitude():
    coordinate_system.__validate_list_coordinates__(
        [[0, 0, 0], [93.5, 99.1, 23], [76.55, 350, 35], [12.01, 12.01]]
    )


def list_out_of_range():
    coordinate_system.__validate_list_coordinates__([[0, 0, -1], [930.5, 99.1, 23]])


def list_path_missing_altitude_1():
    coordinate_system.serialize_arcs(
        [[[0, 0, 0], [93.5, 99.1, 23]], [[76.55, 350], [12.01, 12.01, 12.01]]]
    )


def list_path_missing_altitude_2():
    coordinate_system.serialize_arcs(
        [[[0, 0, 0], [93.5, 99.1, 23]], [[76.55, 350], [12.01, 12.01]]]
    )


def list_path_out_of_range():
    coordinate_system.serialize_arcs(
        [[[0, 0, 0], [93.5, 99.1, 200]], [[76.55, 1000.1, 30], [12.01, 12.01, 30]]]
    )


bad_list_coordinates_tests = [
    list_missing_altitude,
    list_out_of_range,
    list_path_missing_altitude_1,
    list_path_missing_altitude_2,
    list_path_out_of_range,
]

all_list_tests_failed = True

for test in bad_list_coordinates_tests:
    try:
        test()
        all_list_tests_failed = False
        # print(f"Test {test.__name__} passed unexpectedly.")
        break
    except ValueError as e:
        continue

if all_list_tests_failed:
    success["bad_list_coordinates"] = True


def dict_missing_altitude():
    coordinate_system.__validate_dict_coordinates__(
        {"x": [0, 103.5, 76.55, 12.01], "y": [0, 99.1, 350, 12.01], "z": [0, 1, 0.2]}
    )


def dict_missing_latitude():
    coordinate_system.__validate_dict_coordinates__(
        {"x": [0, 103.5, 76.55, 12.01], "y": [0, 99.1, 12.01], "z": [0, 1, 0.2, 36]}
    )


def dict_missing_longitude():
    coordinate_system.__validate_dict_coordinates__(
        {"x": [103.5, 76.55, 12.01], "y": [0, 99.1, 350, 12.01], "z": [0, 1, 0.2, 36]}
    )


def dict_out_of_range():
    coordinate_system.__validate_dict_coordinates__(
        {"x": [0, 103.5, 76.55, 12.01], "y": [0, 99.1, 350, 12.01], "z": [0, 120, -0.2, 36]}
    )


def dict_path_missing_altitude_1():
    coordinate_system.serialize_arcs(
        [
            {"x": [0, 103.5], "y": [0, 99.1], "z": [0, 23]},
            {"x": [76.55, 12.01], "y": [350, 12.01], "z": [12.01]},
        ]
    )


def dict_path_missing_altitude_2():
    coordinate_system.serialize_arcs(
        [{"x": [0, 103.5], "y": [0, 99.1], "z": [0, 23]}, {"x": [76.55, 12.01], "y": [350, 12.01]}]
    )


def dict_path_out_of_range():
    coordinate_system.serialize_arcs(
        [
            {"x": [0, 103.5], "y": [0, 99.1], "z": [0, 200]},
            {"x": [76.55, 12.01], "y": [1000.1, 12.01], "z": [30, 30]},
        ]
    )


bad_dict_coordinates_tests = [
    dict_missing_altitude,
    dict_missing_latitude,
    dict_missing_longitude,
    dict_out_of_range,
    dict_path_missing_altitude_1,
    dict_path_missing_altitude_2,
    dict_path_out_of_range,
]
all_dict_tests_failed = True

for test in bad_dict_coordinates_tests:
    try:
        test()
        all_dict_tests_failed = False
        # print(f"Test {test.__name__} passed unexpectedly.")
        break
    except ValueError as e:
        continue

if all_dict_tests_failed:
    success["bad_dict_coordinates"] = True

if all(success.values()):
    print("Custom Coordinates Tests: Passed!")
else:
    print("Custom Coordinates Tests: Failed!")
    print(success)
    raise Exception(
        "Custom coordinates tests failed for one or more examples. Uncomment the print statements in test/custom_coordinates.py to see the errors."
    )
