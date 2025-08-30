from logging import Logger


def calculate_interpretation(status: str, log: Logger) -> str:
    if status == "known":
        return "Pathogenic"
    if status == "likely":
        return "Likely pathogenic"
    if status == "unknown":
        return "Uncertain significance"
    if status == "ambiguous":
        return "other"

    log.error(f"Failed to resolve interpretation: {status}")
    return ""
