import pandas as pd

from logging import Logger
from ingestion.caris.util.detect_genome_ref import detect_caris_gr


# Take the caris RNA information from the provided tsv for ingestion and input to TSO/pcann
# We are not guaranteed rnaseq results FYI
def convert_tsv_to_rgel(prefix, files, log: Logger):
    if not "tsv" in files:
        return None
    tsv_file = files["tsv"]
    log.info(f"RNA TPM file found. Converting to RGEL: {tsv_file}")

    df = pd.read_table(tsv_file, comment="#", header=None)
    df.rename(columns={0: "gene_id", 1: "expression"}, inplace=True)

    df["sample_id"] = prefix
    df["gene_name"] = df["gene_id"]
    df["raw_count"] = ""
    df["attributes"] = "{}"
    df["is_normalized"] = "True"
    df["expression_unit"] = "tpm"

    df.drop_duplicates(inplace=True)
    # Select columns for output
    df_out = df[
        [
            "sample_id",
            "gene_id",
            "gene_name",
            "expression",
            "raw_count",
            "attributes",
            "is_normalized",
            "expression_unit",
        ]
    ]

    df_out.to_csv(f"{prefix}.expression.rgel.gz", compression="gzip", na_rep="", index=False)

    headers = []
    with open(tsv_file) as f:
        for line in f.readlines()[:10]:
            headers.append(line.strip())
    genome_reference = detect_caris_gr(headers, "expression", log)

    return {
        "fileName": f".lifeomic/caris/{prefix}/{prefix}.expression.rgel.gz",
        "sequenceType": "somatic",
        "type": "expression",
        "reference": genome_reference,
    }

    return None
