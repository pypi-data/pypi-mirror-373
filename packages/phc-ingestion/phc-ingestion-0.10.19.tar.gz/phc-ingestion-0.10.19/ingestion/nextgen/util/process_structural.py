from logging import Logger
import re
from typing import TypedDict

from ingestion.shared_util.coords_to_genes import coords_to_genes
from ingestion.nextgen.util.alteration_table import AlterationTableRow, StructuralVariantGene
from ingestion.nextgen.util.interpretation import map_interpretation
from ingestion.nextgen.util.nextgen_specific_genes import maybe_get_nextgen_specific_gene
from ingestion.shared_util.open_maybe_gzipped import open_maybe_gzipped


class StructuralVariant(TypedDict):
    sample_id: str
    gene1: str
    gene2: str
    effect: str
    position1: tuple[str, str, str]
    position2: tuple[str, str, str]
    interpretation: str
    sequence_type: str
    in_frame: str
    attributes: dict


def structural_variant_to_csv_row(structural_variant: StructuralVariant) -> str:
    csv_row = ""
    for value in structural_variant.values():
        if isinstance(value, tuple):
            csv_row += ",".join(value)
        else:
            csv_row += f"{value}"
        csv_row += ","
    return f"{csv_row[:-1]}\n"


def are_variants_duplicates(sv1: StructuralVariant, sv2: StructuralVariant) -> bool:
    return (sv1["position1"] == sv2["position1"] and sv1["position2"] == sv2["position2"]) or (
        sv1["position1"] == sv2["position2"] and sv1["position2"] == sv2["position1"]
    )


def is_del_dup_or_ins(variant: list[str]) -> bool:
    return any([x in variant[2] for x in ["MantaDEL", "MantaDUP", "MantaINS"]])


def get_center_position(start_position: str, end_position: str) -> int:
    """
    Calculate the center position of a variant based on its start and end positions, useful for finding genes.
    """
    return int((int(start_position) + int(end_position)) / 2)


def process_structural(
    structural_variant_in_file: str,
    structural_variant_table_rows: list[AlterationTableRow[StructuralVariantGene]],
    output_dir: str,
    case_id: str,
    log: Logger,
) -> tuple[str | None, list[str]]:
    structural_variant_path_name = f"{output_dir}/{case_id}.structural.csv"
    sample_id = case_id

    with open_maybe_gzipped(structural_variant_in_file, "rt") as f:
        variants = [line for line in f.readlines() if not line.startswith("#")]

    structural_variants: list[StructuralVariant] = []
    formatted_translocations: set[str] = set()

    for variant in variants:
        gene1: str | None = None
        gene2: str | None = None

        working_variant = variant.strip().split("\t")

        chromosome1 = f"chr{working_variant[0]}"
        start_position1 = working_variant[1]

        if is_del_dup_or_ins(working_variant):
            end_position1 = working_variant[7].split(";")[0].split("=")[1]
            chromosome2 = chromosome1
            start_position2 = start_position1
            end_position2 = end_position1
            effect = "duplication"
            if "MantaDEL" in working_variant[2]:
                effect = "deletion"
            elif "MantaINS" in working_variant[2]:
                effect = "insertion"

            # Get genes from coordinates using center point of start and end positions
            gene1 = None
            gene2 = "N/A"

        else:
            alt = working_variant[4].strip("][TCGA").split(":")

            end_position1 = start_position1
            chromosome2 = f"chr{alt[0]}"
            start_position2 = alt[1]
            end_position2 = alt[1]
            effect = "translocation"

            gene1 = maybe_get_nextgen_specific_gene(
                chromosome1, get_center_position(start_position1, end_position1)
            )
            gene2 = maybe_get_nextgen_specific_gene(
                chromosome2, get_center_position(start_position2, end_position2)
            )

            # Maybe add this variant to the formatted translocations list
            if (gene1 == "MYC" or gene2 == "MYC") and gene1 != gene2:
                formatted_translocations.add("t(MYC)")
            elif gene1 and gene2:
                # Remove the "chr" prefix and convert to int
                chr1, chr2 = int(chromosome1[3:]), int(chromosome2[3:])
                # Don't add translocations between the same chromosome
                if chr1 == chr2:
                    continue
                # Ensure chromosomes are in ascending order
                if chr1 > chr2:
                    chr1, chr2 = chr2, chr1
                formatted_translocations.add(f"t({chr1};{chr2})")

        # Scrape interpretation
        interpretation = "unknown"
        for row in structural_variant_table_rows:
            is_match = (
                row["gene"]["chr1"] == chromosome1
                and row["gene"]["chr2"] == chromosome2
                and row["gene"]["pos1"] == int(start_position1)
                and row["gene"]["pos2"] == int(start_position2)
            )
            if not is_match:
                continue

            interpretation = map_interpretation(row["info"], log)
            # Use the gene names from the alteration table but only if they are not already set
            gene1 = gene1 if gene1 else row["gene"]["gene1"]
            gene2 = gene2 if gene2 else row["gene"]["gene2"]

        # Hard-code
        sequence_type = "Somatic"
        in_frame = "Unknown"
        attributes: dict = {}

        # If genes have not been populated from the nextgen specific genes or alteration
        # table fall back to using the default gene finding method
        if not gene1:
            gene1 = coords_to_genes(
                "GRCh38", chromosome1, get_center_position(start_position1, end_position1), log
            )
        if not gene2:
            gene2 = coords_to_genes(
                "GRCh38", chromosome2, get_center_position(start_position2, end_position2), log
            )

        structural_variants.append(
            {
                "sample_id": sample_id,
                "gene1": gene1,
                "gene2": gene2,
                "effect": effect,
                "position1": (chromosome1, start_position1, end_position1),
                "position2": (chromosome2, start_position2, end_position2),
                "interpretation": interpretation,
                "sequence_type": sequence_type,
                "in_frame": in_frame,
                "attributes": attributes,
            }
        )

    # Dedupe structural variants based on chromosome and positions
    deduped_structural_variants: list[StructuralVariant] = []
    for sv in structural_variants:
        maybe_matching_variant = next(
            (
                variant
                for variant in deduped_structural_variants
                if are_variants_duplicates(sv, variant)
            ),
            None,
        )
        if not maybe_matching_variant:
            deduped_structural_variants.append(sv)

    if not deduped_structural_variants:
        log.info(f"Ignoring empty structural variant file {structural_variant_in_file}")
        return (None, [])

    log.info(f"Saving file to {structural_variant_path_name}")
    with open(structural_variant_path_name, "w+") as f:
        f.write(
            "sample_id,gene1,gene2,effect,chromosome1,start_position1,end_position1,chromosome2,start_position2,end_position2,interpretation,sequence_type,in-frame,attributes\n"
        )
        for sv in deduped_structural_variants:
            f.write(structural_variant_to_csv_row(sv))

    log.info(f"Found {len(formatted_translocations)} translocations for genes of interest")

    return structural_variant_path_name, list(formatted_translocations)
