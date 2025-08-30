import gzip
import os
from logging import Logger


def find_gene(reduced_map_dict, coordinate):
    for gene in reduced_map_dict.items():
        if coordinate > int(gene[1][1]) and coordinate < int(gene[1][2]):
            return gene[0]

    # If given coordinate is not within a gene, check walk out 100bp at a time to find the nearest gene
    for iteration in range(1, 200):
        for gene in reduced_map_dict.items():
            above = coordinate + (100 * iteration)
            if above > int(gene[1][1]) and above < int(gene[1][2]):
                return gene[0]

            below = coordinate - (100 * iteration)
            if below > int(gene[1][1]) and below < int(gene[1][2]):
                return gene[0]


def coords_to_genes(reference_genome, chromosome, coordinate, log):
    BASE_PATH = os.path.abspath(os.path.dirname(__file__))

    # Create reference dict where gene is key, list of chr, pos1, pos2 as value
    ref_dict = {}
    with gzip.open(f"{BASE_PATH}/../resources/{reference_genome}_map.csv.gz", "rt") as f:
        for line in f.readlines()[1:]:
            working_line = line.split(",")
            ref_dict.update(
                {working_line[3].strip(): [working_line[0], working_line[1], working_line[2]]}
            )

    # Dictionary comprehension by chromosome
    reduced_map_dict = {k: v for (k, v) in ref_dict.items() if v[0] == chromosome}

    matched_gene = find_gene(reduced_map_dict, coordinate)

    if matched_gene == None:
        matched_gene = "N/A"
        log.info(
            f"Input coordinates {chromosome}:{coordinate} does not exist in the reference dictionary."
        )

    return matched_gene
