import re
from logging import Logger
from typing import Any

import ingestion.nextgen.util.manifest_helpers as manifest_helpers


def transform_date(date: str):
    """mm/dd/yyyy -> yyyy-mm-dd"""
    date_list = date.split("/")
    new_date = f"{date_list[2]}-{date_list[0]}-{date_list[1]}"
    return new_date


def search_and_grab(array: list, search_item: str, grab_index: int):
    """Searches through an array for a string, and returns the item at the specified index after the search item"""
    return array[array.index([i for i in array if re.search(search_item, i)][0]) + grab_index]


def extract_xml_text(xml_in_file: str) -> list[str]:
    with open(xml_in_file, "r") as f:
        xml_lines = f.readlines()

    in_range_trigger = False
    patient_info_lines = []
    for line in xml_lines:
        if "Diagnostic Genomics Laboratory " in line and "bookmark" not in line:
            in_range_trigger = True
        if "PCM Result:" in line:
            in_range_trigger = False
            break
        if in_range_trigger == True:
            patient_info_lines.append(line.strip())

    return patient_info_lines


def extract_interpretation_text(xml_in_file: str) -> list[str]:
    with open(xml_in_file, "r") as f:
        xml_lines = f.readlines()

    in_range_trigger = False
    interpretation_lines = []
    for line in xml_lines:
        if "INTERPRETATION" in line:
            in_range_trigger = True
        if "References" in line:
            in_range_trigger = False
            break
        if in_range_trigger == True:
            interpretation_lines.append(line.strip())

    return interpretation_lines


def get_cell_purity(interpretation_lines: list):
    cell_purity_value = None
    for line in interpretation_lines:
        if "CD138+" in line:
            search_result = re.search(r"\d\d\.\d\d\%", line)
            if search_result:
                cell_purity_value = float(search_result.group(0)[:-2])
                return cell_purity_value
    if not cell_purity_value:
        return float(00.00)


def extract_patient_data(patient_info_lines: list[str]):
    patient_data: dict = {}
    patient_data["patientInfo"] = {}

    for line in patient_info_lines:
        if "patientLastName" not in patient_data and "Patient Name" in line:
            patient_name = manifest_helpers.parse_patient_name(line)
            if "," not in patient_name:
                raise ValueError("Could not parse patient name from line")
            last, first = patient_name.split(",")
            patient_data["patientInfo"]["firstName"] = first.strip()
            patient_data["patientInfo"]["lastName"] = last.strip()
            patient_data["patientLastName"] = last

        if "patientDOB" not in patient_data and "Birthdate" in line:
            dobArray = line.split(" ")
            dob = search_and_grab(dobArray, "Birthdate:", 1)
            patient_data["patientDOB"] = transform_date(dob)
            patient_data["patientInfo"]["dob"] = transform_date(dob)

        if "mrn" not in patient_data and "MRN #" in line:
            mrnArray = line.split(" ")
            mrn = search_and_grab(mrnArray, "MRN", 2)
            patient_data["mrn"] = mrn
            patient_data["patientInfo"]["identifiers"] = [
                {
                    "codingCode": "MR",
                    "codingSystem": "http://hl7.org/fhir/v2/0203",
                    "value": mrn,
                }
            ]

        if "gender" not in patient_data["patientInfo"] and "Gender" in line:
            genderArray = line.split(" ")
            gender = search_and_grab(genderArray, "Gender", 1)
            if gender == "F":
                gender = "female"
            elif gender == "M":
                gender = "male"
            else:
                gender = "other"
            patient_data["patientInfo"]["gender"] = gender

    return patient_data


def extract_test_data(patient_info_lines: list[str], interpretation_lines: list[str], log: Logger):
    # Initialize manifest and hard-code some values
    manifest: dict[str, Any] = {}
    manifest["testType"] = "Plasma Cell Myeloma Panel"
    manifest["name"] = "IU Diagnostic Genomics"
    manifest["reference"] = "GRCh38"

    manifest["ihcTests"] = []
    manifest["tumorTypePredictions"] = []
    manifest["orderingMDNPI"] = ""

    manifest["bodySiteSystem"] = "http://lifeomic.com/fhir/sequence-body-site"
    manifest["indicationSystem"] = "http://lifeomic.com/fhir/sequence-indication"

    manifest["medFacilID"] = ""
    manifest["medFacilName"] = "IU Health"

    report_date = manifest_helpers.parse_report_date(patient_info_lines, log)
    manifest["reportDate"] = transform_date(report_date)
    manifest["indexedDate"] = manifest["reportDate"]

    for line in patient_info_lines:
        if "collDate" not in manifest and "Collected" in line:
            collArray = line.split(" ")
            coll_date = search_and_grab(collArray, "Collected", 1)
            manifest["collDate"] = transform_date(coll_date)

        if "receivedDate" not in manifest and "Received" in line:
            recArray = line.split(" ")
            rec_date = search_and_grab(recArray, "Received", 1)
            manifest["receivedDate"] = transform_date(rec_date)

        if "reportID" not in manifest and "Accession #" in line:
            manifest["reportID"] = manifest_helpers.parse_report_id(line)

        if "sampleNumber" not in manifest and "Specimen #" in line:
            manifest["sampleNumber"] = manifest_helpers.parse_sample_number(line)

        if "orderingMDName" not in manifest and "Physician Name:" in line:
            manifest["orderingMDName"] = manifest_helpers.parse_ordering_md(line)

        if "indication" not in manifest and "Reason for Referral" in line:
            indication = manifest_helpers.parse_indication(line)
            manifest["indication"] = indication
            manifest["indicationDisplay"] = indication

        if "bodySite" not in manifest and "Specimen:" in line:
            body_site = manifest_helpers.parse_body_site(line).strip()
            manifest["bodySite"] = body_site
            manifest["bodySiteDisplay"] = body_site

    cell_purtiy = get_cell_purity(interpretation_lines)
    if cell_purtiy != 00.00:
        manifest["cellPurity"] = cell_purtiy

    return manifest


def process_manifest(
    xml_in_file: str,
    source_file_id: str,
    case_id: str,
    include_copy_number: bool,
    include_structural: bool,
    somatic_translocations: list[str],
    hyperdiploidy_chromosomes: list[str] | None,
    log: Logger,
):
    test_text = extract_xml_text(xml_in_file)
    interpretation_text = extract_interpretation_text(xml_in_file)
    manifest = extract_test_data(test_text, interpretation_text, log)
    manifest.update(extract_patient_data(test_text))

    file_prefix = f".lifeomic/nextgen/{case_id}/{case_id}"

    if hyperdiploidy_chromosomes:
        manifest["hyperdiploidyTrisomies"] = hyperdiploidy_chromosomes
    if somatic_translocations:
        manifest["somaticTranslocations"] = somatic_translocations

    manifest["reportFile"] = f"{file_prefix}.pdf"
    manifest["sourceFileId"] = source_file_id
    manifest["resources"] = []

    manifest["files"] = [
        {
            "fileName": f"{file_prefix}.modified.somatic.nrm.filtered.vcf.gz",
            "sequenceType": "somatic",
            "type": "shortVariant",
        },
        {
            "fileName": f"{file_prefix}.modified.germline.nrm.filtered.vcf.gz",
            "sequenceType": "germline",
            "type": "shortVariant",
        },
        {
            "fileName": f"{file_prefix}.somatic.updated.bam",
            "sequenceType": "somatic",
            "type": "read",
        },
        {
            "fileName": f"{file_prefix}.germline.updated.bam",
            "sequenceType": "germline",
            "type": "read",
        },
    ]
    if include_structural:
        manifest["files"].append(
            {
                "fileName": f"{file_prefix}.structural.csv",
                "sequenceType": "somatic",
                "type": "structuralVariant",
            },
        )
    if include_copy_number:
        manifest["files"].append(
            {
                "fileName": f"{file_prefix}.copynumber.csv",
                "sequenceType": "somatic",
                "type": "copyNumberVariant",
            }
        )

    return manifest
