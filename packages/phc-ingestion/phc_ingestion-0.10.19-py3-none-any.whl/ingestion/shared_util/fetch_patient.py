from typing import Any
from lifeomic_logging import scoped_logger
from ingestion.shared_util.lambda_client import LambdaClient

# Constants
DATASET_SYSTEM = "http://lifeomic.com/fhir/dataset"


def fetch_patient(
    *,
    elation_id: str,
    given_name: str,
    birthdate: str,
    project_id: str,
    account_id: str,
    ingestion_id: str,
) -> dict[str, Any] | None:
    """
    Fetch a patient from the patient-service lambda using Elation ID AND given name AND
    birthdate.

    Returns:
        The patient resource if found, None otherwise

    Raises:
        RuntimeError: When multiple patients are found (ambiguous match)
    """
    log_context = {
        "accountId": account_id,
        "projectId": project_id,
        "elationId": elation_id,
        "ingestionId": ingestion_id,
    }

    with scoped_logger(__name__, log_context) as log:
        # Create LambdaClient instance with proper headers
        client = LambdaClient(
            "patient-service",
            {
                "Content-Type": "application/json",
                "LifeOmic-Account": account_id,
                "LifeOmic-Correlation-Id": ingestion_id,
            },
        )

        # Search by Elation ID AND given name AND birthdate
        log.info(
            f"Searching for patient with Elation ID: {elation_id}, given name: {given_name}, birthdate: {birthdate}"
        )
        response = client.invoke(
            f"/{account_id}/dstu3/Patient",
            "get",
            None,
            {
                "_tag": f"{DATASET_SYSTEM}|{project_id}",
                "identifier": elation_id,
                "name": given_name,
                "birthdate": birthdate,
            },
        )
        entries = response.get("entry", [])

        if len(entries) == 0:
            error_msg = f"No patient found with Elation ID: {elation_id}, given name: {given_name}, birthdate: {birthdate}"
            log.error(error_msg)
            raise RuntimeError(error_msg)

        if len(entries) > 1:
            error_msg = f"Found multiple patients when one was expected. Found {len(entries)}. Elation ID {elation_id}, given name {given_name}, birthdate {birthdate}."
            log.error(error_msg)
            raise RuntimeError(error_msg)

        log.info(
            f"Found patient with Elation ID: {elation_id}, given name: {given_name}, birthdate: {birthdate}"
        )
        return entries[0]["resource"]
