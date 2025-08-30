"""
This module contains the primary Validator class that is used to validate your session_data against the API spec.
"""

from cave_utils.api_utils.validator_utils import LogObject
from cave_utils.api import Root
import type_enforced


@type_enforced.Enforcer
class Validator:
    def __init__(self, session_data, ignore_keys: list[str] = list(), **kwargs):
        """
        Util to validate your session_data against the API spec.

        Arguments:

        * **`session_data`**: `[dict]` &rarr; The data to validate.
            * **Note**: This should be the data you are sending to the server.
        * **`ignore_keys`**: `[list[str]]` = `None` &rarr; Keys to ignore when validating.
            * **Note**: Any keys specified here will be not be validated if encountered in the data at any level.
        """
        self.session_data = session_data
        self.log = LogObject()
        Root(data=self.session_data, log=self.log, prepend_path=[], ignore_keys=set(ignore_keys))
