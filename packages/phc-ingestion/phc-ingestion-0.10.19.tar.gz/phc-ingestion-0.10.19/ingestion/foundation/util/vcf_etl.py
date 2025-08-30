import gzip
import xmltodict
from logging import Logger
import re
import os
import errno

from ingestion.vcf_standardization.standardize import standardize_vcf


def vcf_etl(in_vcf: str, out_vcf: str, base_xml_name: str, xml_file: str, log: Logger) -> int:
    if not os.path.exists(os.path.dirname(out_vcf)):
        try:
            os.makedirs(os.path.dirname(out_vcf))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

    # Get xml short variant entries for scraping vendsig
    xml_short_vars = get_xml_short_vars(xml_file, log)
    outfile = out_vcf.split("/")[-1]
    out_path = out_vcf.replace(f"/{outfile}", "")

    line_count = standardize_vcf(
        infile=in_vcf,
        outfile=outfile,
        out_path=out_path,
        case_id=base_xml_name,
        log=log,
        vendsig_dict=xml_short_vars,
        compression=True,
    )

    return line_count


def map_vendsig(vendsig: str) -> str:
    if vendsig in ["known"]:
        return "Pathogenic"
    elif vendsig in ["likely"]:
        return "Likely pathogenic"
    elif vendsig in ["unknown"]:
        return "Uncertain significance"
    else:
        return "Unknown"


def get_xml_short_vars(xml_file: str, log):
    vendsig_dict = {"vendor": "foundation"}

    # xml_dict returns a dictionary if only one variant present, otherwise a list of dictionaries
    with open(xml_file) as fd:
        xml_dict = xmltodict.parse(fd.read())
    try:
        xml_short_vars = xml_dict["rr:ResultsReport"]["rr:ResultsPayload"]["variant-report"][
            "short-variants"
        ]["short-variant"]
    except KeyError as e:
        log.info(f"Missing key in XML structure for short variants: {str(e)}")
        return vendsig_dict
    except TypeError:
        log.info("No short variants found in xml")
        return vendsig_dict

    xml_short_vars = [xml_short_vars] if isinstance(xml_short_vars, dict) else xml_short_vars
    for var in xml_short_vars:
        gene_id = var.get("@gene", "")
        depth = var.get("@depth", "")
        lookup_key = f"{gene_id}:{depth}"

        vendsig = var.get("@status", "")
        mapped_vendsig = map_vendsig(vendsig)

        vendsig_dict.update({lookup_key: mapped_vendsig})

    return vendsig_dict
