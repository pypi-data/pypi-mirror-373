from logging import Logger


def calculate_interpretation(result: str, log: Logger) -> str:
    if result == "pathogenic fusion":
        return "Pathogenic"
    elif result in ["likely pathogenic fusion", "likely pathogenic isoform"]:
        return "Likely pathogenic"
    elif result in ["fusion of uncertain significance"]:
        return "Uncertain significance"
    elif result in ["positive", "fusion detected", "unclassifiedvd"]:
        return "other"

    else:
        log.error(f"Failed to resolve interpretation: {result}")
        return ""
