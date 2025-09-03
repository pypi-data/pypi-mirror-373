import logging

from amsdal_utils.schemas.schema import ObjectSchema

from amsdal_cli.commands.build.schemas.loaders.base import CustomCodeLoaderBase

logger = logging.getLogger(__name__)


class CustomCodeExtender:
    """
    Extends object schemas with custom code.

    This class is responsible for extending object schemas with custom code read from a custom code loader.
    """

    def __init__(self, custom_code_reader: CustomCodeLoaderBase):
        self._custom_code_reader = custom_code_reader
        self._custom_code_schemas = {schema.name: schema for schema in self._custom_code_reader.iter_custom_code()}
        self._used_custom_codes: set[str] = set()

    def extend(self, config: ObjectSchema) -> None:
        """
        Extends the given object schema with custom code if available.

        Args:
            config (ObjectSchema): The object schema to extend.

        Returns:
            None
        """
        custom_code_schema = self._custom_code_schemas.get(config.title, None)

        if not custom_code_schema:
            return

        config.custom_code = custom_code_schema.code
        self._used_custom_codes.add(custom_code_schema.name)

    def post_extend(self) -> None:
        """
        Logs any unused custom codes.
        """
        unused_custom_codes = self._custom_code_schemas.keys() - self._used_custom_codes

        if unused_custom_codes:
            logger.warning(
                'Unused custom codes: %s for %s',
                ', '.join(unused_custom_codes),
                self._custom_code_reader,
            )
