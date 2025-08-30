import re
from logging import Logger

from ingestion.caris.util.hla import extract_hla_result_from_test_result
from ingestion.caris.util.ihc import get_ihc_results
from ingestion.caris.util.specimen_details import extract_and_parse_specimen_details
from ingestion.caris.util.tests import safely_extract_tests_from_json_data
from ingestion.caris.util.tmb import parse_tumor_mutation_burden

MSI_MAPPINGS = {
    "low": "low",
    "stable": "stable",
    "high": "high",
    "indeterminate": "indeterminate",
    "equivocal": "indeterminate",
}


def get_report_date(test_details, log: Logger) -> str:
    try:
        test_details["approvalInformation"]["approveDate"].split()[0]
    except KeyError:
        log.info("JSON does not contain approval information")
        return ""

    else:
        return test_details["approvalInformation"]["approveDate"].split()[0]


def get_ordering_md_name(physician_details) -> str:
    return (
        f'{physician_details["lastName"]}, {physician_details["firstName"]}'
        if physician_details.get("lastName") and physician_details.get("firstName")
        else ""
    )


def get_ordering_md_npi(physician_details) -> int:
    return physician_details.get("npi", "")


def get_med_facil_name(physician_details) -> str:
    return physician_details.get("organization", "")


def get_med_facil_id(physician_details) -> int:
    return physician_details.get("sourceID", "")


def get_report_id(test_details) -> str:
    return test_details.get("labReportID", "")


def get_physician_details(data) -> dict:
    return data.get("physicianInformation", {})


def get_test_type(data):
    if re.search(r"liquidBiopsy", data):
        return "Assure"
    if re.search(r"Hybrid_Transcriptome", data):
        return "MI Profile - Hybrid"
    return "MI Profile"


# In the array of Caris test entries, there are only some that we care about
def is_valid_test_entry(test: dict):
    if "test_cancellation_reason" in test:
        return False

    search_expressions = [r"clinical genes", r"liquid germline", r"lp exome variants"]

    is_seq = test.get("testMethodology") == "Seq"
    has_matching_name = any(
        re.search(expr, test["testName"], re.IGNORECASE) for expr in search_expressions
    )

    return is_seq and has_matching_name


# Build up the manifest iteratively because almost everything is optional
def extract_metadata(data, prefix, files, source_file_id, log: Logger) -> dict:
    is_test_cancelled_permit_vcf_skip = False
    metadata = {}

    test_details = data["testDetails"]

    specimen_details = extract_and_parse_specimen_details(data, log)

    physician_details = get_physician_details(data)

    metadata["testType"] = get_test_type(str(data))

    # Get date of collected and received for the specimen
    metadata["receivedDate"] = specimen_details["receivedDate"]
    metadata["collDate"] = specimen_details["collDate"]
    if specimen_details["specimenId"]:
        metadata["specimenIds"] = [specimen_details["specimenId"]]
    if specimen_details["specimenTypes"]:
        metadata["specimenTypes"] = specimen_details["specimenTypes"]
    metadata["reportDate"] = get_report_date(test_details, log)

    # Get the date without the time
    metadata["indexedDate"] = metadata["reportDate"]

    patient = data["patientInformation"]
    metadata["bodySiteSystem"] = "http://lifeomic.com/fhir/sequence-body-site"
    metadata["reportID"] = get_report_id(test_details)
    metadata["mrn"] = patient["mrn"]
    metadata["patientLastName"] = patient["lastName"]

    metadata["patientDOB"] = patient["dob"]

    # Get physician info - ordering name, NPI, and facility
    metadata["medFacilName"] = get_med_facil_name(physician_details)
    metadata["medFacilID"] = get_med_facil_id(physician_details)
    metadata["orderingMDName"] = get_ordering_md_name(physician_details)
    metadata["orderingMDNPI"] = get_ordering_md_npi(physician_details)

    metadata["indicationSystem"] = "http://lifeomic.com/fhir/sequence-indication"
    metadata["indication"] = patient["diagnosis"]
    metadata["indicationDisplay"] = metadata["indication"]

    metadata["bodySite"] = specimen_details["bodySite"]
    metadata["bodySiteDisplay"] = metadata["bodySite"]
    metadata["sourceFileId"] = source_file_id
    pdf = files["pdf"]
    metadata["reportFile"] = f".lifeomic/caris/{prefix}/{pdf}"

    # Some patients do not have an MRN
    patientInfo = (
        {
            "lastName": metadata["patientLastName"],
            "dob": metadata["patientDOB"],
            "firstName": patient["firstName"],
            "gender": patient["gender"].lower(),
            "identifiers": [
                {
                    "codingCode": "MR",
                    "codingSystem": "http://hl7.org/fhir/v2/0203",
                    "value": metadata["mrn"],
                }
            ],
        }
        if metadata["mrn"]
        else {
            "lastName": metadata["patientLastName"],
            "dob": metadata["patientDOB"],
            "firstName": patient["firstName"],
            "gender": patient["gender"].lower(),
        }
    )

    # Ensure no null entries
    metadata["patientInfo"] = {k: v for k, v in patientInfo.items() if v}
    metadata.update({"name": "Caris", "reference": "GRCh37"})
    metadata["hlaResults"] = []

    # Now find the test information

    tests = safely_extract_tests_from_json_data(data)

    # if not sufficient quantity we won't have test results
    if test_details["reportType"] != "QNS":
        for test in tests:
            if "test_cancellation_reason" in test:
                if test["test_cancellation_reason"] == "Quantitation quantity not sufficient":
                    # capture cancellation reason before bailing
                    # this is so we can generate an empty vcf so present biomarkers are
                    # still ingested: https://lifeomic.atlassian.net/browse/PHC-5748
                    is_test_cancelled_permit_vcf_skip = True

            if not is_valid_test_entry(test):
                continue
            # Sometimes, if there is only a single test result,
            # Caris will set it as a dict instead of a list
            test_results = (
                [test["testResults"]]
                if isinstance(test["testResults"], dict)
                else test["testResults"]
            )
            for info in test_results:
                if "tumorMutationBurden" in info.keys():
                    parsed_tmb = parse_tumor_mutation_burden(info["tumorMutationBurden"])
                    if not parsed_tmb:
                        continue
                    metadata["tmb"] = parsed_tmb["tmb"]
                    metadata["tmbScore"] = parsed_tmb["tmbScore"]
                elif "microsatelliteInstability" in info.keys():
                    # if the key isn't found we will get an error during manifest processing
                    # it would be better to fail here, i.e. fail fast, but our alerting
                    # is much better at the manifest level so doing a default value for now
                    msi_key = info["microsatelliteInstability"]["msiCall"].lower()
                    if msi_key == "not detected":
                        continue
                    if msi_key in MSI_MAPPINGS:
                        metadata["msi"] = MSI_MAPPINGS[msi_key]
                    else:
                        metadata["msi"] = msi_key
                elif "genomicLevelHeterozygosity" in info.keys():
                    loh_status = info["genomicLevelHeterozygosity"]["result"].lower()
                    loh_score = info["genomicLevelHeterozygosity"]["LOHpercentage"]
                    # This comes out as a string, convert to integer for proper ingestion
                    metadata["lossOfHeterozygosityScore"] = int(loh_score)
                    metadata["lossOfHeterozygosityStatus"] = (
                        "qns" if loh_status == "quality not sufficient" else loh_status
                    )
                elif "genomicScarScore" in info.keys():
                    hrd_status = info["genomicScarScore"]["result"].lower()
                    hrd_score = info["genomicScarScore"]["score"]
                    # This comes out as a string, convert to integer for proper ingestion
                    metadata["hrdStatus"] = (
                        "qns" if hrd_status == "quality not sufficient" else hrd_status
                    )
                elif "genomicAlteration" in info and "HLA" in info["genomicAlteration"].get(
                    "biomarkerName", ""
                ):
                    metadata["hlaResults"].append(
                        extract_hla_result_from_test_result(info["genomicAlteration"])
                    )

    # Add IHC test results to manifest
    metadata["ihcTests"] = get_ihc_results(data, log)

    # Add in the additional resources as linkable
    metadata["resources"] = []
    ingest_files = [
        "nrm.vcf.gz",
        "tmp",
        "ga4gh.genomics.yml",
        "runner",
        "yml",
        "ga4gh.yml",
        "copynumber.csv",
        "structural.csv",
        "pdf",
    ]
    for ext, filename in files.items():
        if ext not in ingest_files:
            if ext != "bam" and "fastq" not in ext:
                metadata["resources"].append({"fileName": f".lifeomic/caris/{prefix}/{filename}"})
            else:
                for f in files[ext]:
                    metadata["resources"].append({"fileName": f".lifeomic/caris/{prefix}/{f}"})
                    if ext == "bam":
                        metadata["resources"].append(
                            {"fileName": f".lifeomic/caris/{prefix}/{f}.bai"}
                        )
            # If we got RNAseq results let us also make json files available
            if ext == "tsv":
                metadata["resources"].append(
                    {"fileName": f".lifeomic/caris/{prefix}/{prefix}.expression.cancerscope.json"}
                )
                metadata["resources"].append(
                    {"fileName": f".lifeomic/caris/{prefix}/{prefix}.expression.pcann.json"}
                )

    active_metadata = {k: v for k, v in metadata.items() if v is not None}
    return (active_metadata, is_test_cancelled_permit_vcf_skip)
