from __future__ import annotations

import dataclasses
import pprint
import typing

import pydantic
import pydicom
from deid.config import DeidRecipe
from deid.dicom.filter import apply_filter
from deid.dicom.pixels.detect import evaluate_group, extract_coordinates
from loguru import logger
from pydantic import Field

if typing.TYPE_CHECKING:
    from collections import OrderedDict
    import pydicom.valuerep
    from dicom_qr.deid_anonymizer import Options


# https://dicom.nema.org/medical/dicom/current/output/chtml/part05/sect_6.2.html
# https://dicom.nema.org/medical/dicom/current/output/chtml/part15/sect_E.2.html
# https://www.hl7.org/implement/standards/fhir/2013Sep/valueset-dicom-dcim.htm


@pydantic.dataclasses.dataclass
class Filter:
    """ Filter """
    action: list[str] = Field(default_factory=list)
    dcm_tag: list[str] = Field(default_factory=list, alias='field')
    inner_operators: list[str] = Field(default_factory=list, alias='InnerOperators')
    operator: str | None = None
    value: list[str] = Field(default_factory=list)


@dataclasses.dataclass
class FilterResults:
    """ FilterResults """
    reason: str
    group: str
    coordinates: list[str]


# Copied from deid\dicom\pixels\detect.py
def _apply_filters(dicom: pydicom.Dataset, deid: DeidRecipe) -> tuple[bool, list[FilterResults]]:
    # Load criteria (actions) for flagging
    filters: OrderedDict | None = deid.get_filters()
    if not filters:
        logger.warning("Deid provided does not have %filter.")
        return False, []

    global_flagged = False
    results = []
    for name, items in filters.items():
        for item in items:
            flags = []

            descriptions = []  # description for each group across items

            # If there aren't any filters, but we have coordinates, assume True
            if not item.get("filters") and item.get("coordinates"):
                group_flags = ['True']
                group_descriptions = [item.get("name", "")]
                group = Filter()
            else:
                group, group_descriptions, group_flags = _process_group(dicom, item)

            # At the end of a group, evaluate the inner group
            flag: str = evaluate_group(group_flags)

            # "Operator" is relevant for the outcome of the list of actions
            operator = ""
            if group.operator is not None:
                operator = group.operator
                flags.append(operator)

            flags.append(flag)
            reason = f" {operator} ".join(group_descriptions).replace('\n', ' ')
            descriptions.append(reason)

            # When we parse through a group, we evaluate based on all flags
            flagged = evaluate_group(flags=flags)

            if flagged is True:
                global_flagged = True
                reason = " ".join(descriptions)

                # Each coordinate is a list with [value, [coordinate]]
                # and if from: in the coordinate value, it indicates we get
                # the coordinate from some field (done here)
                for coordset in item["coordinates"]:
                    if "from:" in coordset[1]:
                        coordset[1] = extract_coordinates(dicom, coordset[1])

                results.append(FilterResults(reason=reason, group=name, coordinates=item["coordinates"]))

    return global_flagged, results


def _process_group(dicom: pydicom.Dataset, item: dict) -> tuple[Filter, list[str], list[str]]:
    filters = [Filter(**x) for x in item["filters"]]

    if len(filters) == 0:
        return Filter(), [], []

    group_flags: list[str] = []  # evaluation for a single line
    group_descriptions: list[str] = []
    group = Filter()
    for group in filters:
        # You cannot pop from the list
        for action_id, _ in enumerate(group.action):
            action = group.action[action_id]
            field = group.dcm_tag[action_id]
            value = ""

            if len(group.value) > action_id:
                value = group.value[action_id]

            flag = apply_filter(
                dicom=dicom,
                field=field,
                filter_name=action,
                value=value or None,
            )
            group_flags.append(flag)
            description = f'{field} {action} {value}'

            if len(group.inner_operators) > action_id:
                inner_operator = group.inner_operators[action_id]
                group_flags.append(inner_operator)
                description = f"{description} {inner_operator}"

            group_descriptions.append(description)
    return group, group_descriptions, group_flags


# pylint: disable=too-few-public-methods
class DeidFilter:
    """This class checks a dataset against a recipe to split into white/gray/blacklist. """

    def __init__(self, options: Options) -> None:
        self.options = options
        self.recipe = DeidRecipe(self.options.recipe_path)

        if self.options.very_verbose:
            logger.debug(pprint.pformat(self.recipe.deid))

    def check_dataset(self, dataset: pydicom.Dataset) -> tuple[bool, list]:
        """
        Check the dataset
        :param dataset: dataset to check
        :return: filter result
        """
        return _apply_filters(dataset, self.recipe)
