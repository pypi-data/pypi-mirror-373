from ruamel.yaml import YAML

TAG_STR = "tag:yaml.org,2002:str"


def create_yaml(manifest, prefix):

    yaml = YAML()
    with open(f"{prefix}.ga4gh.genomics.yml", "w") as file:
        yaml.dump(manifest, file)


# Numbers with leading zeros can result in problems later, ensure all numbers with leading zeros are quoted
def str_representer(dumper, value):
    if value.startswith("0"):
        return dumper.represent_scalar(TAG_STR, value, style="'")
    return dumper.represent_scalar(TAG_STR, value)
