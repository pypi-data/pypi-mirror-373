from typing import Any

from qdrant_client import models

from mcp_server_qdrant.qdrant import ArbitraryFilter
from mcp_server_qdrant.settings import METADATA_PATH, FilterableField


def make_filter(
    filterable_fields: dict[str, FilterableField], values: dict[str, Any]
) -> ArbitraryFilter:
    must_conditions = []
    must_not_conditions = []
    should_conditions = []

    for raw_field_name, field_value in values.items():
        if raw_field_name not in filterable_fields:
            raise ValueError(f"Field {raw_field_name} is not a filterable field")

        field = filterable_fields[raw_field_name]

        if field_value is None:
            if field.required:
                raise ValueError(f"Field {raw_field_name} is required")
            else:
                continue

        field_name = f"{METADATA_PATH}.{raw_field_name}"

        if field.field_type == "keyword":
            if field.condition == "==":
                must_conditions.append(
                    models.FieldCondition(
                        key=field_name, match=models.MatchValue(value=field_value)
                    )
                )
            elif field.condition == "!=":
                must_not_conditions.append(
                    models.FieldCondition(
                        key=field_name, match=models.MatchValue(value=field_value)
                    )
                )
            elif field.condition == "any":
                must_conditions.append(
                    models.FieldCondition(
                        key=field_name, match=models.MatchAny(any=field_value)
                    )
                )
            elif field.condition == "except":
                must_conditions.append(
                    models.FieldCondition(
                        key=field_name,
                        match=models.MatchExcept(**{"except": field_value}),
                    )
                )
            elif field.condition is not None:
                raise ValueError(
                    f"Invalid condition {field.condition} for keyword field {field_name}"
                )

        elif field.field_type == "integer":
            if field.condition == "==":
                must_conditions.append(
                    models.FieldCondition(
                        key=field_name, match=models.MatchValue(value=field_value)
                    )
                )
            elif field.condition == "!=":
                must_not_conditions.append(
                    models.FieldCondition(
                        key=field_name, match=models.MatchValue(value=field_value)
                    )
                )
            elif field.condition == ">":
                must_conditions.append(
                    models.FieldCondition(
                        key=field_name, range=models.Range(gt=field_value)
                    )
                )
            elif field.condition == ">=":
                must_conditions.append(
                    models.FieldCondition(
                        key=field_name, range=models.Range(gte=field_value)
                    )
                )
            elif field.condition == "<":
                must_conditions.append(
                    models.FieldCondition(
                        key=field_name, range=models.Range(lt=field_value)
                    )
                )
            elif field.condition == "<=":
                must_conditions.append(
                    models.FieldCondition(
                        key=field_name, range=models.Range(lte=field_value)
                    )
                )
            elif field.condition == "any":
                must_conditions.append(
                    models.FieldCondition(
                        key=field_name, match=models.MatchAny(any=field_value)
                    )
                )
            elif field.condition == "except":
                must_conditions.append(
                    models.FieldCondition(
                        key=field_name,
                        match=models.MatchExcept(**{"except": field_value}),
                    )
                )
            elif field.condition is not None:
                raise ValueError(
                    f"Invalid condition {field.condition} for integer field {field_name}"
                )

        elif field.field_type == "float":
            # For float values, we only support range comparisons
            if field.condition == ">":
                must_conditions.append(
                    models.FieldCondition(
                        key=field_name, range=models.Range(gt=field_value)
                    )
                )
            elif field.condition == ">=":
                must_conditions.append(
                    models.FieldCondition(
                        key=field_name, range=models.Range(gte=field_value)
                    )
                )
            elif field.condition == "<":
                must_conditions.append(
                    models.FieldCondition(
                        key=field_name, range=models.Range(lt=field_value)
                    )
                )
            elif field.condition == "<=":
                must_conditions.append(
                    models.FieldCondition(
                        key=field_name, range=models.Range(lte=field_value)
                    )
                )
            elif field.condition is not None:
                raise ValueError(
                    f"Invalid condition {field.condition} for float field {field_name}. "
                    "Only range comparisons (>, >=, <, <=) are supported for float values."
                )

        elif field.field_type == "boolean":
            if field.condition == "==":
                must_conditions.append(
                    models.FieldCondition(
                        key=field_name, match=models.MatchValue(value=field_value)
                    )
                )
            elif field.condition == "!=":
                must_not_conditions.append(
                    models.FieldCondition(
                        key=field_name, match=models.MatchValue(value=field_value)
                    )
                )
            elif field.condition is not None:
                raise ValueError(
                    f"Invalid condition {field.condition} for boolean field {field_name}"
                )

        elif field.field_type == "text":
            # Text fields use full-text matching. We implement soft-preference semantics
            # for lists (OR behavior) by placing conditions into the Filter.should clause.
            # Single string values are treated the same way to avoid excluding entries
            # that lack the field (e.g., when metadata.themes is missing).
            def _to_match_text_conditions(val: Any) -> list[models.FieldCondition]:
                if isinstance(val, list):
                    return [
                        models.FieldCondition(
                            key=field_name, match=models.MatchText(text=str(v))
                        )
                        for v in val
                    ]
                else:
                    return [
                        models.FieldCondition(
                            key=field_name, match=models.MatchText(text=str(val))
                        )
                    ]

            if field.condition in ("any", "==", None):
                should_conditions.extend(_to_match_text_conditions(field_value))
            else:
                raise ValueError(
                    f"Invalid condition {field.condition} for text field {field_name}"
                )

        else:
            raise ValueError(
                f"Unsupported field type {field.field_type} for field {field_name}"
            )

    return models.Filter(
        must=must_conditions if must_conditions else None,
        should=should_conditions if should_conditions else None,
        must_not=must_not_conditions if must_not_conditions else None,
    ).model_dump()


def make_indexes(
    filterable_fields: dict[str, FilterableField],
) -> dict[str, models.PayloadSchemaType]:
    indexes = {}

    for field_name, field in filterable_fields.items():
        if field.field_type == "keyword":
            indexes[f"{METADATA_PATH}.{field_name}"] = models.PayloadSchemaType.KEYWORD
        elif field.field_type == "integer":
            indexes[f"{METADATA_PATH}.{field_name}"] = models.PayloadSchemaType.INTEGER
        elif field.field_type == "float":
            indexes[f"{METADATA_PATH}.{field_name}"] = models.PayloadSchemaType.FLOAT
        elif field.field_type == "boolean":
            indexes[f"{METADATA_PATH}.{field_name}"] = models.PayloadSchemaType.BOOL
        elif field.field_type == "text":
            indexes[f"{METADATA_PATH}.{field_name}"] = models.PayloadSchemaType.TEXT
        else:
            raise ValueError(
                f"Unsupported field type {field.field_type} for field {field_name}"
            )

    return indexes
