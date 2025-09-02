"""
File storage related dependency injection.

This module provides FastAPI dependency injection functions
for file storage services and template synchronization.
"""

import os

from dependency_injector.wiring import Provide, inject
from fastapi import Depends

from ingenious.config.main_settings import IngeniousSettings
from ingenious.files.files_repository import FileStorage
from ingenious.services.container import Container


@inject
def get_config(
    config: IngeniousSettings = Provide[Container.config],
) -> IngeniousSettings:
    """Get config from container."""
    return config


@inject
def get_file_storage_data(
    file_storage: FileStorage = Provide[Container.file_storage_data],
) -> FileStorage:
    """Get file storage for data from container."""
    return file_storage


@inject
def get_file_storage_revisions(
    file_storage: FileStorage = Provide[Container.file_storage_revisions],
) -> FileStorage:
    """Get file storage for revisions from container."""
    return file_storage


def sync_templates(config: IngeniousSettings = Depends(get_config)) -> None:
    """Sync templates from file storage."""
    if config.file_storage.revisions.storage_type == "local":
        return
    else:
        fs = FileStorage(config)
        working_dir = os.getcwd()
        template_path = os.path.join(working_dir, "ingenious", "templates")
        import asyncio

        async def sync_files() -> None:
            template_files = await fs.list_files(file_path=template_path)
            for file in template_files:
                file_name = os.path.basename(file)
                file_contents = await fs.read_file(
                    file_name=file_name, file_path=template_path
                )
                file_path = os.path.join(
                    working_dir, "ingenious", "templates", file_name
                )
                with open(file_path, "w") as f:
                    f.write(file_contents)

        asyncio.run(sync_files())
