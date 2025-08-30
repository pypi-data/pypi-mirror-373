import pandas as pd
from logging import Logger

from ingestion.caris.util.tests import safely_extract_tests_from_json_data
from ingestion.caris.util.interpretation import calculate_interpretation
from ingestion.caris.util.detect_genome_ref import detect_caris_gr


def extract_structural(prefix, data, log: Logger):
    log.info("Extracting fusion variants from json")
    extracted_tests = safely_extract_tests_from_json_data(data)
    structural_variant_tests = []
    for test in extracted_tests:
        if (
            test["platformTechnology"] in ["Transcriptome", "Hybrid Transcriptome"]
            and "testResults" in test.keys()
        ):
            for test_result in test["testResults"]:
                this_result = test_result["translocation"]

                # Result_group values:
                #     - Mutated
                #     - Normal
                #     - No Result
                #
                # We only keep Mutated. Possible results:
                #     - Fusion Detected
                #     - Likely Pathogenic Fusion
                #     - Likely Pathogenic Isoform
                #     - Pathogenic Fusion
                if this_result["result_group"].lower() not in [
                    "normal",
                    "no result",
                    "indeterminate",
                    "wild type",
                    "hlavd",
                ]:
                    structural_variant_tests.append(this_result)
    if not structural_variant_tests:
        return None

    df = pd.DataFrame(structural_variant_tests)

    def split_coords(x):
        return x.strip(":+").replace("+/", "").strip(":-").replace("-/", "")

    df["genomicBreakpoint"] = df["genomicBreakpoint"].apply(split_coords)

    df[["chromosome1", "start_position1", "chromosome2", "start_position2"]] = df[
        "genomicBreakpoint"
    ].str.split(":", expand=True)

    # Structural Variant CSV fields found in documentation here:
    # https://docs.us.lifeomic.com/user-guides/omics/data-processing/#structural-variants
    df["sample_id"] = prefix  # required str
    # df['gene1']                                 #already exists from JSON
    # df['gene2']                                 #already exists from JSON
    df["effect"] = (
        "Fusion"  # "Fusion" if "Fusion" in df['result'] else ""                   #optional str
    )
    # df['chromosome1']     = ""#firstBreak[0]#""                   #optional str
    # df['start_position1'] = ""#firstBreak[1]#""                   #optional str
    df["end_position1"] = df["start_position1"]  # optional str
    # df['chromosome2']     = ""                   #optional str
    # df['start_position2'] = ""                   #optional str
    df["end_position2"] = df["start_position2"]  # optional str
    # df['interpretation']                        #already exists from JSON
    df["sequence_type"] = df["genomicSource"]  # optional str

    # Fusions are no longer described in depth from what I can see in the new json files...
    df["in_frame"] = "Unknown"
    # To explain below: https://stackoverflow.com/a/11531402/14708230
    df.loc[df["interpretation"].str.contains("in-frame"), "in_frame"] = "Yes"

    # Utilize "result" as the interpretation, mapped to approved values
    # (if result_group is 'unclassifiedVD' we use that, because a result will not be present)
    mapped_interpretation_list = []
    for entry in zip(list(df.result_group), list(df.result)):
        if entry[0].lower() == "unclassifiedvd":
            mapped_interpretation_list.append("Uncertain significance")
        else:
            mapped_interpretation_list.append(calculate_interpretation(entry[1].lower(), log))

    df["interpretation"] = mapped_interpretation_list

    df["attributes"] = "{}"  # optional str containing JSON

    # Select columns for output
    df_out = df[
        [
            "sample_id",
            "gene1",
            "gene2",
            "effect",
            "chromosome1",
            "start_position1",
            "end_position1",
            "chromosome2",
            "start_position2",
            "end_position2",
            "interpretation",
            "sequence_type",
            "in_frame",
            "attributes",
        ]
    ]

    df_out.to_csv(f"{prefix}.structural.csv", na_rep="N/A", index=False)

    genome_reference = detect_caris_gr(structural_variant_tests, "structural", log)
    return {
        "fileName": f".lifeomic/caris/{prefix}/{prefix}.structural.csv",
        "sequenceType": "somatic",
        "type": "structuralVariant",
        "reference": genome_reference,
    }
