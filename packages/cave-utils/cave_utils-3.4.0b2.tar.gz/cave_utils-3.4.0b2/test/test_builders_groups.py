from cave_utils.builders.groups import GroupsBuilder

group_data = [
    {"continent": "North America", "country": "USA", "state": "New York"},
    {"continent": "North America", "country": "USA", "state": "California"},
    {"continent": "North America", "country": "Canada", "state": "Ontario"},
    {"continent": "Europe", "country": "France", "state": "Paris"},
    {"continent": "Europe", "country": "France", "state": "Lyon"},
    {"continent": "Europe", "country": "Germany", "state": "Berlin"},
]
group_parents = {"state": "country", "country": "continent"}
group_names = {"continent": "Continents", "country": "Countries", "state": "States"}

success = {
    "init": False,
    "double_init": False,
    "serialize": False,
    "get_id": False,
    "bad_parents": False,
    "circular_group_parents": False,
    "bad_group_data": False,
    "id_col_serialize": False,
    "id_col_broken": False,
}

geo_builder = GroupsBuilder(
    group_name="Geography",
    group_data=group_data,
    group_parents=group_parents,
    group_names=group_names,
)
success["init"] = True

try:
    geo_builder = GroupsBuilder(
        group_name="Geography",
        group_data=group_data,
        group_parents=group_parents,
        group_names=group_names,
    )
    success["double_init"] = True
except:
    pass

expected_output = {
    "data": {
        "continent": [
            "North America",
            "North America",
            "North America",
            "Europe",
            "Europe",
            "Europe",
        ],
        "country": ["USA", "USA", "Canada", "France", "France", "Germany"],
        "id": ["0", "1", "2", "3", "4", "5"],
        "state": ["New York", "California", "Ontario", "Paris", "Lyon", "Berlin"],
    },
    "levels": {
        "continent": {"name": "Continents"},
        "country": {"name": "Countries", "parent": "continent"},
        "state": {"name": "States", "parent": "country"},
    },
    "name": "Geography",
    "order": {"data": ["continent", "country", "state"]},
}

if geo_builder.serialize() == expected_output:
    success["serialize"] = True

if geo_builder.get_id({"continent": "North America", "country": "USA", "state": "New York"}) == "0":
    success["get_id"] = True

bad_parents = {"state_mispelled": "country"}
circular_group_parents = {"state": "country", "country": "state"}
bad_group_data = group_data + [{"bad_record": "bad_value"}]

try:
    test_builder = GroupsBuilder(
        group_name="Geography",
        group_data=group_data,
        group_parents=bad_parents,
        group_names=group_names,
    )
except ValueError as e:
    success["bad_parents"] = True

try:
    test_builder = GroupsBuilder(
        group_name="Geography",
        group_data=group_data,
        group_parents=circular_group_parents,
        group_names=group_names,
    )
except ValueError as e:
    success["circular_group_parents"] = True


try:
    test_builder = GroupsBuilder(
        group_name="Geography",
        group_data=bad_group_data,
        group_parents=group_parents,
        group_names=group_names,
    )
except ValueError as e:
    success["bad_group_data"] = True

id_group_data = [
    {"id": "a", "continent": "North America", "country": "USA", "state": "New York"},
    {"id": "b", "continent": "North America", "country": "USA", "state": "California"},
    {"id": "c", "continent": "North America", "country": "Canada", "state": "Ontario"},
    {"id": "d", "continent": "Europe", "country": "France", "state": "Paris"},
    {"id": "e", "continent": "Europe", "country": "France", "state": "Lyon"},
    {"id": "f", "continent": "Europe", "country": "Germany", "state": "Berlin"},
]

geo_builder = GroupsBuilder(
    group_name="Geography",
    group_data=id_group_data,
    group_parents=group_parents,
    group_names=group_names,
)

expected_output = {
    "data": {
        "continent": [
            "North America",
            "North America",
            "North America",
            "Europe",
            "Europe",
            "Europe",
        ],
        "country": ["USA", "USA", "Canada", "France", "France", "Germany"],
        "id": ["a", "b", "c", "d", "e", "f"],
        "state": ["New York", "California", "Ontario", "Paris", "Lyon", "Berlin"],
    },
    "levels": {
        "continent": {"name": "Continents"},
        "country": {"name": "Countries", "parent": "continent"},
        "state": {"name": "States", "parent": "country"},
    },
    "name": "Geography",
    "order": {"data": ["continent", "country", "state"]},
}

if geo_builder.serialize() == expected_output:
    success["id_col_serialize"] = True

try:
    geo_builder = GroupsBuilder(
        group_name="Geography",
        group_data=[
            *id_group_data,
            {"id": "b", "continent": "North America", "country": "USA", "state": "New York"},
        ],
        group_parents=group_parents,
        group_names=group_names,
    )
except ValueError as e:
    success["id_col_broken"] = True

if all(success.values()):
    print("Builder Groups Tests: Passed!")
else:
    print("Builder Groups Tests: Failed!")
    print(success)
