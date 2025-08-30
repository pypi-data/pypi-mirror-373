import os

from ingestion.nebula.constants import NEBULA_TEST_TYPE
from ingestion.shared_util.ga4gh import create_yaml
from ingestion.vcf_standardization.standardize import standardize_vcf
from lifeomic_logging import scoped_logger
from ingestion.nebula.manifest_assembler import ManifestAssembler


def process(vcf_file, out_path, file_name, source_file_id, ingestion_id, account_id, project_id):

    with scoped_logger(__name__) as log:
        log.info(
            f"Beginning Nebula ingestion for vcf_file: {vcf_file}, file_name: {file_name}, out_path: {out_path}, source_file_id: {source_file_id}"
        )

        case_id = file_name
        manifest = ManifestAssembler(
            ingestion_id, account_id, project_id, case_id, vcf_file
        ).create_manifest()
        base_vcf_file = os.path.basename(vcf_file)
        vcf_out = base_vcf_file.replace(".vcf", ".modified.vcf")
        vcf_final = base_vcf_file.replace(".vcf", ".modified.nrm.filtered.vcf")
        if not vcf_final.endswith(".gz"):
            vcf_final = vcf_final + ".gz"

        # All Nebula VCF ingestions are germline, so ensure the
        # sample name is prefixed with "germline_". This matches
        # the downstream logic in genomic-manifest
        sample_name = f"germline_{case_id}"
        vcf_line_count = standardize_vcf(
            vcf_file, vcf_out, out_path, sample_name, log, compression=True
        )

        # Add to manifest
        manifest["testType"] = NEBULA_TEST_TYPE
        manifest["reportID"] = case_id
        manifest["sourceFileId"] = source_file_id
        manifest["resources"] = [{"fileName": f".lifeomic/nebula/{case_id}/{base_vcf_file}"}]
        manifest["files"] = [
            {
                "fileName": f".lifeomic/nebula/{case_id}/{vcf_final}",
                "sequenceType": "germline",
                "type": "shortVariant",
            }
        ]

        create_yaml(manifest, f"{out_path}/{file_name}")

        # Hard-code genome reference for Nebula VCFs
        genome_reference = "GRCh38"

        case_metadata = {
            "test_type": manifest["testType"],
            "vcf_line_count": vcf_line_count,
            "germline_case_id": manifest["reportID"],
            "germline_genome_reference": genome_reference,
        }

        return case_metadata, manifest
