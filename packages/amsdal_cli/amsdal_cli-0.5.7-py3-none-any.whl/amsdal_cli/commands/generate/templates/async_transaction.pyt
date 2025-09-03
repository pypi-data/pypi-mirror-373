from amsdal_data.transactions.decorators import async_transaction


@async_transaction
async def {{ ctx.transaction_class_name }}():
    # TODO: implementation here
    ...
