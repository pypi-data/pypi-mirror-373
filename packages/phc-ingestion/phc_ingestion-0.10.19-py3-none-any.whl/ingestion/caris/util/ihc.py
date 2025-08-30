import numpy as np
import re


def get_ihc_results(data, log) -> list[dict]:
    # Initialize trigger for logging, and a results list
    trigger = False
    ihc_results: list[dict] = []

    try:
        ihc_tests = [test for test in data.get("tests") if test["testMethodology"] == "IHC"]
    except TypeError:
        log.info("No Immunohistochemistry tests reported")
        return ihc_results

    hidden_ic = re.compile(r"[IC]")

    for test in ihc_tests:
        test_results = test["testResults"]["expressionAlteration"]

        biomarkername = test_results.get("biomarkerName", "")
        result = test_results.get("result", "")
        result_group = test_results.get("result_group", "")

        if result_group == "No Result":
            continue

        # Grab a field prefix list to hunt for tc / ic fields
        prefix_list = [x[:2] for x in list(test_results)]
        # If ic / tc counts are off, log it and try to load in minimal test info for future troubleshooting
        if (prefix_list.count("tc") + prefix_list.count("ic")) not in [0, 3, 7]:
            log.warning(
                f'IHC test {test_results["biomarkerName"]} has an unexpected pattern: ic/tc field count is {prefix_list.count("tc")+prefix_list.count("ic")}. Should be 0, 3, or 7(PD-L1).'
            )
            trigger = True
            ihc_results.append({"biomarkerName": biomarkername, "result": result})

        # Check for PD-L1 tests, work through odd handling patterns
        elif test_results["biomarkerName"][:5] == "PD-L1":
            # Tumor cell / immune cell logic
            if prefix_list.count("ic") == 3:
                ic_result = test_results.get("icResult", "")
                ic_stainpercent = test_results.get("icStainPercent", np.nan)

                ic_threshold = (
                    test_results["icThreshold"].split("or")[0].strip()
                    if test_results.get("icThreshold")
                    else ""
                )

                if prefix_list.count("tc") == 4:
                    tc_result = test_results.get("tcResult", "")
                    tc_intensity = test_results.get("tcIntensity", "")
                    tc_stainpercent = test_results.get("tcStainPercent", np.nan)
                    tc_threshold = (
                        test_results["tcThreshold"].split("or")[-1].strip()
                        if test_results.get("tcThreshold")
                        else ""
                    )
                    ihc_results.append(
                        {
                            "biomarkerName": biomarkername,
                            "result": result,
                            "tcResult": tc_result,
                            "tcIntensity": tc_intensity,
                            "tcStainPercent": float(tc_stainpercent),
                            "tcThreshold": tc_threshold,
                            "icResult": ic_result,
                            "icStainPercent": float(ic_stainpercent),
                            "icThreshold": ic_threshold,
                        }
                    )
                else:
                    ihc_results.append(
                        {
                            "biomarkerName": biomarkername,
                            "result": result,
                            "icResult": ic_result,
                            "icStainPercent": float(ic_stainpercent),
                            "icThreshold": ic_threshold,
                        }
                    )

            # PD-L1 (22c3) tests report a cpScore, and no stain or intensity metrics
            elif test_results["biomarkerName"][-6:] == "(22c3)":
                threshold = (
                    test_results["threshold"].split("or")[-1].strip()
                    if test_results.get("threshold")
                    else ""
                )

                tpScore = test_results.get("tpScore", np.nan)
                if np.isnan(float(tpScore)) == True:
                    cpScore = test_results.get("cpScore", np.nan)

                    ihc_results.append(
                        {
                            "biomarkerName": biomarkername,
                            "result": result,
                            "cpScore": float(cpScore),
                            "threshold": threshold,
                        }
                    )

                else:
                    ihc_results.append(
                        {
                            "biomarkerName": biomarkername,
                            "result": result,
                            "tpScore": float(tpScore),
                            "threshold": threshold,
                        }
                    )

                # Check if correct pattern is followed
                # stainPercent and intensity fields should be missing
                if test_results.get("intensity"):
                    if test_results["intensity"] != "":
                        log.warning(
                            f'IHC test {test_results["biomarkerName"]} has an unexpected pattern for "intensity": value of "{test_results["intensity"]}" was given when None was expected'
                        )
                        trigger = True
                if test_results.get("stainPercent"):
                    try:
                        stain_percent = float(test_results["stainPercent"])
                        if np.isnan(stain_percent) == False:
                            log.warning(
                                f'IHC test {test_results["biomarkerName"]} has an unexpected pattern for "stainPercent": value of "{test_results["stainPercent"]}" was given when None was expected'
                            )
                            trigger = True
                    except (ValueError, TypeError):
                        log.warning(
                            f'IHC test {test_results["biomarkerName"]} has an invalid value for "stainPercent": "{test_results["stainPercent"]}"'
                        )
                        trigger = True

            # Some PD-L1 tests don't have icThreshold field filled out,
            # but report IC Threshold in the regular Threshold field
            elif isinstance((re.search(hidden_ic, test_results["threshold"])), re.Match):
                stainpercent = test_results.get("stainPercent", np.nan)

                # IC grabs threshold from the front
                threshold = (
                    test_results["threshold"].split("or")[0].strip()
                    if test_results.get("threshold")
                    else ""
                )

                ihc_results.append(
                    {
                        "biomarkerName": biomarkername,
                        "result": result,
                        "stainPercent": float(stainpercent),
                        "threshold": threshold,
                    }
                )

                # Check if correct pattern is followed
                # Intensity field should be missing
                if test_results.get("intensity"):
                    if test_results["intensity"] != "":
                        log.warning(
                            f'IHC test {test_results["biomarkerName"]} has an unexpected pattern for "intensity": value of "{test_results["intensity"]}" was given when None was expected'
                        )
                        trigger = True

            # If no PD-L1 oddities are found, then report PD-L1 as a standard test
            else:
                intensity = test_results.get("intensity", "")
                stainpercent = test_results.get("stainPercent", np.nan)
                threshold = (
                    test_results["threshold"].split("or")[-1].strip()
                    if test_results.get("threshold")
                    else ""
                )

                ihc_results.append(
                    {
                        "biomarkerName": biomarkername,
                        "result": result,
                        "intensity": intensity,
                        "stainPercent": float(stainpercent),
                        "threshold": threshold,
                    }
                )

        # A growing list of tests only report biomarker and result
        elif test_results["biomarkerName"] in [
            "Mismatch Repair Status",
            "Folfox Responder Similarity",
            "ER/PR/Her2/Neu",
        ]:
            ihc_results.append({"biomarkerName": biomarkername, "result": result})
            # Check if correct pattern is followed
            # stainPercent, intensity and threshold fields should be missing
            if test_results.get("intensity"):
                if test_results["intensity"] != "":
                    log.warning(
                        f'IHC test {test_results["biomarkerName"]} has an unexpected pattern for "intensity": value of "{test_results["intensity"]}" was given when None was expected'
                    )
                    trigger = True
            if test_results.get("stainPercent"):
                try:
                    stain_percent = float(test_results["stainPercent"])
                    if not np.isnan(stain_percent):
                        log.warning(
                            f'IHC test {test_results["biomarkerName"]} has an unexpected pattern for "stainPercent": value of "{test_results["stainPercent"]}" was given when None was expected'
                        )
                        trigger = True
                except (ValueError, TypeError):
                    log.warning(
                        f'IHC test {test_results["biomarkerName"]} has an invalid value for "stainPercent": "{test_results["stainPercent"]}"'
                    )
                    trigger = True
            if test_results.get("threshold"):
                if test_results["threshold"] != "":
                    log.warning(
                        f'IHC test {test_results["biomarkerName"]} has an unexpected pattern for "threshold": value of "{test_results["threshold"]}" was given when None was expected'
                    )
                    trigger = True

        # Caris has a list of other tests which report result, and stainPercent
        # [MLH1, MSH2, MSH6, PMS2]
        elif test_results["biomarkerName"] in ["MLH1", "MSH2", "MSH6", "PMS2"]:
            stainpercent = test_results.get("stainPercent", np.nan)

            ihc_results.append(
                {
                    "biomarkerName": biomarkername,
                    "result": result,
                    "stainPercent": float(stainpercent),
                }
            )

            # Check if correct pattern is followed
            # Intensity and threshold fields should be missing
            if test_results.get("intensity"):
                if test_results["intensity"] != "":
                    log.warning(
                        f'IHC test {test_results["biomarkerName"]} has an unexpected pattern for "intensity": value of "{test_results["intensity"]}" was given when None was expected'
                    )
                    trigger = True

            if test_results.get("threshold"):
                if test_results["threshold"] != "":
                    log.warning(
                        f'IHC test {test_results["biomarkerName"]} has an unexpected pattern for "threshold": value of "{test_results["threshold"]}" was given when None was expected'
                    )
                    trigger = True

        # Standard test reporting
        else:
            intensity = test_results.get("intensity", "")
            stainpercent = test_results.get("stainPercent", np.nan)
            threshold = (
                test_results["threshold"].split("or")[-1].strip()
                if test_results.get("threshold")
                else ""
            )

            ihc_results.append(
                {
                    "biomarkerName": biomarkername,
                    "result": result,
                    "intensity": intensity,
                    "stainPercent": float(stainpercent),
                    "threshold": threshold,
                }
            )

    log.info(f"Immunohistochemistry tests detected: {len(ihc_results)}")

    # Missing field pattern checking
    for test in ihc_results:
        for k, v in test.items():
            # Log if any expected fields are left blank
            if k == "cpScore" or k == "tpScore" or k == "stainPercent":
                if np.isnan(v):
                    log.warning(
                        f'IHC test {test["biomarkerName"]} has an unexpected pattern for field: {k}'
                    )
                    trigger = True

            else:
                if v == "":
                    log.warning(
                        f'IHC test {test["biomarkerName"]} has an unexpected pattern for field: {k}'
                    )
                    trigger = True

    if trigger == False:
        log.info("All IHC tests matched the expected patterns.")

    return ihc_results
