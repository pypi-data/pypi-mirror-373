import ast
import csv
import json
from logging import Logger

from ingestion.foundation.util.interpretation import calculate_interpretation


def calculate_status(equivocal: str, copy_type: str, log: Logger) -> str:
    if copy_type == "amplification":
        if equivocal == "true":
            return "gain"
        return "amplification"
    if copy_type == "loss":
        if equivocal == "true":
            return "partial_loss"
        return "loss"
    if copy_type == "partial amplification":
        return "gain"

    log.error(f"Failed to resolve copy type: {copy_type}, equivocal: {equivocal}")
    return ""


def gather_attributes(copy_number: dict) -> dict:
    attributes = {}
    if "@number-of-exons" in copy_number.keys():
        attributes["number-of-exons"] = copy_number["@number-of-exons"]
    if "@type" in copy_number.keys():
        attributes["status"] = copy_number["@type"]
    if "@ratio" in copy_number.keys():
        attributes["ratio"] = copy_number["@ratio"]
    if "@status" in copy_number.keys():
        attributes["interpretation"] = copy_number["@status"]

    return attributes


def extract_copy_numbers(
    results_payload_dict: dict, base_xml_name, output_dir: str, log: Logger
) -> bool:
    log.info("Extracting copy numbers from xml")
    copy_number_list: dict = {"CopyNumbers": []}

    if (
        "variant-report" in results_payload_dict
        and "copy-number-alterations" in results_payload_dict["variant-report"].keys()
    ):
        if (
            results_payload_dict["variant-report"]["copy-number-alterations"] is not None
            and "copy-number-alteration"
            in results_payload_dict["variant-report"]["copy-number-alterations"].keys()
        ):
            variants_dict = results_payload_dict["variant-report"]["copy-number-alterations"][
                "copy-number-alteration"
            ]
            copy_numbers = variants_dict if isinstance(variants_dict, list) else [variants_dict]

            for copy_number in copy_numbers:
                copy_number_value = {
                    "sample_id": base_xml_name,
                    "gene": copy_number["@gene"],
                    "copy_number": float(format(copy_number["@copy-number"])),
                    "status": calculate_status(
                        copy_number["@equivocal"], copy_number["@type"], log
                    ),
                    "chromosome": copy_number["@position"].split(":")[0],
                    "start_position": copy_number["@position"].split(":")[1].split("-")[0],
                    "end_position": copy_number["@position"].split(":")[1].split("-")[1],
                    "attributes": gather_attributes(copy_number),
                    "interpretation": calculate_interpretation(copy_number["@status"], log),
                }

                copy_number_list["CopyNumbers"].append(
                    ast.literal_eval(json.dumps(copy_number_value))
                )

    return write_copy_numbers_to_cnv(copy_number_list, base_xml_name, output_dir, log)


def write_copy_numbers_to_cnv(
    cnv_dict: dict, base_xml_name: str, output_dir: str, log: Logger
) -> bool:
    log.info("Saving copy numbers to cnv file")

    if len(cnv_dict["CopyNumbers"]) == 0:
        return False

    with open(
        f"{output_dir}/{base_xml_name}/{base_xml_name}.copynumber.csv",
        "w",
    ) as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=",")
        csv_writer.writerow(
            [
                "sample_id",
                "gene",
                "copy_number",
                "status",
                "attributes",
                "chromosome",
                "start_position",
                "end_position",
                "interpretation",
            ]
        )
        for cnv in cnv_dict["CopyNumbers"]:
            csv_writer.writerow(
                [
                    cnv["sample_id"],
                    cnv["gene"],
                    cnv["copy_number"],
                    cnv["status"],
                    cnv["attributes"],
                    cnv["chromosome"],
                    cnv["start_position"],
                    cnv["end_position"],
                    cnv["interpretation"],
                ]
            )

    return True
