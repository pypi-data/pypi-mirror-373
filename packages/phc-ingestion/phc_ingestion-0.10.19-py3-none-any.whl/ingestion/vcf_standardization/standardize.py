import gzip
from logging import Logger
from typing import Iterator, Optional

from ingestion.vcf_standardization.util.read_write import (
    add_to_headers,
    write_vcf,
    check_vcf,
    read_headers,
    read_variants,
)
from ingestion.vcf_standardization.Variant import Variant


def format_variant(variant: str, log: Logger, vendsig_dict: dict | None = None) -> Optional[str]:
    # Ignore structural variants
    if "SVTYPE" in variant:
        return None
    # Working variant
    wv = Variant.check_formatting(variant)

    # Only process variants that aren't multiallelic
    if len(wv.alt.split(",")) == 1:
        if "AD" in wv.frmt:
            wv.ad_af_dp.update({"AD": wv.smpl[wv.frmt.index("AD")]})

        wv.standardize_allele_frequency(log)

        wv.standardize_genotype(log)

        wv.standardize_depth(log)

        wv.standardize_allelic_depth(log)

    if vendsig_dict:
        wv.add_vendsig(vendsig_dict, log)

    wv.prune_var(log)

    updated_variant = wv.reassemble_variant()

    return updated_variant


def standardize_vcf(
    infile: str,
    outfile: str,
    out_path: str,
    case_id: str,
    log: Logger,
    vendsig_dict: dict | None = None,
    compression: bool = False,
) -> Optional[int]:
    check_vcf(infile, log)

    if compression and not outfile.endswith(".gz"):
        outfile = outfile + ".gz"

    headers = []
    with gzip.open(infile, "rt") if infile.endswith(".gz") else open(infile, "r") as f:
        headers = read_headers(f)

    line_count = len(headers)

    with gzip.open(infile, "rt") if infile.endswith(".gz") else open(infile, "r") as f:
        input_variants = read_variants(f)

        def output_variants_gen() -> Iterator[Optional[str]]:
            for variant in input_variants:
                formatted_variant = format_variant(variant, log, vendsig_dict)
                yield formatted_variant

        standardized_headers = add_to_headers(headers, case_id)
        output_variants = output_variants_gen()

        log.info(f"Writing standardized VCF to {out_path}/{outfile}")
        line_count = write_vcf(
            standardized_headers,
            output_variants,
            f"{out_path}/{outfile}",
            compression,
            line_count,
            log,
        )
        return line_count
