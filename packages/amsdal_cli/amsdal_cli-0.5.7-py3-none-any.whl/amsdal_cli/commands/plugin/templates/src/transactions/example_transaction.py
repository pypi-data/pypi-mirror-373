{% if ctx.is_async_mode %}from amsdal_data.transactions.decorators import async_transaction


@async_transaction(name='ExampleTransaction')
async def example_transaction(name: str, description: str = "") -> None:
    """
    Example transaction for {{ ctx.plugin_name }} plugin.
    
    Args:
        name: Name for the example model
        description: Description for the example model
    """
    # TODO: Add your transaction logic here
    # Example:
    # from models.example_model import ExampleModel
    # 
    # new_model = ExampleModel(
    #     name=name,
    #     description=description,
    #     is_active=True
    # )
    # await new_model.async_save()
    pass
{% else %}from amsdal_data.transactions.decorators import transaction


@transaction(name='ExampleTransaction')
def example_transaction(name: str, description: str = "") -> None:
    """
    Example transaction for {{ ctx.plugin_name }} plugin.
    
    Args:
        name: Name for the example model
        description: Description for the example model
    """
    # TODO: Add your transaction logic here
    # Example:
    # from models.example_model import ExampleModel
    # 
    # new_model = ExampleModel(
    #     name=name,
    #     description=description,
    #     is_active=True
    # )
    # new_model.save()
    pass
{% endif %}
