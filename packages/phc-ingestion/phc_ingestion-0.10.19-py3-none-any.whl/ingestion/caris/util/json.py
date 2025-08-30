import glob
import gzip
import json
import os
import shutil

from ingestion.shared_util.tar import unpack
from ingestion.caris.util.metadata import extract_metadata
from ingestion.caris.util.structural import extract_structural
from ingestion.caris.util.cnv import extract_cnv
from ingestion.caris.util.tsv import convert_tsv_to_rgel
from ingestion.caris.util.vcf import extract_sv
from ingestion.shared_util.ga4gh import create_yaml
from logging import Logger

CARIS_CASE_ID_LENGTH = len("TN22-000000")


def handle_tsv(file: str, file_list: list[str]) -> dict[str, str]:
    multiple_tsv = len([file for file in file_list if file.endswith("tsv")]) > 1

    if not multiple_tsv or "Transformed" in file:
        return {
            "tsv": file,
        }
    return {}


def process_caris_json(infile: str, outpath: str, file_name: str, source_file_id: str, log: Logger):
    # Unpack tarball and go into the new directory
    unpack(infile, outpath)
    os.chdir(outpath)

    file_list = glob.glob("*")
    files: dict[str, str] = {}

    # if file_list has more than one file that starts with DNA_ then we need to throw an error
    if len([file for file in file_list if file.startswith("DNA_")]) > 1:
        raise Exception(f"More than one DNA file found in {file_name}\n")

    for file in file_list:
        extension = ".".join(file.split(".")[1:])
        if file.lower().startswith("germline") or file.startswith("gDNA"):
            files["germline.vcf"] = file
        elif file.endswith("vcf") and "germline" not in file:
            files["somatic.vcf"] = file
        elif file.endswith("tsv"):
            files.update(handle_tsv(file, file_list))
        else:
            files[extension] = file

    log.info(f"Files in tarball input: {file_list}")

    json_file = files["json"]

    with open(json_file, "rb") as f:
        data = json.load(f)
    if "root" in data:
        data = data["root"]

    somatic_filename = None
    germline_filename = None
    germline_case_id = None

    # Sometimes they don't come in gzipped
    for key in files.keys():
        if "somatic.vcf" in key:
            somatic_filename = files["somatic.vcf"].replace(".vcf", ".somatic.vcf") + ".gz"
            with open(files["somatic.vcf"], "rb") as f_in:
                with gzip.open(somatic_filename, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
        if "germline.vcf" in key:
            germline_filename = (
                files["germline.vcf"].replace("Germline_", "").replace(".vcf", ".germline.vcf")
                + ".gz"
            )
            with open(files["germline.vcf"], "rb") as f_in:
                with gzip.open(germline_filename, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
            # Liquid cases don't start with `Germline_` and follow a different pattern for germline
            if "germline" in files["germline.vcf"].lower():
                germline_case_id = files["germline.vcf"].replace("Germline_", "")[
                    0:CARIS_CASE_ID_LENGTH
                ]

    # Get patient
    metadata, is_test_cancelled_permit_vcf_skip = extract_metadata(
        data, file_name, files, source_file_id, log
    )
    structural_results = extract_structural(file_name, data, log)
    cnv_results = extract_cnv(file_name, data, log)
    rgel_results = convert_tsv_to_rgel(file_name, files, log)

    include_empty = metadata["ihcTests"] and is_test_cancelled_permit_vcf_skip
    vcf_results = extract_sv(
        file_name, bool(somatic_filename), bool(germline_filename), include_empty
    )

    # We might not have any of these files but we need an empty json object here.
    file_genome_references = {}
    metadata["files"] = []
    if structural_results:
        metadata["files"].append(structural_results)
        file_genome_references["structural_genome_reference"] = structural_results["reference"]
    if rgel_results:
        metadata["files"].append(rgel_results)
        file_genome_references["expression_genome_reference"] = rgel_results["reference"]
    if cnv_results:
        metadata["files"].append(cnv_results)
        file_genome_references["cnv_genome_reference"] = cnv_results["reference"]
    if vcf_results:
        metadata["files"] = metadata["files"] + vcf_results
        for vcf in vcf_results:
            seq_type = vcf.get("sequenceType")
            file_genome_references[f"{seq_type}_genome_reference"] = vcf["reference"]

    create_yaml(metadata, file_name)

    # Return VCF files for immediate processing, and JSON data for adding vendsig
    result = {}

    if somatic_filename is not None:
        result["somatic_vcf"] = f"{outpath}/{somatic_filename}"
    if germline_filename is not None:
        result["germline_vcf"] = f"{outpath}/{germline_filename}"
    if not germline_filename and not somatic_filename and include_empty:
        result["somatic_vcf"] = f"{outpath}/{file_name}.modified.somatic.vcf.gz"

    return (result, germline_case_id, file_genome_references, data)
