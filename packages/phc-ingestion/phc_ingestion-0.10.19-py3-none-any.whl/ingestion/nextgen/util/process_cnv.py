import pandas as pd
from logging import Logger

from ingestion.nextgen.util.alteration_table import AlterationTableRow, CopyNumberVariantGene
from ingestion.nextgen.util.interpretation import map_interpretation


def process_cnv(
    cnv_in_file: str,
    copy_number_variant_table_rows: list[AlterationTableRow[CopyNumberVariantGene]],
    output_dir: str,
    case_id: str,
    log: Logger,
) -> str | None:
    copy_number_path_name = f"{output_dir}/{case_id}.copynumber.csv"
    sample_id = case_id

    copy_number_variant_rows: list[str] = []

    with open(cnv_in_file, "r") as f:
        cnv_rows = f.readlines()

    for row in cnv_rows[1:]:
        working = row.strip().split("\t")

        chromosome = "chr" + working[0]
        start_position = working[1]
        end_position = working[2]
        gene = working[3]
        gene_id_only = gene.split("_")[0]
        if gene_id_only.endswith("CN"):
            gene_id_only = gene_id_only[:-2]

        copy_number = working[4]
        try:
            float(copy_number)
        except ValueError:
            log.warn("Copy number value is not a number. Omitting row.")
            continue

        status = working[5]
        if status == "normal":
            status = "neutral"

        # Hard-code
        attributes = {}

        # Scrape interpretation
        interpretation = "unknown"
        for row in copy_number_variant_table_rows:
            if (
                row["gene"]["gene"] == gene_id_only
                and row["gene"]["chr"] == chromosome
                and row["gene"]["start"] <= int(start_position)
                and row["gene"]["end"] >= int(end_position)
            ):
                interpretation = map_interpretation(row["info"], log)

        copy_number_variant_rows.append(
            f"{sample_id},{gene_id_only},{copy_number},{status},{attributes},{chromosome},{start_position},{end_position},{interpretation}\n"
        )

    if not copy_number_variant_rows:
        log.info(f"Ignoring empty copy number file {cnv_in_file}")
        return None

    log.info(f"Saving file to {copy_number_path_name}")
    with open(copy_number_path_name, "w") as f:
        f.write(
            "sample_id,gene,copy_number,status,attributes,chromosome,start_position,end_position,interpretation\n"
        )
        for cnv_text_row in copy_number_variant_rows:
            f.write(cnv_text_row)

    return copy_number_path_name
