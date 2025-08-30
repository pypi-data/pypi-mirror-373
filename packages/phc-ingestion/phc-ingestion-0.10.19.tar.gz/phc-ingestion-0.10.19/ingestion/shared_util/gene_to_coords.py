import gzip
import os
from logging import Logger


def gene_to_coords(reference_genome, gene):
    BASE_PATH = os.path.abspath(os.path.dirname(__file__))

    # Create reference dict where gene is key, list of chr, pos1, pos2 as value
    ref_dict = {}
    with gzip.open(f"{BASE_PATH}/../resources/{reference_genome}_map.csv.gz", "rt") as f:
        for line in f.readlines()[1:]:
            working_line = line.split(",")
            ref_dict.update(
                {working_line[3].strip(): [working_line[0], working_line[1], working_line[2]]}
            )
    try:
        chromosome = ref_dict.get(gene)[0]

        start_position = ref_dict.get(gene)[1]

        end_position = ref_dict.get(gene)[2]

    except TypeError:
        raise KeyError(f"Input gene {gene} does not exist in the reference dictionary.")

    return chromosome, [start_position, end_position]
