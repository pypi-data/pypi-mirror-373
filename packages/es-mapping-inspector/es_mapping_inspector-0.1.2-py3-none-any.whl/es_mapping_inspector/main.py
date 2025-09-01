# main.py
import logging

from elasticsearch import Elasticsearch
from pydantic import BaseModel

from .es_inspector import EsMappingInspector
from .pydantic_inspector import get_pydantic_model_fields

logging.basicConfig(
    level=logging.INFO,  # switch to DEBUG for deeper detail
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class MappingMismatchError(Exception):
    """
    Raised when differences are detected between a Pydantic model and an Elasticsearch mapping.

    Typically emitted by `compare_mapping_with_model` when missing fields, extra fields,
    or type mismatches are found.
    """

    pass


def compare_es_mapping_with_model(
    client: Elasticsearch, index: str, model: BaseModel, ignored_fields: list
):
    """
    Compare the Elasticsearch index mapping with the Pydantic model before sending data.

    Behavior
    --------
    - Logs a summary and prints a human-readable report.
    - Raises `MappingMismatchError` if missing fields, extra fields (excluding ignored),
      or type mismatches are detected.

    Raises
    ------
    MappingMismatchError
        If any differences are found between the Pydantic model and the ES mapping.
    """
    es_inspector = EsMappingInspector(client=client, index=index)
    es_fields = es_inspector.get_es_field_type_map()

    model_fields, errors = get_pydantic_model_fields(model=model)
    if errors:
        logger.error("Error extracting fields from Pydantic model: %s", errors)
        raise ValueError("Failed to parse Pydantic model fields.")

    missing_in_es = set(model_fields.keys()) - set(es_fields.keys())
    extra_in_es = set(es_fields.keys()) - set(model_fields.keys()) - set(ignored_fields)

    type_mismatches = {
        field: (model_fields[field], es_fields[field])
        for field in model_fields.keys() & es_fields.keys()
        if model_fields[field] != es_fields[field]
    }

    logger.info("🔍 Elasticsearch Mapping Comparison Report")

    if missing_in_es:
        logger.warning("🚨 Missing in Elasticsearch:")
        for field in missing_in_es:
            logger.warning("  - %s: %s", field, model_fields[field])

    if extra_in_es:
        logger.warning("⚠️ Extra in Elasticsearch (not in model):")
        for field in extra_in_es:
            logger.warning("  - %s: %s", field, es_fields[field])

    if type_mismatches:
        logger.warning("🔄 Type mismatches found:")
        for field, (expected, found) in type_mismatches.items():
            logger.warning("  - %s: Expected '%s', Found '%s'", field, expected, found)

    if not missing_in_es and not extra_in_es and not type_mismatches:
        logger.info("✅ No differences found between model and Elasticsearch mapping.")
    else:
        raise MappingMismatchError(
            "Pydantic model and Elasticsearch mapping differ. "
            f"Missing: {list(missing_in_es)}, "
            f"Extra: {list(extra_in_es)}, "
            f"Mismatched types: {list(type_mismatches.keys())}"
        )
