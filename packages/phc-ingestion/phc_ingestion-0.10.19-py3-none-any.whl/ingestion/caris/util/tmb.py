from typing import TypedDict


class TumorMutationBurden(TypedDict):
    """A partial representation of the Tumor Mutation Burden in the Caris JSON file"""

    mutationBurdenCall: str
    mutationBurdenScore: float | str
    mutationBurdenUnit: str


class ParsedTumorMutationBurden(TypedDict):
    tmb: str
    tmbScore: float


def parse_tumor_mutation_burden(tmb_dict: TumorMutationBurden) -> ParsedTumorMutationBurden | None:
    tmb = tmb_dict["mutationBurdenCall"].lower()
    tmb_score = tmb_dict["mutationBurdenScore"]

    if not tmb_score or tmb_score == "Unknown":
        return None

    tmb_unit = tmb_dict["mutationBurdenUnit"]

    # Convert from their format, which is "21 per Mb"
    if tmb_unit == "Mutations/Megabase" and isinstance(tmb_score, str):
        if ">150" in tmb_score:
            tmb_score = 151.0
        else:
            tmb_score = float(tmb_score.split(" per")[0])
    elif isinstance(tmb_score, str):
        tmb_score = float(tmb_score)

    return {"tmb": tmb, "tmbScore": tmb_score}
