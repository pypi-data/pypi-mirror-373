import logging

from amsdal_models.errors import AmsdalValidationError
from amsdal_utils.schemas.schema import ObjectSchema

from amsdal_cli.commands.build.schemas.loaders.base import OptionsLoaderBase

logger = logging.getLogger(__name__)


class OptionsExtender:
    """
    Extends object schemas with options.

    This class is responsible for extending object schemas with options read from an options loader.
    """

    def __init__(self, options_reader: OptionsLoaderBase):
        self._options_reader = options_reader
        self._options = {schema.title: schema for schema in self._options_reader.iter_options()}
        self._used_options: set[str] = set()

    def extend(self, config: ObjectSchema) -> None:
        """
        Extends the given object schema with options if available.

        Args:
            config (ObjectSchema): The object schema to extend.

        Returns:
            None
        """
        if not config.properties:
            return

        for _property_name, property_value in config.properties.items():
            options_list_name = getattr(property_value, 'options_list_name', None)

            if not options_list_name:
                continue

            if options_list_name not in self._options:
                msg = (
                    f'Options list name={options_list_name} is unknown. Make sure to create corresponding options '
                    'list under models/options folder'
                )
                raise AmsdalValidationError(msg)

            property_value.options = self._options[options_list_name].values
            self._used_options.add(options_list_name)

    def post_extend(self) -> None:
        """
        Logs any unused options lists.

        Returns:
            None
        """
        unused_options = set(self._options.keys()) - self._used_options

        if unused_options:
            msg = f'Unused options lists: {unused_options} for {self._options_reader}'
            logger.warning(msg)
