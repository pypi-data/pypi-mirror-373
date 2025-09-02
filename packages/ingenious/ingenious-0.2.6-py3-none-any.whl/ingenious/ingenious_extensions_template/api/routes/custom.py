from fastapi import APIRouter, FastAPI

from ingenious.models.api_routes import IApiRoutes


class Api_Routes(IApiRoutes):
    def add_custom_routes(self) -> FastAPI:
        router = APIRouter()

        @router.post("/chat_custom_sample")
        def chat_custom_sample():
            # logger = logging.getLogger(__name__)

            # config = get_config()
            # fs = files_repository.FileStorage(config=config, Category="revisions")
            # fs_data = files_repository.FileStorage(config=config, Category="data")

            # Todo implement the processing logic

            # Return acknowledgment immediately
            return {"status": "acknowledged"}

        self.app.include_router(router, prefix="/api/v1", tags=["chat_custom_sample"])
        return self.app.router
