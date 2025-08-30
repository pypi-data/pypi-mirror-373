"""
Special utility functions to help in validating your data against the CAVE API. This is not a key that should be passed as part of your `session_data`.
"""

from pamda import pamda
import type_enforced
import re, datetime
from cave_utils.log import LogHelper, LogObject


class ApiValidator:
    def __init__(self, **fields):
        self.__validate__(**fields)

    def spec(self, **kwargs):
        """
        The default `spec` method.

        This provides a baseline spec for some utility validators.

        This should be overridden by any non utility child class.
        """
        return {
            "kwargs": {},
            "accepted_values": {},
        }

    def __validate__(self, data: dict, log: LogObject, prepend_path: list[str] = list(), **kwargs):
        """
        Run the API validation process for the passed data.
        """
        # Make a copy of the data to avoid modifying the original
        self.data = {**data}
        self.ignore_keys = kwargs.get("ignore_keys", set())
        self.log = LogHelper(log=log, prepend_path=prepend_path)
        try:
            self.__genericKeyValidation__(**kwargs)
            spec_output = self.spec(**self.data)
            extra_kwargs = spec_output.get("kwargs", {})
            if extra_kwargs != {}:
                self.__warn__(
                    msg=f"Unknown Fields: {str(list(extra_kwargs.keys()))}",
                )

        except Exception as e:
            self.__error__(
                msg=f"Error validating spec: {e}",
            )
            # Must return since an invalid spec will bug out other validation checks
            return
        for field, accepted_values in spec_output.get("accepted_values", {}).items():
            if field not in self.data:
                continue
            check_value = self.data.get(field)
            if isinstance(check_value, dict):
                check_value = list(check_value.keys())
            if isinstance(check_value, str):
                check_value = [check_value]
            if isinstance(check_value, list):
                if self.__check_subset_valid__(
                    subset=check_value, valid_values=accepted_values, prepend_path=[field]
                ):
                    continue

        # Run additional Validations
        # self.__extend_spec__(**kwargs)
        try:
            self.__extend_spec__(**kwargs)
        except Exception as e:
            self.__error__(
                path=[],
                msg=f"Extended spec validations failed (likely due to another error with your API data). Error: {e}",
            )

    # Placeholder method for additional validations
    def __extend_spec__(self, **kwargs):
        pass

    # Additional core validations for generic terms like `order` and `timeValues`
    def __genericKeyValidation__(self, **kwargs):
        # Remove `timeValues` out prior to each level validation
        data_timeValues = self.data.pop("timeValues", None)
        # Remove `order` out prior to each level validation
        data_order = self.data.pop("order", None)
        if data_timeValues is not None:
            timeLength = kwargs.get("timeLength")
            if timeLength is None:
                self.__error__(
                    path=["timeValues"],
                    msg="`settings.time.timeLength` must be specified to validate `timeValues`",
                )
            else:
                self.__timeValues_validation__(timeValues=data_timeValues, timeLength=timeLength)
        if data_order is not None:
            self.__order_validation__(order=data_order)

    @type_enforced.Enforcer
    def __order_validation__(self, order: dict[str, list[str | int]]):
        """
        Check that the ordering options are valid
        """
        orderable_data_keys = {
            key: list(value.keys()) for key, value in self.data.items() if isinstance(value, dict)
        }
        if self.__check_subset_valid__(
            subset=list(order.keys()),
            valid_values=list(orderable_data_keys.keys()),
            prepend_path=["order"],
        ):
            for order_key, order_list in order.items():
                self.__check_subset_valid__(
                    subset=order_list,
                    valid_values=orderable_data_keys[order_key],
                    prepend_path=["order", order_key],
                )

    @type_enforced.Enforcer
    def __timeValues_validation__(self, timeValues: dict[int, dict] | list[dict], timeLength: int):
        if len(timeValues) == 0:
            return
        if isinstance(timeValues, list):
            if len(timeValues) != timeLength:
                self.__error__(
                    path=["timeValues"],
                    msg=f"The length of `timeValues` (as a list) must be equal to `settings.time.timeLength` ({timeLength})",
                )
                return
        if isinstance(timeValues, dict):
            keys = list(timeValues.keys())
            if not all(isinstance(key, int) for key in keys):
                self.__error__(
                    path=["timeValues"],
                    msg="`timeValues` (as a dict) keys must be integers",
                )
                return
            if not all(key >= 0 and key < timeLength for key in keys):
                self.__error__(
                    path=["timeValues"],
                    msg=f"`timeValues` (as a dict) keys must be integers between 0 and {timeLength-1} inclusive (1 minus the value at `settings.time.timeLength`)",
                )
                return
            timeValues = list(timeValues.values())
        timeValueTypes = {k: type(v) for k, v in timeValues[0].items()}
        for timeValue in timeValues:
            if timeValueTypes != {k: type(v) for k, v in timeValue.items()}:
                self.__error__(
                    path=["timeValues"],
                    msg="All timeValues must have the same keys and each key must have the same type",
                )
                return
        # Update the data with the first timeValue prioritizing original data
        # over the first timeValue
        self.data = {**timeValues[0], **self.data}

    # Error and Warning Helpers
    def __error__(self, msg: str, path: list[str] = list()):
        """
        Raise an error for the log the log
        """
        self.log.add(path=path, msg=msg)

    def __warn__(self, msg: str, path: list[str] = list()):
        """
        Raise a warning for the log the log
        """
        self.log.add(path=path, msg=msg, level="warning")

    # Useful Validator Checks
    def __check_color_string_valid__(self, color_string: str, prepend_path: list[str] = list()):
        """
        Validate a color string and if an issue is present, log an error
        """
        # Regular expression for HEX color (e.g., #000000 or #000)
        hex_pattern = r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
        # Regular expression for RGB color (e.g., rgb(0, 0, 0), rgb(0 0 0), or rgb(0,0,0), or rgb(0, 0, 0, 0) or rgba(0 0 0 0), ...)
        rgb_pattern = r"(?i)^rgba?\(\s*(\d{1,3})\s*(,\s*|\s+)(\d{1,3})\s*(,\s*|\s+)(\d{1,3})(?:\s*(,\s*|\s+)(0|1|0?\.\d+))?\s*\)$"
        # Regular expression for HSL color (e.g., hsl(0, 0%, 0%), hsl(0 0% 0%), or hsl(0,0%,0%))
        hsl_pattern = r"(?i)^hsl\(\s*(\d{1,3})\s*(,\s*|\s+)(\d{1,3})%\s*(,\s*|\s+)(\d{1,3})%\s*\)$"

        is_valid = False
        if re.match(hex_pattern, color_string):
            is_valid = True
        elif match := re.match(rgb_pattern, color_string):
            values = [value for value in match.groups() if match.groups().index(value) % 2 == 0]
            if all(0 <= int(value) <= 255 for value in values[:3]):
                is_valid = True
                # Check A values if present
                if len(values) == 4 and not (0 <= float(values[3]) <= 1):
                    is_valid = False
        elif match := re.match(hsl_pattern, color_string):
            values = [value for value in match.groups() if match.groups().index(value) % 2 == 0]
            if 0 <= int(match.group(1)) <= 360 and all(
                0 <= int(value) <= 100 for value in values[1:]
            ):
                is_valid = True
        else:
            is_valid = False

        if not is_valid:
            self.__error__(
                path=prepend_path,
                msg="Invalid color string. Must be in a valid RGB, HSL or HEX format.",
            )

    def __check_pixel_string_valid__(self, pixel_string: str, prepend_path: list[str] = list()):
        """
        Validate a pixel string and if an issue is present, log an error
        """
        msg = "Invalid pixel string. Must be in the format '5px' where the value portion is a whole number."
        try:
            if "px" != pixel_string[-2:]:
                self.__error__(path=prepend_path, msg=msg)
                return
            if int(pixel_string[:-2]) < 0:
                self.__error__(path=prepend_path, msg=msg)
        except:
            self.__error__(path=prepend_path, msg=msg)

    def __check_url_valid__(self, url: str, prepend_path: list[str] = list()):
        """
        Validate a url and if an issue is present, log an error.
        """
        # Use Django regex for URL validation
        # See https://stackoverflow.com/a/7160778/12014156
        regex = re.compile(
            r"^(?:http|ftp)s?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        if re.match(regex, url) is None:
            self.__error__(path=prepend_path, msg="Invalid url")
            return False
        return True

    def __check_date_valid__(self, input: str, date_variant: str, prepend_path: list[str] = list()):
        """
        Validate a date string and if an issue is present, log an error.
        """
        if date_variant == "date":
            try:
                datetime.datetime.strptime(input, "%Y-%m-%d")
            except ValueError:
                self.__error__(
                    path=prepend_path,
                    msg=f"Invalid input for type of `date` with variant `date`. Must be in the format `YYYY-MM-DD`",
                )
                return False
        elif date_variant == "datetime":
            try:
                datetime.datetime.strptime(input, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                self.__error__(
                    path=prepend_path,
                    msg=f"Invalid input for type of `date` with variant `datetime`. Must be in the format `YYYY-MM-DDTHH:MM:SS`",
                )
                return False
        elif date_variant == "time":
            try:
                datetime.datetime.strptime(input, "%H:%M:%S")
            except ValueError:
                self.__error__(
                    path=prepend_path,
                    msg=f"Invalid input for type of `date` with variant `time`. Must be in the format `HH:MM:SS`",
                )
                return False
        else:
            self.__error__(
                path=prepend_path,
                msg=f"Invalid variant ({date_variant}) for prop with type `date`. Must be one of `date`, `datetime`, or `time`",
            )
            return False
        return True

    def __prevent_subset_collision__(
        self, subset: list[str], invalid_values: list[str], prepend_path: list[str] = list()
    ):
        """
        Prevent a subset of values from colliding with a set of invalid values and if an issue is present, log an error

        Returns True if the subset check passed and False otherwise
        """
        invalid = pamda.intersection(subset, invalid_values)
        if len(invalid) > 0:
            self.__error__(
                path=prepend_path,
                msg=f"Invalid value(s) selected: {str(invalid)}. Reserved Values are {invalid_values}",
            )
            return False
        return True

    def __check_subset_valid__(
        self,
        subset: list,
        valid_values: list,
        prepend_path: list[str] = list(),
        valid_values_count: int = 6,
    ):
        """
        Validate a subset of values is in a set of valid values and if an issue is present, log an error

        Returns True if the subset check passed and False otherwise
        """
        invalid_values = pamda.difference(subset, valid_values)
        if len(invalid_values) > 0:
            valid_values = (
                valid_values[:valid_values_count] + ["..."]
                if len(valid_values) > valid_values_count
                else valid_values
            )
            self.__error__(
                path=prepend_path,
                msg=f"Invalid value(s) selected: {str(invalid_values)}. Accepted Values are {valid_values}",
            )
            return False
        return True

    def __check_coord_path_valid__(
        self,
        coord_path: list[list[int | float]],
        coord_variant: str,
        prepend_path: list[str] = list(),
    ):
        """
        Validate a coordinate path and if an issue is present, log an error
        """
        try:
            if (
                coord_variant == "latLngPath"
                and len(coord_path) < 2
                or coord_variant != "latLngPath"
                and len(coord_path) > 1
            ):
                self.__error__(path=prepend_path, msg="Invalid coordinate path")
                return
            for coord in coord_path:
                # Ensure coord is less than 3 items (longitude, latitude, altitude)
                if len(coord) > 3:
                    self.__error__(path=prepend_path, msg="Invalid coordinate path")
                    return
                # Check Longitude
                if coord[0] < -180 or coord[0] > 180:
                    self.__error__(path=prepend_path, msg="Invalid coordinate path")
                    return
                # Check Latitude
                if coord[1] < -90 or coord[1] > 90:
                    self.__error__(path=prepend_path, msg="Invalid coordinate path")
                    return
                # Check Altitude (if present)
                if len(coord) == 3:
                    if coord[2] < 0:
                        self.__error__(path=prepend_path, msg="Invalid coordinate path")
                        return
        except:
            self.__error__(path=prepend_path, msg="Invalid coordinate path")

    def __check_type_list__(self, data: list, types: tuple, prepend_path: list = list()):
        """
        Validate a list only contains certain object types and if an issue is present, log an error

        Returns True if the type check passed and False otherwise
        """
        if not isinstance(types, tuple):
            types = (types,)
        for idx, item in enumerate(data):
            if not isinstance(item, types):
                self.__error__(
                    path=prepend_path,
                    msg=f"Invalid list item type at index: {idx} with type: {type(item)}. Expected one of {types}",
                )
                return False
        return True

    def __check_type_dict__(self, data: dict, types: tuple, prepend_path: list[str] = list()):
        """
        Validate a dict only contains certain object types for values and if an issue is present, log an error

        Returns True if the type check passed and False otherwise
        """
        if not isinstance(types, tuple):
            types = (types,)
        for key, value in data.items():
            if not isinstance(value, types):
                self.__error__(
                    path=prepend_path,
                    msg=f"Invalid dict item type at key: {key} with type: {type(value)}. Expected one of {types}",
                )
                return False
        return True

    def __check_type__(self, value, check_type, prepend_path: list[str] = list()):
        """
        Validate a value is a certain type and if an issue is present, log an error

        Returns True if the type check passed and False otherwise

        Required Arguments:

        - `value`:
            - Type: any
            - What: The value to check.
        - `check_type`:
            - Type: type | tuple of types
            - What: The type(s) to check against.

        Optional Arguments:

        - `prepend_path`:
            - Type: list
            - What: The path to prepend to the error message.
            - Default: `[]`
        """
        if not isinstance(value, check_type):
            self.__error__(
                msg=f"({value}) Invalid Type: Expected one of {check_type} but got type {type(value)} instead.",
                path=prepend_path,
            )
            return False
        return True


@type_enforced.Enforcer
class CustomKeyValidator(ApiValidator):
    @staticmethod
    def spec(**kwargs):
        for k, v in kwargs.items():
            if not isinstance(v, dict):
                raise Exception(
                    f"Error for field ({k}): Type {type(dict())} is required but instead received {type(v)}"
                )
        return {
            "kwargs": {},
            "accepted_values": {},
        }

    def __extend_spec__(self, **kwargs):
        validator = kwargs.get("validator")
        assert validator is not None, "Must pass validator to CustomKeyValidator"
        kwargs = {
            k: v for k, v in kwargs.items() if k not in ["validator", "CustomKeyValidatorFieldId"]
        }
        for field, value in self.data.items():
            validator(
                data=value,
                log=self.log,
                prepend_path=[field],
                CustomKeyValidatorFieldId=field,
                **kwargs,
            )
