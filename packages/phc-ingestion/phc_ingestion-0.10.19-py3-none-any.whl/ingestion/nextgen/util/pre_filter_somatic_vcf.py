from logging import Logger

from ingestion.nextgen.util.alteration_table import AlterationTableRow, ShortVariantGene
from ingestion.shared_util.open_maybe_gzipped import open_maybe_gzipped


def build_variant_key_from_vcf_line(line: str) -> str:
    split_line = line.strip().split("\t")
    chrom, pos, ref, alt = split_line[0], split_line[1], split_line[3], split_line[4]
    return f"{chrom}:{pos}:{ref}:{alt}"


def extract_filter_from_vcf_line(line: str) -> str:
    split_line = line.strip().split("\t")
    return split_line[6]


def replace_filter_in_line(line: str, new_filter: str) -> str:
    split_line = line.strip().split("\t")
    split_line[6] = new_filter
    return "\t".join(split_line) + "\n"


def is_line_in_alteration_table(
    line: str, short_variant_table_rows: list[AlterationTableRow[ShortVariantGene]]
) -> bool:
    """
    Returns True if the line in the VCF appears in
    the alteration table, False otherwise.

    Matching in the alteration table is less strict than in the
    VCF files; we only need to match chromosome and position.

    Also position may differ by +1 or -1, as deletion and insertion positions
    are represented differently in the VCF and the alteration table.
    """
    split_line = line.strip().split("\t")
    chrom, pos = split_line[0], int(split_line[1])

    for row in short_variant_table_rows:
        ref_chrom, ref_pos = row["gene"]["chr"], row["gene"]["pos"]

        if ref_chrom == chrom and (abs(ref_pos - pos) <= 1):
            return True

    return False


def pre_filter_somatic_vcf(
    somatic_vcf_file: str,
    somatic_vcf_snv_file: str,
    somatic_vcf_indel_file: str,
    short_variant_table_rows: list[AlterationTableRow[ShortVariantGene]],
    working_dir: str,
    log: Logger,
) -> str:
    """
    Removes all variants from the `somatic_vcf_file` that are not
    also in the `somatic_vcf_snv_file`, the `somatic_vcf_indel_file`,
    or the alteration table.

    Also updates the FILTER field in the `somatic_vcf_file` to match
    the FILTER field of the corresponding variant in the
    `somatic_vcf_snv_file` or `somatic_vcf_indel_file`.
    For variants in the alteration table, the original FILTER field is kept.
    """
    log.info("Pre-filtering somatic VCF file")

    valid_variants_with_filters: dict[str, str] = {}

    for file in [somatic_vcf_snv_file, somatic_vcf_indel_file]:
        with open_maybe_gzipped(file, "rt") as f:
            for line in f:
                if line.startswith("#"):
                    continue
                valid_variants_with_filters[build_variant_key_from_vcf_line(line)] = (
                    extract_filter_from_vcf_line(line)
                )

    log.info(f"Found {len(valid_variants_with_filters)} valid variants in the SNV and INDEL files")

    output_vcf_path = f"{working_dir}/filtered_somatic.vcf.gz"
    with (
        open_maybe_gzipped(somatic_vcf_file, "rt") as r,
        open_maybe_gzipped(output_vcf_path, "wt") as w,
    ):
        for line in r:
            if line.startswith("#"):
                w.write(line)
            else:
                key = build_variant_key_from_vcf_line(line)
                if key in valid_variants_with_filters:
                    w.write(replace_filter_in_line(line, valid_variants_with_filters[key]))
                elif is_line_in_alteration_table(line, short_variant_table_rows):
                    w.write(line)

    log.info(f"Successfully pre-filtered somatic VCF file to {output_vcf_path}")
    return output_vcf_path
