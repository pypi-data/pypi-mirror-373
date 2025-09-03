from pathlib import Path


async def init_amsdal(config_path: Path, temp_dir: Path) -> None:
    from amsdal.configs.main import settings
    from amsdal.manager import AmsdalManager
    from amsdal_utils.config.manager import AmsdalConfigManager

    settings.override(
        APP_PATH=temp_dir,
        USER_MODELS_MODULE_PATH=temp_dir / 'models',
    )

    if not settings.USER_MODELS_MODULE_PATH:
        msg = 'USER_MODELS_MODULE_PATH must be set in settings.'
        raise ValueError(msg)

    settings.USER_MODELS_MODULE_PATH.mkdir(parents=True, exist_ok=True)
    (settings.USER_MODELS_MODULE_PATH / '__init__.py').touch(exist_ok=True)

    config_manager = AmsdalConfigManager()
    config_manager.load_config(config_path)

    config = config_manager.get_config()

    if config.async_mode:
        await _async_init()
    else:
        amsdal_manager = AmsdalManager()
        amsdal_manager.setup()
        amsdal_manager.authenticate()
        amsdal_manager.post_setup()  # type: ignore[call-arg]


async def _async_init() -> None:
    from amsdal.manager import AsyncAmsdalManager

    amsdal_manager = AsyncAmsdalManager()
    await amsdal_manager.setup()
    amsdal_manager.authenticate()
    await amsdal_manager.post_setup()  # type: ignore[call-arg, misc]
