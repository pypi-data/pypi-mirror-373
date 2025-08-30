from typing import TypedDict, Literal


class HlaResult(TypedDict):
    gene: Literal["HLA-A", "HLA-B", "HLA-C"]
    interpretation: str
    mhClass: Literal["I", "gDNA"]
    genotype: str


def extract_hla_result_from_test_result(test_result) -> HlaResult:
    gene = test_result.get("gene", "")
    if gene not in ["HLA-A", "HLA-B", "HLA-C"]:
        raise RuntimeError(f"Unknown HLA gene detected: {gene}")
    interpretation = test_result.get("result_group", "")
    mh_class = test_result.get("mhClass", "")
    if mh_class not in ["I", "gDNA"]:
        raise RuntimeError(f"Unknown MHC class detected: {mh_class}")

    genotype = test_result.get("genotype", "")

    return HlaResult(gene=gene, interpretation=interpretation, mhClass=mh_class, genotype=genotype)
