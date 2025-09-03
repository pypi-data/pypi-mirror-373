import json
from collections.abc import Iterable
from typing import Any

from amsdal_models.errors import AmsdalValidationError
from amsdal_utils.schemas.schema import ObjectSchema

from amsdal_cli.commands.build.schemas.utils.merger import merge_schema


class EnrichSchemasMixin:
    """
    Mixin class to enrich schemas with additional configurations.

    This class provides methods to enrich type, core, contrib, and user schemas by merging them with additional
    configurations. It ensures that schemas are enriched in the correct order and raises an `AmsdalValidationError`
    if any parent schemas are missing.
    """

    def enrich_configs(
        self,
        type_schemas: list[ObjectSchema],
        core_schemas: list[ObjectSchema],
        contrib_schemas: list[ObjectSchema],
        user_schemas: list[ObjectSchema],
    ) -> tuple[list[ObjectSchema], list[ObjectSchema], list[ObjectSchema], list[ObjectSchema]]:
        """
        Enriches the provided schemas with additional configurations.

        This method enriches type, core, contrib, and user schemas by merging them with additional configurations.
        It ensures that schemas are enriched in the correct order and raises an `AmsdalValidationError` if any parent
        schemas are missing.

        Args:
            type_schemas (list[ObjectSchema]): A list of type schemas to enrich.
            core_schemas (list[ObjectSchema]): A list of core schemas to enrich.
            contrib_schemas (list[ObjectSchema]): A list of contrib schemas to enrich.
            user_schemas (list[ObjectSchema]): A list of user schemas to enrich.

        Returns:
            tuple[list[ObjectSchema], list[ObjectSchema], list[ObjectSchema], list[ObjectSchema]]:
            A tuple containing the enriched type, core, contrib, and user schemas.

        Raises:
            AmsdalValidationError: If any parent schemas are missing.
        """
        _core_schemas = self._enrich(type_schemas, core_schemas)
        _contrib_schemas = self._enrich(type_schemas, contrib_schemas, extra_schemas=_core_schemas)
        _user_schemas = self._enrich(
            type_schemas,
            user_schemas,
            extra_schemas=[
                *_core_schemas,
                *_contrib_schemas,
            ],
        )

        return (
            type_schemas,
            _core_schemas,
            _contrib_schemas,
            _user_schemas,
        )

    def _enrich(
        self,
        type_schemas: list[ObjectSchema],
        schemas: list[ObjectSchema],
        extra_schemas: Iterable[ObjectSchema] | None = None,
    ) -> list[ObjectSchema]:
        # we want to save original order
        indexed_schemas: list[tuple[int, ObjectSchema]] = list(enumerate(schemas))
        enriched_schemas: list[tuple[int, ObjectSchema]] = []
        skipped_schemas: list[tuple[int, ObjectSchema]] = []

        core_schemas_map: dict[str, ObjectSchema] = {_type.title.lower(): _type for _type in type_schemas}
        parent_schemas: dict[str, ObjectSchema] = {}

        if extra_schemas:
            parent_schemas.update({_type.title.lower(): _type for _type in extra_schemas})

        while True:
            try:
                i, current_schema = indexed_schemas.pop()
            except IndexError:
                break

            if current_schema.type.lower() in core_schemas_map:
                parent_schemas[current_schema.title.lower()] = current_schema
                enriched_schemas.append((i, current_schema))
                indexed_schemas = indexed_schemas + skipped_schemas
                skipped_schemas = []
            elif current_schema.type.lower() in parent_schemas:
                enriched_schema_json = merge_schema(
                    self._decode_json(parent_schemas[current_schema.type.lower()].model_dump_json()),
                    self._decode_json(current_schema.model_dump_json()),
                )
                enriched_schema = ObjectSchema.model_validate(enriched_schema_json)
                parent_schemas[enriched_schema.title.lower()] = enriched_schema
                enriched_schemas.append((i, enriched_schema))
                indexed_schemas = indexed_schemas + skipped_schemas
                skipped_schemas = []
            else:
                skipped_schemas.append((i, current_schema))

        if skipped_schemas:
            exc_msg = 'Cannot find parent schemas for some schemas: {}'.format(
                ', '.join(sorted(schema.title for _, schema in skipped_schemas)),
            )
            raise AmsdalValidationError(exc_msg)

        return [enriched_schema for _, enriched_schema in enriched_schemas]

    @staticmethod
    def _decode_json(json_string: str) -> dict[str, Any]:
        data: dict[str, Any] = json.loads(json_string)

        return data
