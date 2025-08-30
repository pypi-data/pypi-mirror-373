from typing import TypedDict


class GeneWithLocation(TypedDict):
    gene: str
    chr: str
    start: int
    end: int


nextgen_specific_genes_with_location: list[GeneWithLocation] = [
    {"gene": "IGK", "chr": "chr2", "start": 88852034, "end": 90258119},
    {"gene": "NSD2", "chr": "chr4", "start": 1792518, "end": 1940193},
    {"gene": "CCND3", "chr": "chr6", "start": 41920534, "end": 42562008},
    {"gene": "MYC", "chr": "chr8", "start": 125309416, "end": 129673293},
    {"gene": "CCND1", "chr": "chr11", "start": 69090733, "end": 69656860},
    {"gene": "IGH", "chr": "chr14", "start": 105325507, "end": 109902208},
    {"gene": "MAF", "chr": "chr16", "start": 78428398, "end": 79615096},
    {"gene": "MAFB", "chr": "chr20", "start": 39039005, "end": 40688948},
    {"gene": "IGL", "chr": "chr22", "start": 22012552, "end": 22965858},
]
nextgen_specific_genes: set[str] = {gene["gene"] for gene in nextgen_specific_genes_with_location}


def maybe_get_nextgen_specific_gene(chr: str, position: int) -> str | None:
    for gene in nextgen_specific_genes_with_location:
        if gene["chr"] == chr and gene["start"] <= position <= gene["end"]:
            return gene["gene"]
    return None
