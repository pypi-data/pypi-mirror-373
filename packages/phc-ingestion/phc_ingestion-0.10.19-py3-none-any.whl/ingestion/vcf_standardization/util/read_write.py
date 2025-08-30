import gzip
from logging import Logger
import re
import os
from typing import Iterator, Optional


def check_vcf(infile: str, log: Logger) -> None:
    log.info("Checking VCF file")
    # Check if file exists. Raise if it doesn't.
    if os.path.exists(infile) == False:
        raise RuntimeError(f'Given file path "{infile}" could not be located')

    if not (infile.endswith((".vcf", ".vcf.gz"))):
        raise RuntimeError(f'Given file "{infile}" must be in vcf or vcf.gz format')


def read_variants(f) -> Iterator[str]:
    for line in f:
        record = re.sub(" ", "", line.rstrip("\r\n"))
        if record.startswith("#"):
            continue
        yield record


def read_headers(f):
    headers = []
    for line in f:
        record = line.rstrip("\r\n")
        if record.startswith("#"):
            if not record.startswith("##INFO"):
                headers.append(record)
            else:
                if record.split(",")[1] == "Number=0" and record.split(",")[2] != "Type=Flag":
                    continue
                headers.append(record)

        else:
            break

    return headers


def add_to_headers(headers: list, case_id) -> list:
    headers_to_add = [
        '##INFO=<ID=AF,Number=A,Type=Float,Description="Allele frequency, for each ALT allele, in the same order as listed">',
        '##FORMAT=<ID=AD,Number=.,Type=Integer,Description="Number of reads harboring allele (in order specified by GT)">',
        '##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Read depth">',
        '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">',
        '##INFO=<ID=VENDSIG,Number=1,Type=String,Description="Vendor Significance">',
    ]
    for new_header in headers_to_add:
        if new_header not in headers:
            headers.insert(-1, new_header)

    case_id_header = f"#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t{case_id}"

    if case_id_header not in headers:
        headers.insert(-1, case_id_header)
        return headers[:-1]

    return headers


def write_vcf(
    headers: list,
    variants_gen: Iterator[Optional[str]],
    outfile: str,
    compression: bool,
    line_count: int,
    log,
) -> int:
    log.info(f"Writing standardized VCF to {outfile}")

    with gzip.open(outfile, "wt") if compression else open(outfile, "w") as w:
        w.write("\n".join(headers) + "\n")
        for variant in variants_gen:
            line_count += 1
            if variant:
                w.write(variant + "\n")

    return line_count
