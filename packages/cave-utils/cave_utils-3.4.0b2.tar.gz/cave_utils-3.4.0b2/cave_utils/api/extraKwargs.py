"""
Optionally, pass special arguments to adjust some options related to
how the CAVE API server handles data.
"""

from cave_utils.api_utils.validator_utils import ApiValidator
import type_enforced


@type_enforced.Enforcer
class extraKwargs(ApiValidator):
    """
    The special arguments are located under the path **`extraKwargs`**.
    """

    @staticmethod
    def spec(wipeExisting: bool = False, **kwargs):
        """
        Arguments:

        * **`wipeExisting`**: `[bool]` = `False` &rarr;
            * If set to `True`, all existing data will be deleted just
            before session data updates are merged. By default (set to
            `False`), the CAVE API will merge new data with existing
            data.
            * **Note**: The data is merged at the root level. In this
            case, if you update an item in `settings`, the entire
            `settings` object must be present when you return
            `session_data`.
        """
        return {
            "kwargs": kwargs,
            "accepted_values": {},
        }
