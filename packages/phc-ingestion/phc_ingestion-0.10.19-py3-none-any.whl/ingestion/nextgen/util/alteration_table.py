from logging import Logger
import re
from typing import TypedDict, Generic, TypeVar


T = TypeVar("T")


class AlterationTableRow(Generic[T], TypedDict):
    gene: T
    type: str
    description: str
    vaf: str
    info: str


class ShortVariantGene(TypedDict):
    chr: str
    pos: int


class CopyNumberVariantGene(TypedDict):
    gene: str
    chr: str
    start: int
    end: int


class StructuralVariantGene(TypedDict):
    gene1: str
    chr1: str
    pos1: int
    gene2: str
    chr2: str
    pos2: int


base_short_variant_types: list[str] = [
    "Missense",
    "Frameshift",
    "Stop gained",
    "Stop lost",
    "Inframe deletion",
    "In-frame deletion",
    "Inframe insertion",
    "In-frame insertion",
    "Inframe",
    "In-frame",
    "Splice site",
    "Splice region",
    "Nonsense",
    "Splice acceptor",
    "Splice donor",
]


def get_short_variant_types() -> list[str]:
    # For multi-word short variant types, sometimes the spaces are not included
    short_variant_types: list[str] = []
    for short_variant_type in base_short_variant_types:
        short_variant_types.append(short_variant_type)
        if " " in short_variant_type:
            short_variant_types.append(short_variant_type.replace(" ", ""))

    return short_variant_types


def extract_all_table_lines(xml_in_file: str) -> list[str]:
    with open(xml_in_file, "r") as f:
        xml_lines = f.readlines()

    in_range_trigger = False
    table_lines: list[str] = []
    for line in xml_lines:
        if "Gene (Chr. Position, hg38)" in line:
            in_range_trigger = True
        if in_range_trigger:
            if "</Table>" in line:
                break
            table_lines.append(line)

    return table_lines


def extract_alteration_table_rows(xml_in_file: str, log: Logger) -> list[AlterationTableRow[str]]:
    table_lines = extract_all_table_lines(xml_in_file)
    # Remove completely empty lines
    table_lines = [line for line in table_lines if line.strip() != ""]

    table_row_lines: list[list[str]] = []
    current_row: list[str] = []
    for line in table_lines:
        if line.strip() == "</TR>":
            if current_row:
                table_row_lines.append(current_row)
                current_row = []
        line = re.sub(r"<\/?T.\/?>", "", line).strip()
        if line and line != "p.":
            current_row.append(line)

    alteration_table_rows: list[AlterationTableRow[str]] = []

    # Skip the first row which is the header
    for row in table_row_lines[1:]:
        # Sometimes the alteration table is "empty", in which case the `type` column will only contain "NA" values
        if row[1] == "NA":
            continue
        alteration_table_rows.append(
            {
                "gene": row[0],
                "type": row[1],
                "description": row[2],
                "vaf": row[3],
                # Sometimes the info column is empty, so we need to check if it actually exists
                # So far, it seems like rows with empty "info" columns are generally not useful for us
                # and the data in them will not be used anywhere, so we just fill in an empty string
                "info": row[4] if len(row) > 4 else "",
            }
        )

    return alteration_table_rows


def parse_short_variant_gene(gene: str) -> ShortVariantGene:
    pattern = r"^.*\((?P<chr>chr\d+|chrX|chrY):(?P<pos>\d+).*$"
    match = re.match(pattern, gene)
    if not match:
        raise RuntimeError(f"Failed to parse gene field for short variant")
    return {"chr": match.group("chr"), "pos": int(match.group("pos"))}


def parse_copy_number_variant_gene(gene: str) -> CopyNumberVariantGene:
    pattern = r"^(?P<gene>[A-Z1-9]*).*?\((?P<chr>chr\d+|chrX|chrY):(?P<start>\d+)_(?P<end>\d+)\).*$"
    match = re.match(pattern, gene)
    if not match:
        raise RuntimeError(f"Failed to parse gene field for copy number variant")
    return {
        "gene": match.group("gene"),
        "chr": match.group("chr"),
        "start": int(match.group("start")),
        "end": int(match.group("end")),
    }


def parse_structural_variant_gene(gene: str) -> StructuralVariantGene:
    pattern = r"^\*?(?P<gene1>[A-Z1-9]*)(-|\/|:+)(?P<gene2>[A-Z1-9]*).*\(.*(?P<chr1>chr\d+|chrX|chrY):(?P<pos1>\d+).*;.*(?P<chr2>chr\d+|chrX|chrY):(?P<pos2>\d+).*\).*$"
    match = re.match(pattern, gene)
    if not match:
        raise RuntimeError(f"Failed to parse gene field for structural variant")
    return {
        "gene1": match.group("gene1"),
        "chr1": match.group("chr1"),
        "pos1": int(match.group("pos1")),
        "gene2": match.group("gene2"),
        "chr2": match.group("chr2"),
        "pos2": int(match.group("pos2")),
    }


def extract_variant_table_rows_and_hyperdiploidy(xml_in_file: str, log: Logger) -> tuple[
    list[AlterationTableRow[ShortVariantGene]],
    list[AlterationTableRow[CopyNumberVariantGene]],
    list[AlterationTableRow[StructuralVariantGene]],
    list[str] | None,
]:
    alteration_table_rows = extract_alteration_table_rows(xml_in_file, log)

    short_variant_rows: list[AlterationTableRow[ShortVariantGene]] = []
    copy_number_rows: list[AlterationTableRow[CopyNumberVariantGene]] = []
    structural_variant_rows: list[AlterationTableRow[StructuralVariantGene]] = []
    hyperdiploidy_chromosomes: list[str] | None = None

    short_variant_types = get_short_variant_types()

    for row in alteration_table_rows:
        if row["type"] in short_variant_types:
            short_variant_rows.append({**row, "gene": parse_short_variant_gene(row["gene"])})
        elif row["type"] == "CNV":
            copy_number_rows.append({**row, "gene": parse_copy_number_variant_gene(row["gene"])})
        elif row["type"] == "Translocation":
            structural_variant_rows.append(
                {**row, "gene": parse_structural_variant_gene(row["gene"])}
            )
        elif row["type"] == "Hyperdiploidy":
            hyperdiploidy_chromosomes = re.findall(r"\d+", row["gene"])

    return short_variant_rows, copy_number_rows, structural_variant_rows, hyperdiploidy_chromosomes
