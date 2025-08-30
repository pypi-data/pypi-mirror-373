import os

from ingestion.vcf_standardization.standardize import standardize_vcf
from ingestion.generic.utils import check_manifest
from lifeomic_logging import scoped_logger


def process(
    manifest_file: str, vcf_file: str, source_file_id: str, out_path: str, case_id: str
) -> dict[str, str]:
    with scoped_logger(__name__) as log:

        # Read in supplied manifest
        manifest = check_manifest(manifest_file, case_id, log)

        # Process VCF
        base_vcf_file = os.path.basename(vcf_file)
        vcf_out = base_vcf_file.replace(".vcf", ".modified.vcf")
        vcf_final = base_vcf_file.replace(".vcf", ".modified.nrm.filtered.vcf")
        if not vcf_final.endswith(".gz"):
            vcf_final = vcf_final + ".gz"
        # All generic VCF ingestions are germline, so ensure the
        # sample name is prefixed with "germline_". This matches
        # the downstream logic in genomic-manifest
        sample_name = f"germline_{case_id}"
        vcf_line_count = standardize_vcf(
            vcf_file, vcf_out, out_path, sample_name, log, compression=True
        )

        # Add to manifest
        manifest["sourceFileId"] = source_file_id
        manifest["resources"] = [{"fileName": f".lifeomic/vcf-ingest/{case_id}/{base_vcf_file}"}]
        manifest["files"] = [
            {
                "fileName": f".lifeomic/vcf-ingest/{case_id}/{vcf_final}",
                "sequenceType": "germline",
                "type": "shortVariant",
            }
        ]

        case_metadata = {
            "test_type": manifest["testType"],
            "vcf_line_count": vcf_line_count,
            "case_id": manifest["reportID"],
            "germline_genome_reference": manifest["reference"],
        }

        return case_metadata, manifest
