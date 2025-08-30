import os
from logging import Logger
from schema import Schema, SchemaError, Optional
from ruamel.yaml import YAML


def check_manifest(manifest_file_path: str, case_id, log: Logger):
    manifest_schema = Schema(
        {
            # Required fields
            "name": str,  # Vendor name
            "testType": str,  # Vendor test name
            "indexedDate": str,  # Date of ingestion YYYY-MM-DD
            "reference": str,  # Reference genome
            "mrn": str,  # Patient MRN
            "patientInfo": {
                "lastName": str,
                "dob": str,  # YYYY-MM-DD
                "firstName": str,
                "gender": str,
            },
            # Optional fields
            Optional("receivedDate"): str,
            Optional("collDate"): str,
            Optional("reportDate"): str,
            Optional("reportFile"): str,
            Optional("medFacilName"): str,
            Optional("medFacilID"): str,
            Optional("orderingMDName"): str,
            Optional("orderingMDNPI"): str,
            Optional("indicationSystem"): "http://lifeomic.com/fhir/sequence-indication",
            Optional("indication"): str,
            Optional("indicationDisplay"): str,
            Optional("bodySite"): str,
            Optional("bodySiteDisplay"): str,
            Optional("bodySiteSystem"): "http://lifeomic.com/fhir/sequence-body-site",
            Optional("tmb"): str,
            Optional("tmbScore"): float,
            Optional("msi"): str,
            Optional("lossOfHeterozygosityScore"): int,
            Optional("lossOfHeterozygosityStatus"): str,
            Optional("ihcTests"): any,
            Optional("nonHumanContent"): any,
            Optional("plasmaTumorFraction"): str,
            Optional("cellPurity"): float,
            Optional("hrdStatus"): str,
        }
    )

    # Read in manifest yaml
    if os.path.exists(manifest_file_path):
        with open(manifest_file_path, "r") as file:
            manifest = YAML(typ="safe")
            manifest = manifest.load(file)
    else:
        raise FileNotFoundError(f"Manifest file not found: {manifest_file_path}")

    # Validate
    try:
        manifest_schema.validate(manifest)
    except SchemaError as e:
        log.error(e)
        raise e

    # Add duplicate fields from supplied ones to fit formatting
    manifest["patientInfo"]["identifiers"] = [
        {
            "codingCode": "MR",
            "codingSystem": "http://hl7.org/fhir/v2/0203",
            "value": manifest["mrn"],
        }
    ]

    manifest["patientLastName"] = manifest["patientInfo"]["lastName"]

    manifest["patientDOB"] = manifest["patientInfo"]["dob"]

    manifest["reportID"] = case_id  # Vendor report ID / Case ID

    log.info(f"Manifest file validated")
    return manifest
