"""
# API

This module serves to document the `cave_app` API data structures.

## API Reference

Classes represent the actual API items and should have relevant API documentation for each item at the class level. In this current module, the `root` class represents the root of the API. The method `spec` details exactly what must be passed to root as well as other relevant documentation.

Submodules (and their classes) are used to define the api at each level. You can use the links on the left to navigate into the API and get detailed documentation for each API item at each level.

See the left hand side for all available submodules.
"""

from cave_utils.api_utils.validator_utils import *
from cave_utils.api.extraKwargs import extraKwargs
from cave_utils.api.settings import settings
from cave_utils.api.appBar import appBar
from cave_utils.api.panes import panes
from cave_utils.api.pages import pages
from cave_utils.api.maps import maps
from cave_utils.api.globalOutputs import globalOutputs
from cave_utils.api.mapFeatures import mapFeatures
from cave_utils.api.groupedOutputs import groupedOutputs
import type_enforced


@type_enforced.Enforcer
class Root(ApiValidator):
    """
    The root of the CAVE API data structure.

    This should include all of the data needed to build out your application.
    """

    @staticmethod
    def spec(
        settings: dict,
        appBar: dict = dict(),
        panes: dict = dict(),
        pages: dict = dict(),
        maps: dict = dict(),
        mapFeatures: dict = dict(),
        groupedOutputs: dict = dict(),
        globalOutputs: dict = dict(),
        extraKwargs: dict = dict(),
        **kwargs,
    ):
        """
        Arguments:

        * **`settings`**: `[dict]` &rarr; General settings for your application.
            * **Note**: `settings.iconUrl` is the only required field in `settings`
            * **See**: `cave_utils.api.settings`
        * **`appBar`**: `[dict]` = `None` &rarr; Configure actions for your app bar(s).
            * **Notes**:
                * If left unspecified (i.e., `None`), there will be no action elements on the app bar.
                * Otherwise, `appBar.data` is required and should have at least one item in it.
            * **See**: `cave_utils.api.appBar`
        * **`panes`**: `[dict]` = `{}` &rarr; Configure panes for your application.
            * **See**: `cave_utils.api.panes`
        * **`pages`**: `[dict]` = `{}` &rarr; Configure pages for your application.
            * **See**: `cave_utils.api.pages`
        * **`maps`**: `[dict]` = `{}` &rarr; Configure map views and settings for your application.
            * **See**: `cave_utils.api.maps`
        * **`mapFeatures`**: `[dict]` = `{}` &rarr;
            * Configure map features (interactive items on the map) for your application.
            * **See**: `cave_utils.api.mapFeatures`
        * **`groupedOutputs`**: `[dict]` = `{}` &rarr;
            * Configure data that can be sliced and diced for charts and tables based on arbitrary groups.
            * **See**: `cave_utils.api.groupedOutputs`
        * **`globalOutputs`**: `[dict]` = `{}` &rarr;
            * Configure data that is general to the entire application and can be compared across sessions.
            * **See**: `cave_utils.api.globalOutputs`
        * **`extraKwargs`**: `[dict]` = `{}` &rarr; Special arguments to be passed to the server.
            * **See**: `cave_utils.api.extraKwargs`
        """
        kwargs = {k: v for k, v in kwargs.items() if k != "associated"}
        return {
            "kwargs": kwargs,
            "accepted_values": {},
        }

    def __extend_spec__(self, **kwargs):
        # Validate Kwargs
        if "extraKwargs" in self.data:
            extraKwargs(
                data=self.data.get("extraKwargs", {}),
                log=self.log,
                prepend_path=["kwargs"],
                **kwargs,
            )
        # Validate Settings
        settings(
            data=self.data.get("settings", {}),
            log=self.log,
            prepend_path=["settings"],
            root_data=self.data,
            **kwargs,
        )
        # Special logic to add timeLength to kwargs
        # This is used to validate timeValues across the app
        kwargs["timeLength"] = pamda.path(["settings", "time", "timeLength"], self.data)
        # Validate panes
        panes_data = self.data.get("panes")
        pane_validPaneIds = []
        if panes_data is not None:
            panes(data=panes_data, log=self.log, prepend_path=["panes"], **kwargs)
            pane_validPaneIds = list(panes_data.get("data", {}).keys())
        # Validate mapFeatures
        mapFeatures_data = self.data.get("mapFeatures", dict())
        mapFeatures_feature_props = {}
        if mapFeatures_data != {}:
            mapFeatures(
                data=mapFeatures_data,
                log=self.log,
                prepend_path=["mapFeatures"],
                **kwargs,
            )
            for key, value in mapFeatures_data.get("data", {}).items():
                mapFeatures_feature_props[key] = value.get("props", {})
        # Validate maps
        maps_data = self.data.get("maps", dict())
        maps_validMapIds = []
        if maps_data != {}:
            maps(
                data=maps_data,
                log=self.log,
                prepend_path=["maps"],
                mapFeatures_feature_props=mapFeatures_feature_props,
                **kwargs,
            )
            maps_validMapIds = list(maps_data.get("data", {}).keys())
        # Validate globalOutputs
        globalOutputs_data = self.data.get("globalOutputs", dict())
        globalOuputs_validPropIds = []
        if globalOutputs_data != {}:
            globalOutputs(
                data=globalOutputs_data,
                log=self.log,
                prepend_path=["globalOutputs"],
                **kwargs,
            )
            globalOuputs_validPropIds = list(globalOutputs_data.get("values", {}).keys())
        # Validate groupedOutputs
        groupedOutputs_data = self.data.get("groupedOutputs", dict())
        groupedOutputs_validLevelIds = {}
        groupedOutputs_validStatIds = {}
        groupedOutputs_validDatasetIds = {}
        if groupedOutputs_data != {}:
            groupedOutputs(
                data=groupedOutputs_data,
                log=self.log,
                prepend_path=["groupedOutputs"],
                **kwargs,
            )
            # Populate valid ids for each relevant groupedOutput to be used in pages.
            try:
                groupedOutputs_validLevelIds = {
                    k: list(v.get("levels").keys())
                    for k, v in groupedOutputs_data.get("groupings", {}).items()
                }
            except:
                pass
            try:
                groupedOutputs_validStatIds = {
                    k: list(v.get("stats", []))
                    for k, v in groupedOutputs_data.get("data", {}).items()
                }
            except:
                pass
            try:
                groupedOutputs_validDatasetIds = {
                    k: list(v.get("groupLists").keys())
                    for k, v in groupedOutputs_data.get("data", {}).items()
                }
            except:
                pass
        # Validate pages
        pages_data = self.data.get("pages", dict())
        page_validPageIds = []
        if pages_data != {}:
            pages(
                data=pages_data,
                log=self.log,
                prepend_path=["pages"],
                # Special Kwargs to validate globalOutputs, groupedOutputs and maps are valid:
                globalOuputs_validPropIds=globalOuputs_validPropIds,
                maps_validMapIds=maps_validMapIds,
                groupedOutputs_validLevelIds=groupedOutputs_validLevelIds,
                groupedOutputs_validStatIds=groupedOutputs_validStatIds,
                groupedOutputs_validDatasetIds=groupedOutputs_validDatasetIds,
                **kwargs,
            )
            page_validPageIds = list(pages_data.get("data", {}).keys())
        # Validate appBar
        appBar_data = self.data.get("appBar", dict())
        if appBar_data != {}:
            appBar(
                data=appBar_data,
                log=self.log,
                prepend_path=["appBar"],
                # Special kwargs to validate panes and pages are valid:
                page_validPageIds=page_validPageIds,
                pane_validPaneIds=pane_validPaneIds,
                **kwargs,
            )
