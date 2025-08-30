import os
from shutil import copyfile
from typing import Union, TypedDict, Optional


class WriteToManifest(TypedDict):
    vcf: bool
    fnv: bool
    cnv: bool


def is_number(s: str):
    try:
        float(s)
        return True
    except ValueError:
        return False


# if date_field is a string then return it as the date
# otherwise, it's a dictionary (due to namespace) so return the `#text` field
def get_date(date_field: Union[str, dict]):
    if isinstance(date_field, str):
        return date_field
    return date_field.get("#text")


def get_mrn(pmi) -> str:
    return pmi["MRN"] if pmi.get("MRN") else ""


def get_trf(sample) -> str:
    return sample.get("TRFNumber", "")


def get_med_facil(pmi) -> list:
    med_facil_info = []
    med_facil_info.append(pmi.get("MedFacilName", ""))
    med_facil_info.append(pmi.get("MedFacilID", ""))
    return med_facil_info


def get_ordering_md(pmi, npi) -> list:
    ordering_md_info = []
    ordering_md_info.append(pmi.get("OrderingMD", ""))
    ordering_md_info.append(npi)
    return ordering_md_info


def get_non_human_content(nhc_dicts: list[dict]) -> list:
    nhc_final = []

    for sub_dict in nhc_dicts:
        nhc_final.append(
            {
                "nhcOrganism": sub_dict.get("@organism", "unknown"),
                "nhcReadsPerMil": float(sub_dict.get("@reads-per-million", 0.0)),
                "nhcStatus": sub_dict.get("@status", "unknown"),
            }
        )

    return nhc_final


def get_plasma_tumor_fraction(genes) -> Optional[str]:
    ptf_dict = {
        "Elevated Tumor Fraction": "Elevated",
        "Elevated Tumor Fraction Not Detected": "Not Elevated",
        "Cannot Be Determined": "Undetermined",
        # 12/5/2023: Foundation renamed `Tumor Fraction` to `ctDNA Tumor Fraction`
        # They also changed the values from `Elevated` and `Not Elevated` to `High` and `Low`
        # We need to support both the old and the new names to account for reingestions
        "Low": "Not Elevated",
        "High": "Elevated",
        # 12/2/2024 Foundation changed "Elevated Tumor Fraction Not Detected" to "Not Detected"
        "Not Detected": "Not Elevated",
    }
    ptf_entry_names = ["Tumor Fraction", "ctDNA Tumor Fraction"]
    entries = genes.get("Gene", [])
    ptf_entry = next((entry for entry in entries if entry.get("Name", "") in ptf_entry_names), None)
    if ptf_entry:
        ptf_val = ptf_entry.get("Alterations", {}).get("Alteration", {}).get("Name", "")
        if ptf_val in ["> 0%", ">0%"]:
            return "Elevated"
        try:
            # See https://github.com/lifeomic/phc-ingestion/pull/129
            float_val = float(ptf_val.strip("%"))
            if float_val > 0:
                return "Elevated"
            elif float_val == 0:
                return "Not Elevated"
        except ValueError:
            # If it's not a numeric value, look it up in the dictionary
            return ptf_dict[ptf_val]
    else:
        return None


def get_plasma_tumor_fraction_score_from_value(value: str) -> Optional[float]:
    if value == "Units Not Reported":
        return None

    stripped_value = value.strip("%")
    try:
        return float(stripped_value)
    except ValueError:
        return None


def get_hrd_status(genes) -> Optional[str]:
    hrd_dict = {
        "HRD Positive": "positive",
        "HRD Not Detected": "negative",
        "HRDsig Positive": "positive",
        "HRDsig Not Detected": "negative",
        "HRDsig Negative": "negative",
    }
    hrd_entry = next(
        (
            entry
            for entry in genes.get("Gene", {})
            if entry.get("Name", "") == "Homologous Recombination status"
            or entry.get("Name", "") == "HRD signature"
        ),
        None,
    )
    if not hrd_entry:
        return None
    hrd_val = hrd_entry.get("Alterations", {}).get("Alteration", {}).get("Name", "")
    return hrd_dict.get(hrd_val, None)


def get_test_yml(
    customer_info_dict: dict,
    results_payload_dict: dict,
    base_xml_name: str,
    local_output_dir: str,
    report_file: str,
    write_to_manifest: WriteToManifest,
    phc_output_dir: str,
    source_file_id: str,
) -> dict:
    npi = customer_info_dict.get("rr:NPI", "")
    pmi = results_payload_dict.get("FinalReport", {}).get("PMI", {})
    signatures = results_payload_dict.get("FinalReport", {}).get("Signatures")
    sample = results_payload_dict.get("FinalReport", {}).get("Sample", {})
    variant_report = results_payload_dict.get("variant-report", {})
    biomarkers = variant_report.get("biomarkers", {})
    non_human_content = variant_report.get("non-human-content", {})
    report_properties = results_payload_dict.get("FinalReport", {}).get("reportProperties", {})
    properties = report_properties.get("reportProperty", [])
    # `Genes` may exist as a key but have a value of None, so we need to ensure it defaults to an empty dict
    genes = results_payload_dict.get("FinalReport", {}).get("Genes", {}) or {}
    plasma_tumor_fraction = get_plasma_tumor_fraction(genes)
    hrd_status = get_hrd_status(genes)
    gw_loh = next(
        (prop for prop in properties if prop.get("@key") == "LossOfHeterozygosityScore"),
        None,
    )
    plasma_tumor_fraction_score_value = next(
        (prop for prop in properties if prop.get("@key") == "ComprehensiveTumorFractionScore"),
        {},
    ).get("value")
    hrd_score = next(
        (
            prop
            for prop in properties
            if prop.get("@key") == "HomologousRecombinationDeficiencyScore"
        ),
        {},
    ).get("value")
    plasma_tumor_fraction_score = None
    if plasma_tumor_fraction_score_value:
        plasma_tumor_fraction_score = get_plasma_tumor_fraction_score_from_value(
            plasma_tumor_fraction_score_value
        )

    os.makedirs(f"{local_output_dir}/{base_xml_name}", exist_ok=True)

    # Hard-code genome reference for FMI
    genome_reference = "GRCh37"

    mrn = get_mrn(pmi)

    trf = get_trf(sample)

    med_facil_info = get_med_facil(pmi)

    ordering_md_info = get_ordering_md(pmi, npi)

    # store both values sperately
    receivedDate = get_date(sample.get("ReceivedDate"))
    collDate = get_date(pmi.get("CollDate"))

    # store date of published report
    reportDate = str(get_date(signatures.get("Signature").get("ServerTime")))[0:10]
    indexedDate = reportDate

    sample_id = (sample.get("SampleId") or "").strip()
    block_id = (sample.get("BlockId") or "").strip()
    if block_id == "N/A":
        block_id = ""

    specimen_ids = []
    if sample_id:
        specimen_ids.append(sample_id)
    if block_id:
        specimen_ids.append(block_id)

    specimenType = sample.get("SpecFormat", "").strip()

    yaml_file = {
        "name": "Foundation Medicine",
        "reference": "GRCh37",
        "sourceFileId": source_file_id,
        "testType": sample.get("TestType"),
        "indexedDate": indexedDate,
        "receivedDate": receivedDate,
        "collDate": collDate,
        "reportDate": reportDate,
        "reportID": trf,
        "mrn": mrn,
        "patientDOB": get_date(pmi.get("DOB")),
        "patientLastName": pmi.get("LastName"),
        "medFacilName": med_facil_info[0],
        "medFacilID": med_facil_info[1],
        "orderingMDName": ordering_md_info[0],
        "orderingMDNPI": ordering_md_info[1],
        "bodySite": variant_report.get("@tissue-of-origin"),
        "bodySiteSystem": "http://lifeomic.com/fhir/sequence-body-site",
        "bodySiteDisplay": variant_report.get("@tissue-of-origin"),
        "indication": pmi.get("SubmittedDiagnosis"),
        "indicationDisplay": pmi.get("SubmittedDiagnosis"),
        "indicationSystem": "http://lifeomic.com/fhir/sequence-indication",
        "files": [],
    }

    if specimen_ids:
        yaml_file["specimenIds"] = specimen_ids
    if specimenType:
        yaml_file["specimenTypes"] = [specimenType]

    if write_to_manifest["cnv"]:
        yaml_file["files"].append(
            {
                "type": "copyNumberVariant",
                "sequenceType": "somatic",
                "fileName": f"{phc_output_dir}/{base_xml_name}/{base_xml_name}.copynumber.csv",
                "reference": genome_reference,
            }
        )

    if write_to_manifest["fnv"]:
        yaml_file["files"].append(
            {
                "type": "structuralVariant",
                "sequenceType": "somatic",
                "fileName": f"{phc_output_dir}/{base_xml_name}/{base_xml_name}.structural.csv",
                "reference": genome_reference,
            }
        )

    if write_to_manifest["vcf"]:
        yaml_file["files"].append(
            {
                "type": "shortVariant",
                "sequenceType": "somatic",
                "fileName": f"{phc_output_dir}/{base_xml_name}/{base_xml_name}.modified.nrm.filtered.vcf.gz",
                "reference": genome_reference,
            }
        )

    yaml_file["patientInfo"] = {
        "firstName": pmi.get("FirstName"),
        "lastName": pmi.get("LastName"),
        "gender": pmi.get("Gender").lower(),
        "dob": get_date(pmi.get("DOB")),
    }

    if mrn:
        yaml_file["patientInfo"]["identifiers"] = [
            {
                "codingSystem": "http://hl7.org/fhir/v2/0203",
                "codingCode": "MR",
                "value": pmi.get("MRN"),
            }
        ]

    if gw_loh:
        values = {"loh-high": "high", "loh-low": "low"}
        alterations = []
        genes_list = genes.get("Gene", [])
        for gene in genes_list:
            alt = gene.get("Alterations", {}).get("Alteration", [])
            alterations.extend(alt) if isinstance(alt, list) else alterations.append(alt)

        loh_alt: dict = next(
            (alt for alt in alterations if values.get(alt.get("Name", "").lower())), {}
        )

        value = gw_loh.get("value", "").replace("%", "")
        # it is possible that value is "Units Not Reported"
        yaml_file["lossOfHeterozygosityScore"] = float(value) if is_number(value) else -1
        yaml_file["lossOfHeterozygosityStatus"] = values.get(
            loh_alt.get("Name", "").lower(), "unknown"
        )

    if biomarkers and "microsatellite-instability" in biomarkers:
        values = {
            "MSI-H": "high",
            "MSI-L": "low",
            "MSS": "stable",
            "unknown": "indeterminate",
        }
        microsatellite_dict = biomarkers["microsatellite-instability"]
        yaml_file["msi"] = values.get(microsatellite_dict.get("@status", "unknown"))

    if biomarkers and "tumor-mutation-burden" in biomarkers:
        tumor_dict = biomarkers["tumor-mutation-burden"]
        yaml_file["tmb"] = tumor_dict.get("@status", "unknown")
        yaml_file["tmbScore"] = float(tumor_dict.get("@score"))

    # adding non-human content fields
    if non_human_content != None:
        yaml_file["nonHumanContent"] = get_non_human_content(non_human_content.get("non-human", []))

    if report_file:
        copyfile(report_file, f"{local_output_dir}/{base_xml_name}/{base_xml_name}.report.pdf")

        yaml_file["reportFile"] = f"{phc_output_dir}/{base_xml_name}/{base_xml_name}.report.pdf"

    # add plasma tumor fraction
    if plasma_tumor_fraction:
        yaml_file["plasmaTumorFraction"] = plasma_tumor_fraction
    # A score of 0 is a valid score, so we need to check for None
    if plasma_tumor_fraction_score != None:
        yaml_file["plasmaTumorFractionScore"] = plasma_tumor_fraction_score

    # add homologous recombination deficiency
    if hrd_status:
        yaml_file["hrdStatus"] = hrd_status
    if hrd_score != None and is_number(hrd_score):
        yaml_file["hrdScore"] = float(hrd_score)

    return yaml_file
