from pamda import pamda
import type_enforced
from datetime import datetime, timedelta


class GroupsUtils:
    def serialize(self):
        """
        Serialize the group structure to a dictionary of the proper format.

        Returns:
        * `[dict]` &rarr; The serialized group structure.
        """
        return {
            "name": self.group_name,
            "order": {"data": self.group_keys},
            "data": self.data_structure,
            "levels": self.levels_structure,
        }

    def get_id_list(self):
        """
        Get the list of ids for the groups in the same order as the provided group_data.

        Returns:
        * `[list]` &rarr; The list of ids for the groups in the same order as the provided group_data.
        """
        if isinstance(self, DateGroupsBuilder):
            return self.date_data
        elif isinstance(self, GroupsBuilder):
            return [self.get_id(i) for i in self.group_data]
        else:
            raise NotImplementedError(
                "This function is not supported with this type of GroupsBuilder."
            )


@type_enforced.Enforcer
class GroupsBuilder(GroupsUtils):
    def __init__(
        self,
        group_name: str,
        group_data: list[dict[str, str]],
        group_parents: dict[str, str],
        group_names: dict[str, str],
    ) -> None:
        """
        Initialize a group builder.

        Arguments:

        * **`group_name`**: `[str]` &rarr; The name of the group.
        * **`group_data`**: `[list[dict[str, str]]]` &rarr; The data to use to build the group.
            * **Note**: This should be a list of dictionaries where each dictionary represents a combination of group keys and values.
            * **Note**: The keys in the dictionaries should be the same for all records.
            * **Note**: If the key `id` is specified, it will be used as the id for the group and not included in the group data.
            * **Example**: `[{'key1': 'value1', 'key2': 'value2'}, {'key1': 'value3', 'key2': 'value4'}]`
        * **`group_parents`**: `[dict[str, str]]` &rarr; Parent allocations to make for groups.
            * **Note**: This should be a dictionary where the keys are the child group keys and the values are the parent group keys.
            * **Example**: `{'child_key': 'parent_key'}`
                * **Note**: This would mean that `child_key` has a parent of `parent_key`.
            * **Note**: If a group is not a child of another group, it should not be included in the dictionary.
        * **`group_names`**: `[dict[str, str]]` &rarr; The group names to use for the group keys.
            * **Note**: This should be a dictionary where the keys are the group keys and the values are the group_names to use for the group keys.


        Returns:

        * `[GroupsBuilder]` &rarr; The initialized GroupsBuilder object.
        """
        self.group_name = group_name
        self.group_keys_all = list(group_data[0].keys())
        self.group_keys = [i for i in self.group_keys_all if i != "id"]
        self.group_parents = group_parents
        self.group_names = group_names
        self.group_data = [dict(i) for i in group_data]
        self.__validate_group_data__()
        self.__validate_parent_data__()
        self.__validate_name_data__()
        self.__gen_structures__()

    def __validate_group_data__(self):
        """
        Validate the group data to ensure it is in the proper format.

        Raises:

        * **`ValueError`** &rarr; If the group data is not in the proper format.
        """
        for record in self.group_data:
            if list(record.keys()) != self.group_keys_all:
                raise ValueError(
                    "Group data must have the same keys in the same order for all records."
                )

    def __validate_name_data__(self):
        """
        Validate the name data to ensure it is in the proper format.

        Raises:

        * **`ValueError`** &rarr; If the name data is not in the proper format.
        """
        bad_keys = pamda.difference(self.group_keys, list(self.group_names.keys()))
        if len(bad_keys) > 0:
            raise ValueError(
                f"You specified group data keys {bad_keys}, but they are not specified in group_names."
            )

    def __validate_parent_data__(self):
        """
        Validate the parent data to ensure it is in the proper format.

        Raises:

        * **`ValueError`** &rarr; If the parent data is not in the proper format.
        """
        parent_values = list(self.group_parents.values())
        child_values = list(self.group_parents.keys())
        root_keys = pamda.difference(self.group_keys, child_values)
        if len(root_keys) < 1:
            raise ValueError(
                "No root keys found in parent data. At least one key must be a root key and have no parent."
            )
        bad_keys = pamda.difference(child_values, self.group_keys) + pamda.difference(
            parent_values, self.group_keys
        )
        if len(bad_keys) > 0:
            raise ValueError(
                f"The keys and values {list(set(bad_keys))} were passed in the group_parents dict, but not found as keys in the group data."
            )
        for key, value in self.group_parents.items():
            if key == value:
                raise ValueError(f"Parent key '{key}' cannot be the same as the parent value.")
        for key in child_values:
            idx = 0
            while True:
                if idx > len(self.group_keys):
                    raise ValueError(f"A circular reference was found in your parent data.")
                if key in self.group_parents:
                    key = self.group_parents[key]
                    idx += 1
                else:
                    break

    def __gen_structures__(self):
        """
        Generate the group structures.

        Arguments:

        * **`group_data`**: `[list[dict[str, str]]]` &rarr; The data to use to build the group.


        Modifies:

        * **`self.id_structure`**: `[dict]` &rarr; The structure to use to get the id of a group.
        * **`self.data_structure`**: `[dict]` &rarr; The serialized data strucutre given the group_data.
        * **`self.levels_structure`**: `[dict]` &rarr; The structure to use to get the levels of a group.

        Returns:

        * `[None]`
        """
        groups_data = pamda.groupKeys(keys=self.group_keys, data=self.group_data)
        # Validate that the id is consistent if it is specified
        if "id" in self.group_keys_all:
            for group in groups_data:
                if len(set(pamda.pluck("id", group))) > 1:
                    raise ValueError(
                        f"The 'id' key has different values for items that are supposed to be in the same group. This is not allowed."
                    )
        # Get only relevant data from each group
        groups = [i[0] for i in groups_data]
        self.id_structure = {}
        for idx, group in enumerate(groups):
            id = group.pop("id", str(idx))
            self.id_structure = pamda.assocPath(
                path=list(group.values()), value=id, data=self.id_structure
            )
            group["id"] = id
        self.data_structure = pamda.pivot(groups)

        self.levels_structure = {}
        for idx, key in enumerate(self.group_keys):
            self.levels_structure[key] = {
                "name": self.group_names[key],
            }
            if key in self.group_parents:
                self.levels_structure[key]["parent"] = self.group_parents[key]

    def get_id(self, group: dict[str, str]):
        return pamda.path(path=pamda.props(self.group_keys, group), data=self.id_structure)


@type_enforced.Enforcer
class DateGroupsBuilder(GroupsUtils):
    def __init__(
        self,
        group_name: str,
        date_data: list[str],
        date_format: str = "%Y-%m-%d",
        include_year: bool = True,
        include_year_month: bool = True,
        include_year_month_day: bool = True,
        include_year_week: bool = False,
        include_year_day: bool = False,
        include_month: bool = True,
        include_month_week: bool = False,
        include_month_day: bool = False,
        include_week_day: bool = True,
    ) -> None:
        """
        Initialize a date group builder.

        Arguments:

        * **`group_name`**: `[str]` &rarr; The name of the group.
        * **`date_data`**: `[list[str]]` &rarr; The list of dates to use to build the group.
            * **Note**: This should be a list of strings where each string is a date in the format specified by `date_format`.
        * **`date_format`**: `[str]` = `"%Y-%m-%d"` &rarr; The format of the dates in `date_data`.
        * **`include_year`**: `[bool]` = `True` &rarr; Whether or not to include the year in the group.
        * **`include_year_month`**: `[bool]` = `True` &rarr; Whether or not to include the year and month in the group.
        * **`include_year_month_day`**: `[bool]` = `True` &rarr; Whether or not to include the year, month, and day in the group.
        * **`include_year_week`**: `[bool]` = `False` &rarr; Whether or not to include the year and week in the group.
        * **`include_year_day`**: `[bool]` = `False` &rarr; Whether or not to include the year and day in the group.
        * **`include_month`**: `[bool]` = `True` &rarr; Whether or not to include the month in the group.
        * **`include_month_week`**: `[bool]` = `False` &rarr; Whether or not to include the month and week in the group.
        * **`include_month_day`**: `[bool]` = `False` &rarr; Whether or not to include the month and day in the group.
        * **`include_week_day`**: `[bool]` = `True` &rarr; Whether or not to include the week day in the group.

        Returns:

        * `[DateGroupsBuilder]` &rarr; The initialized DateGroupsBuilder object.
        """
        self.group_name = group_name
        self.date_data = date_data
        self.date_format = date_format
        self.include_year = include_year
        self.include_year_month = include_year_month
        self.include_year_month_day = include_year_month_day
        self.include_year_week = include_year_week
        self.include_year_day = include_year_day
        self.include_month = include_month
        self.include_month_week = include_month_week
        self.include_month_day = include_month_day
        self.include_week_day = include_week_day
        self.date_objects = self.__get_date_objects__(date_data=date_data)
        self.__gen_structures__()

    def __get_date_objects__(self, date_data):
        """
        Get the date objects from the date data.

        Arguments:

        * **`date_data`**: `[list[str]]` &rarr; The list of dates to use to build the group.

        Returns:

        * `[list[datetime]]` &rarr; The list of date objects.
        """
        date_objects_raw = [datetime.strptime(date, self.date_format) for date in date_data]
        max_date = max(date_objects_raw)
        min_date = min(date_objects_raw)
        date_objects = [min_date + timedelta(days=i) for i in range((max_date - min_date).days + 1)]
        return date_objects

    def __gen_structures__(self):
        """
        Generate the group structures.

        Modifies:

        * **`self.data_structure`**: `[dict]` &rarr; The serialized data structure given the group_data.
        * **`self.levels_structure`**: `[dict]` &rarr; The structure to use to get the levels of a group.
        * **`self.group_keys`**: `[list[str]]` &rarr; The keys of the group.

        Returns:

        * `[None]`
        """
        self.data_structure = {
            "id": [i.strftime(self.date_format) for i in self.date_objects],
        }
        self.levels_structure = {}
        self.group_keys = []
        if self.include_year:
            self.levels_structure["year"] = {
                "name": "Year",
                "ordering": sorted(list(set([i.year for i in self.date_objects]))),
            }
            self.data_structure["year"] = [i.year for i in self.date_objects]
            self.group_keys.append("year")
        if self.include_year_month:
            self.levels_structure["year_month"] = {
                "name": "Year Month",
                "ordering": sorted(list(set([i.strftime("%Y-%m") for i in self.date_objects]))),
            }
            self.data_structure["year_month"] = [i.strftime("%Y-%m") for i in self.date_objects]
            self.group_keys.append("year_month")
        if self.include_year_month_day:
            self.levels_structure["year_month_day"] = {
                "name": "Year Month Day",
                "ordering": sorted(list(set([i.strftime("%Y-%m-%d") for i in self.date_objects]))),
            }
            self.data_structure["year_month_day"] = [
                i.strftime("%Y-%m-%d") for i in self.date_objects
            ]
            self.group_keys.append("year_month_day")
        if self.include_year_week:
            self.levels_structure["year_week"] = {
                "name": "Year Week",
                "ordering": sorted(list(set([i.strftime("%Y-%U") for i in self.date_objects]))),
            }
            self.data_structure["year_week"] = [i.strftime("%Y-%U") for i in self.date_objects]
            self.group_keys.append("year_week")
        if self.include_year_day:
            self.levels_structure["year_day"] = {
                "name": "Year Day",
                "ordering": sorted(list(set([i.strftime("%Y-%j") for i in self.date_objects]))),
            }
            self.data_structure["year_day"] = [i.strftime("%Y-%j") for i in self.date_objects]
            self.group_keys.append("year_day")
        if self.include_month:
            self.levels_structure["month"] = {
                "name": "Month",
                "ordering": sorted(list(set([i.strftime("%m") for i in self.date_objects]))),
            }
            self.data_structure["month"] = [i.strftime("%m") for i in self.date_objects]
            self.group_keys.append("month")
        if self.include_month_week:
            self.levels_structure["month_week"] = {
                "name": "Month Week",
                "ordering": sorted(list(set([i.strftime("%m-%U") for i in self.date_objects]))),
            }
            self.data_structure["month_week"] = [i.strftime("%m-%U") for i in self.date_objects]
            self.group_keys.append("month_week")
        if self.include_month_day:
            self.levels_structure["month_day"] = {
                "name": "Month Day",
                "ordering": sorted(list(set([i.strftime("%m-%d") for i in self.date_objects]))),
            }
            self.data_structure["month_day"] = [i.strftime("%m-%d") for i in self.date_objects]
            self.group_keys.append("month_day")
        if self.include_week_day:
            self.levels_structure["week_day"] = {
                "name": "Week Day",
                "ordering": sorted(list(set([i.strftime("%w") for i in self.date_objects]))),
            }
            self.data_structure["week_day"] = [i.strftime("%w") for i in self.date_objects]
            self.group_keys.append("week_day")

    def get_id(self, *args, **kwargs):
        """
        Ensure that the get_id function is not called with date Groups.
        """
        raise NotImplementedError("This function is not supported with date Groups.")
