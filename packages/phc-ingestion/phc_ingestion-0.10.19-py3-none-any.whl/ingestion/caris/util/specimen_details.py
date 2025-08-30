from logging import Logger
from typing import TypedDict, cast, Optional


class SpecimenDetails(TypedDict, total=False):
    """A partial representation of the specimen details in the Caris JSON file"""

    specimenReceivedDate: str
    specimenCollectionDate: str
    specimenSite: str
    specimenType: str
    specimenID: str | int


class ParsedSpecimenDetails(TypedDict):
    bodySite: str
    receivedDate: str
    collDate: str
    specimenId: Optional[str]
    specimenTypes: Optional[list[str]]


def parse_specimen_details(specimen_details: list[SpecimenDetails]) -> ParsedSpecimenDetails:
    specimen_types: list[str] = []
    for specimen in specimen_details:
        specimen_type = specimen.get("specimenType")
        if specimen_type and specimen_type not in specimen_types:
            specimen_types.append(specimen_type)
    maybe_specimen_id = specimen_details[0].get("specimenID")

    return {
        "bodySite": specimen_details[0].get("specimenSite", ""),
        "receivedDate": specimen_details[0].get("specimenReceivedDate", ""),
        "collDate": specimen_details[0].get("specimenCollectionDate", ""),
        "specimenId": str(maybe_specimen_id) if maybe_specimen_id else None,
        "specimenTypes": specimen_types if specimen_types else None,
    }


def standardize_specimen_details(
    specimen_details: SpecimenDetails | list[SpecimenDetails],
    log: Logger,
) -> list[SpecimenDetails]:
    """
    Specimen details can be a single dictionary or a list of dictionaries
    This function standardizes the input to always be a list of dictionaries

    If it is a list, we expect all the specimens to have the same site and warn otherwise.
    """
    if isinstance(specimen_details, dict):
        return [specimen_details]

    # Sometimes, we have multiple specimen details
    # In this case, we expect them to all be the same and warn otherwise
    sites = {specimen.get("specimenSite") for specimen in specimen_details}

    if len(sites) > 1:
        log.warning("Multiple specimen sites found")

    return specimen_details


def extract_and_parse_specimen_details(data: dict, log: Logger) -> ParsedSpecimenDetails:
    specimen_information = data["specimenInformation"]
    specimen_details: SpecimenDetails | list[SpecimenDetails] | None = None

    # The key for the specimen details varies based on the test type
    potential_keys = [
        # Tissue case
        "tumorSpecimenInformation",
        # Liquid case
        "liquidBiopsySpecimenInformation",
    ]
    for key in potential_keys:
        if key in specimen_information:
            specimen_details = cast(
                SpecimenDetails | list[SpecimenDetails], specimen_information[key]
            )
            break

    if not specimen_details:
        raise ValueError("No specimen details found in data")

    specimen_details = standardize_specimen_details(specimen_details, log)

    return parse_specimen_details(specimen_details)
