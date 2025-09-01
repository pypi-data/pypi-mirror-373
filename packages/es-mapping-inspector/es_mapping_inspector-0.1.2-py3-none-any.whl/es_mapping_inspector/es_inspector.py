# es_inspector.py
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from functools import cached_property

from elasticsearch import Elasticsearch

logger = logging.getLogger(__name__)


@dataclass
class EsMappingInspector:
    client: Elasticsearch
    index: str

    def _fetch_full_es_mapping(self) -> dict:
        logger.debug("Fetching full mapping for index '%s'.", self.index)
        mapping = self.client.indices.get_mapping(index=self.index)
        props = mapping[self.index]["mappings"].get("properties", {})
        logger.debug("Fetched mapping with %d top-level properties.", len(props))
        return props

    def _flatten_es_mapping_types(self, mapping: dict, prefix="") -> dict[str, str]:
        """
        Recursively flatten an Elasticsearch mapping to `dot.path -> type` entries.

        Parameters
        ----------
        mapping : dict
            An ES mapping (or sub-mapping). If it contains a top-level "properties",
            it will be used as the starting point.
        prefix : str, optional
            An optional path prefix for nested recursion.

        Returns
        -------
        dict[str, str]
            A dictionary from field path (dot notation) to ES type string.
            For objects without explicit `"type"`, `"dict"` is used as a marker.

        Notes
        -----
        - `"nested"` and `"object"` fields are traversed and included in the result.
        - Fields with `"keyword"` are recorded explicitly as `"keyword"`.
        """
        fields = {}

        if "properties" in mapping:
            mapping = mapping["properties"]

        for name, field in mapping.items():
            full_name = f"{prefix}.{name}" if prefix else name

            if "type" in field:
                if field["type"] in {"nested", "object"} and "properties" in field:
                    fields[full_name] = field["type"]
                    fields.update(self._flatten_es_mapping_types(field, full_name))
                else:
                    if field["type"] == "keyword":
                        fields[full_name] = "keyword"
                    else:
                        fields[full_name] = field["type"]
            elif "properties" in field:  # Ensure objects without explicit "type" are handled
                fields[full_name] = dict
                fields.update(self._flatten_es_mapping_types(field, full_name))
            else:
                fields[full_name] = field["type"]

        return fields

    def _normalize_es_types(self, es_fields):
        """
        Convert Elasticsearch type strings to Python types or canonical markers.

        Parameters
        ----------
        es_fields : dict[str, str]
            A flattened mapping of field path to ES type string (e.g., "keyword", "integer").

        Returns
        -------
        dict[str, type | str]
            A mapping of field path to either a Python type (e.g., `int`, `str`) or a marker
            (`list`, `dict`, or the original string if no mapping is known).

        Notes
        -----
        - ES `"nested"` is treated conceptually as a `list` of objects.
        - Unknown ES types are preserved as-is to avoid masking mismatches.
        """

        es_to_py = {
            "text": str,
            "keyword": str,
            "wildcard": str,
            "constant_keyword": str,
            "byte": int,
            "short": int,
            "integer": int,
            "long": int,
            "unsigned_long": int,
            "half_float": float,
            "float": float,
            "double": float,
            "scaled_float": float,
            "boolean": bool,
            "date": datetime,
            "date_nanos": datetime,
            "object": dict,
            "nested": list,
            "flattened": dict,
            "ip": str,
            "version": str,
            "geo_point": "geo_point",
            "geo_shape": "geo_shape",
            "completion": "completion",
            "rank_feature": "rank_feature",
        }

        normalized = {
            es_key: es_to_py.get(es_type, es_type) for es_key, es_type in es_fields.items()
        }

        logger.debug("Normalized %d ES fields.", len(normalized))
        return normalized

    def get_es_field_type_map(self) -> dict:
        mapping = self._fetch_full_es_mapping()
        flat = self._flatten_es_mapping_types(mapping)
        return self._normalize_es_types(flat)

    @cached_property
    def field_type_map(self) -> dict:
        """Public, cached view."""
        return self.get_es_field_type_map()
