import ast
import csv
import json
from logging import Logger
from typing import Optional

from ingestion.foundation.util.interpretation import calculate_interpretation


def gather_attributes(fusion: dict) -> dict:
    attributes = {}
    if "@equivocal" in fusion.keys():
        attributes["equivocal"] = fusion["@equivocal"]
    if "@supporting-read-pairs" in fusion.keys():
        attributes["supporting-read-pairs"] = fusion["@supporting-read-pairs"]

    return attributes


def calculate_other_gene(other_gene: str) -> str:
    if other_gene == "N/A":
        return ""
    return other_gene


def cleanup_chromosome(chromosome: str) -> str:
    if "chr" in chromosome:
        return chromosome
    return chromosome.replace("ch", "chr")


def get_value_or_default(value: Optional[str], default: str = "N/A") -> str:
    if value:
        return value
    return default


def extract_start_and_end_positions(
    fusion_variant: dict, position1: str, position2: str
) -> tuple[list[int], list[int]]:
    # First check if positions are ranges, or individual loci
    # Assume that if pos1 is a range, pos2 is as well
    pos_one_list = []
    pos_two_list = []
    if len(fusion_variant[position1].split(":")[1].split("-")) > 1:
        pos_one_list.append(int(fusion_variant[position1].split(":")[1].split("-")[0]))
        pos_one_list.append((fusion_variant[position1].split(":")[1].split("-")[1]))
        pos_two_list.append(int(fusion_variant[position2].split(":")[1].split("-")[0]))
        pos_two_list.append((fusion_variant[position2].split(":")[1].split("-")[1]))
        return pos_one_list, pos_two_list

    # If ranges aren't provided, we need two different entries, with ranges of identical start and end ponts
    else:
        pos_one_list.append(int(fusion_variant[position1].split(":")[1]))
        pos_one_list.append(int(fusion_variant[position1].split(":")[1]))
        pos_two_list.append(int(fusion_variant[position2].split(":")[1]))
        pos_two_list.append(int(fusion_variant[position2].split(":")[1]))
        return pos_one_list, pos_two_list


def extract_fusion_variant(
    results_payload_dict: dict,
    base_xml_name: str,
    output_dir: str,
    log: Logger,
) -> bool:
    log.info("Extracting fusion variants from xml")
    fusion_variant_list: dict = {"FusionVariants": []}

    if (
        "variant-report" in results_payload_dict
        and "rearrangements" in results_payload_dict["variant-report"].keys()
    ):
        if (
            results_payload_dict["variant-report"]["rearrangements"] is not None
            and "rearrangement" in results_payload_dict["variant-report"]["rearrangements"].keys()
        ):
            variants_dict = results_payload_dict["variant-report"]["rearrangements"][
                "rearrangement"
            ]
            fusion_variants = variants_dict if isinstance(variants_dict, list) else [variants_dict]

            for fusion_variant in fusion_variants:
                pos_one_list, pos_two_list = extract_start_and_end_positions(
                    fusion_variant, "@pos1", "@pos2"
                )
                fusion_variant_value = {
                    "sample_id": base_xml_name,
                    "gene1": get_value_or_default(fusion_variant["@targeted-gene"]),
                    "gene2": get_value_or_default(fusion_variant["@other-gene"]),
                    "effect": get_value_or_default(fusion_variant["@type"].lower()),
                    "chromosome1": cleanup_chromosome(fusion_variant["@pos1"].split(":")[0]),
                    "start_position1": pos_one_list[0],
                    "end_position1": pos_one_list[1],
                    "chromosome2": cleanup_chromosome(fusion_variant["@pos2"].split(":")[0]),
                    "start_position2": pos_two_list[0],
                    "end_position2": pos_two_list[1],
                    "in-frame": get_value_or_default(fusion_variant["@in-frame"].lower()),
                    "interpretation": calculate_interpretation(fusion_variant["@status"], log),
                    "sequence_type": "somatic",
                    "attributes": gather_attributes(fusion_variant),
                }
                fusion_variant_list["FusionVariants"].append(
                    ast.literal_eval(json.dumps(fusion_variant_value))
                )

    return write_fusions_to_fnv(fusion_variant_list, base_xml_name, output_dir, log)


def write_fusions_to_fnv(fnv_dict: dict, base_xml_name: str, output_dir: str, log: Logger) -> bool:
    log.info("Saving fusion variants to fnv file")

    if len(fnv_dict["FusionVariants"]) == 0:
        return False

    with open(
        f"{output_dir}/{base_xml_name}/{base_xml_name}.structural.csv",
        "w",
    ) as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=",")
        csv_writer.writerow(
            [
                "sample_id",
                "gene1",
                "gene2",
                "effect",
                "chromosome1",
                "start_position1",
                "end_position1",
                "chromosome2",
                "start_position2",
                "end_position2",
                "interpretation",
                "sequence_type",
                "in-frame",
                "attributes",
            ]
        )
        for fnv in fnv_dict["FusionVariants"]:
            csv_writer.writerow(
                [
                    fnv["sample_id"],
                    fnv["gene1"],
                    fnv["gene2"],
                    fnv["effect"],
                    fnv["chromosome1"],
                    fnv["start_position1"],
                    fnv["end_position1"],
                    fnv["chromosome2"],
                    fnv["start_position2"],
                    fnv["end_position2"],
                    fnv["interpretation"],
                    fnv["sequence_type"],
                    fnv["in-frame"],
                    fnv["attributes"],
                ]
            )

    return True
