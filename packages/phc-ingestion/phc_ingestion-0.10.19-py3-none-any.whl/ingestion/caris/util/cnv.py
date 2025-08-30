from logging import Logger

from ingestion.shared_util.gene_to_coords import gene_to_coords
from ingestion.caris.util.tests import safely_extract_tests_from_json_data


def extract_cnv(prefix, data, log: Logger):
    # Get all CNV calls into a csv
    caris_lo_keywords = {"intermediate": "gain", "amplified": "amplification", "deleted": "loss"}
    extracted_tests = safely_extract_tests_from_json_data(data)
    copy_number_variant_tests = []
    for test in extracted_tests:
        # We don't want to bring in "not detected" or wild type results
        test_name = test["testName"]
        if ("CNA" in test_name or "CND" in test_name) and "testResults" in test.keys():
            test = test["testResults"]
            if isinstance(test, dict):
                test = [test]
            for cna in test:
                if "copyNumberAlteration" in cna.keys():
                    results = cna["copyNumberAlteration"]
                    if "result" in results.keys() and results["result_group"].lower() not in [
                        "normal",
                        "no result",
                        "indeterminate",
                        "wild type",
                    ]:
                        status = results["result"].lower()
                        if status in caris_lo_keywords.keys():
                            # We only accept 2 of their results and they have to match our PHC keywords to be searchable
                            results["result"] = caris_lo_keywords[status]
                            copy_number_variant_tests.append(results)
                    elif (
                        "Exome CNA Panel - Additional Genes" in test_name
                        and "result" in results.keys()
                        and "copyNumber" in results.keys()
                    ):
                        status = results["result"].lower()

                        copy_number = 2.0
                        if results["copyNumber"]:
                            copy_number = float(results["copyNumber"])
                            cn_status = ""
                            # We only accept 2 of their results and they have to match our PHC keywords to be searchable
                            if copy_number >= 4 and copy_number < 6:
                                cn_status = "gain"
                            elif copy_number >= 6:
                                cn_status = "amplification"
                            elif copy_number < 1.3:
                                cn_status = "loss"
                            else:
                                continue
                            results["result"] = cn_status
                            copy_number_variant_tests.append(results)

    if not copy_number_variant_tests:
        return None

    # Save our results
    with open(f"{prefix}.copynumber.csv", "w") as f:
        f.write(
            "sample_id,gene,copy_number,status,attributes,chromosome,start_position,end_position,interpretation\n"
        )
        for alt in copy_number_variant_tests:
            if "genomicCoordinates" in alt.keys():
                chrom = alt["genomicCoordinates"].split(":")[1]
                coords = alt["genomicCoordinates"].split(":")[2].split("-")
            else:
                chrom, coords = gene_to_coords("GRCh37", alt["gene"])

            # Get pathogenic result
            if alt["result_group"].lower() in ["high", "mutated"]:
                interpretation = "Pathogenic"
            elif alt["result_group"].lower() in ["intermediate", "no result"]:
                interpretation = "Uncertain significance"
            else:
                interpretation = "other"

            f.write(
                ",".join(
                    [
                        prefix,
                        alt["gene"],
                        str(alt["copyNumber"]),
                        alt["result"],
                        "{}",
                        chrom,
                        coords[0],
                        coords[1],
                        f"{interpretation}\n",
                    ]
                ),
            )

    # Hard-code genome reference for Caris CNVs only
    genome_reference = "GRCh37"

    return {
        "fileName": f".lifeomic/caris/{prefix}/{prefix}.copynumber.csv",
        "sequenceType": "somatic",
        "type": "copyNumberVariant",
        "reference": genome_reference,
    }
