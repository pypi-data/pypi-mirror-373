import os

from ingestion.caris.util.json import process_caris_json
from ingestion.caris.util.vcf import process_caris_vcf
from ingestion.caris.util.metadata import get_test_type
from lifeomic_logging import scoped_logger


def process_caris(infile, outpath, file_name, source_file_id):

    with scoped_logger(__name__) as log:
        os.makedirs(f"{outpath}", exist_ok=True)
        somatic_vcf_line_count = 0
        germline_vcf_line_count = 0
        result, germline_case_id, file_genome_references, json_data = process_caris_json(
            infile, outpath, file_name, source_file_id, log
        )
        caris_test_type = get_test_type(str(json_data))
        if "somatic_vcf" in result:
            somatic_vcf_line_count = process_caris_vcf(
                result["somatic_vcf"], json_data, outpath, file_name, log
            )
        if "germline_vcf" in result:
            germline_vcf_line_count = process_caris_vcf(
                result["germline_vcf"], json_data, outpath, file_name, log
            )
        case_metadata = {
            "germline_case_id": germline_case_id,
            "somatic_vcf_line_count": somatic_vcf_line_count,
            "germline_vcf_line_count": germline_vcf_line_count,
            "test_type": caris_test_type,
        }

        if file_genome_references != {}:
            case_metadata.update(file_genome_references)

        return case_metadata
