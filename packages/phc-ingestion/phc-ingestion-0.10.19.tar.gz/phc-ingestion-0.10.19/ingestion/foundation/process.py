from lifeomic_logging import scoped_logger
import xmltodict
from ruamel.yaml import YAML
from pathlib import Path

from ingestion.foundation.util.cnv import extract_copy_numbers
from ingestion.foundation.util.fnv import extract_fusion_variant
from ingestion.foundation.util.ga4gh import get_test_yml
from ingestion.foundation.util.vcf_etl import vcf_etl


def read_xml(xml_file: str) -> dict:
    with open(xml_file) as fd:
        return xmltodict.parse(fd.read(), force_list=("reportProperty", "non-human", "Gene"))


def process(
    xml_file: str,
    vcf_file: str,
    report_file: str,
    local_output_dir: str,
    source_file_id: str,
    phc_output_dir: str = ".lifeomic/foundation",
) -> dict[str, str]:
    with scoped_logger(__name__) as log:
        xml_dict = read_xml(xml_file)
        customer_info_dict = xml_dict["rr:ResultsReport"]["rr:CustomerInformation"]
        results_payload_dict = xml_dict["rr:ResultsReport"]["rr:ResultsPayload"]

        base_xml_name = Path(xml_file).stem

        vcf_name = f"{local_output_dir}/{base_xml_name}/{base_xml_name}.modified.vcf"
        vcf_line_count = vcf_etl(vcf_file, vcf_name, base_xml_name, xml_file, log)
        write_cnv = extract_copy_numbers(results_payload_dict, base_xml_name, local_output_dir, log)
        write_fnv = extract_fusion_variant(
            results_payload_dict, base_xml_name, local_output_dir, log
        )

        yaml_file = get_test_yml(
            customer_info_dict,
            results_payload_dict,
            base_xml_name,
            local_output_dir,
            report_file,
            {"cnv": write_cnv, "vcf": vcf_line_count != 0, "fnv": write_fnv},
            phc_output_dir,
            source_file_id,
        )

        with open(
            f"{local_output_dir}/{base_xml_name}/{base_xml_name}.ga4gh.genomics.yml",
            "w",
        ) as file:
            yaml = YAML()
            yaml.dump(yaml_file, file)

        # Hard-code genome reference for FMI
        genome_reference = "GRCh37"

        case_metadata = {
            "test_type": yaml_file["testType"],
            "vcf_line_count": vcf_line_count,
            "case_id": base_xml_name,
            "somatic_genome_reference": genome_reference,
        }

        if write_cnv:
            case_metadata["cnv_genome_reference"] = genome_reference
        if write_fnv:
            case_metadata["structural_genome_reference"] = genome_reference

        return case_metadata
