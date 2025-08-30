def safely_extract_tests_from_json_data(data: dict) -> list[dict]:
    tests = data["tests"]

    # It seems like Caris generates the JSON file from XML.
    # Because of this, sometimes a `tests` with one test gets converted to a dict.
    # We need it as a list so we can safely iterate over it.
    if isinstance(tests, dict):
        tests = [tests]

    return tests
