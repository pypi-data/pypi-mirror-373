from logging import Logger
import re


def parse_pattern(pattern: str, line: str, name: str) -> str:
    regex = re.compile(pattern)
    match = regex.match(line)

    if not match:
        raise ValueError(f"Could not parse {name} from line")

    return match.group(1).strip()


def parse_indication(line: str) -> str:
    return parse_pattern(r"^.*Reason for Referral:(.*?)(Patient|<).*$", line, "indication")


def parse_ordering_md(line: str) -> str:
    return parse_pattern(r"^.*Physician Name:(.*?)(Reason|<).*$", line, "ordering MD")


def parse_patient_name(line: str) -> str:
    return parse_pattern(r"^.*Patient Name: (.*?)(Accession|<).*$", line, "patient name")


def parse_sample_number(line: str) -> str:
    return parse_pattern(r"^.*Specimen #: (\d*-?R?) .*$", line, "sample number")


def parse_body_site(line: str) -> str:
    return parse_pattern(r"^.*Specimen:(.*?)(Age|Birthdate|<).*$", line, "body site")


def parse_report_id(line: str) -> str:
    return parse_pattern(r"^.*Accession #: (.*?) .*$", line, "report ID")


def parse_report_date_single_line(line: str) -> str:
    return parse_pattern(
        r"^.*Diagnostic Genomics Laboratory.*(\d{2}\/\d{2}\/\d{4}).*$", line, "report date"
    )


def parse_report_date_multiline(patient_info_lines: list[str]) -> str:
    in_range_trigger = False

    for line in patient_info_lines:
        if "Laboratory" in line:
            in_range_trigger = True
            continue
        if in_range_trigger:
            formatted_line = re.sub(r"<\/?T.\/?>", "", line).strip()
            if not formatted_line:
                continue
            return parse_pattern(
                r"^.*(\d{2}\/\d{2}\/\d{4}).*$", formatted_line, "report date from multiline"
            )

    raise ValueError("Could not parse report date from lines")


def parse_report_date(patient_info_lines: list[str], log: Logger) -> str:
    """
    Typically, the report date is in a form like:
    ```
    Diagnostic Genomics Laboratory 01/01/2021
    ```

    However, sometimes the date is split across multiple lines, like:
    ```
    Diagnostic Genomics Laboratory
    ...random empty lines or lines with only tags...
    01/01/2021
    ```
    This function attempts to first parse the date from a single line, and if that fails,
    it will attempt to parse it from multiple lines.
    """
    for line in patient_info_lines:
        if "Laboratory" in line:
            try:
                report_date = parse_report_date_single_line(line)
                return report_date
            except ValueError:
                log.warning("Could not parse report date from single line")
                break

    return parse_report_date_multiline(patient_info_lines)
