from amsdal_cli.commands.register_connection.utils.model_generator import ModelGenerator


async def fetch_tables(
    connection_name: str,
) -> list[str]:
    from amsdal_utils.config.manager import AmsdalConfigManager

    if AmsdalConfigManager().get_config().async_mode:
        schemas = await ModelGenerator.async_fetch_schemas(connection_name)
    else:
        schemas = ModelGenerator.fetch_schemas(connection_name)

    return [schema.name for schema in schemas]
