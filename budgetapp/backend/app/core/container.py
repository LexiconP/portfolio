"""Dependency container for wiring the app."""

from __future__ import annotations

from contextlib import asynccontextmanager
from functools import cached_property

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import AppConfig
from .database import Database
from ..api.routes import build_router
from ..repositories.budgets import BudgetRepository
from ..repositories.receipts import ReceiptRepository
from ..services.budgets import BudgetService
from ..services.ocr import OcrService, ReceiptParser
from ..services.receipts import ReceiptService


class Container:
    """Simple DI container to assemble services and repositories."""
    def __init__(self, config: AppConfig | None = None) -> None:
        self._config = config or AppConfig.from_environment()

    @property
    def config(self) -> AppConfig:
        return self._config

    @cached_property
    def db(self) -> Database:
        return Database(self.config.db_path)

    @cached_property
    def receipt_repository(self) -> ReceiptRepository:
        return ReceiptRepository(self.db)

    @cached_property
    def budget_repository(self) -> BudgetRepository:
        return BudgetRepository(self.db)

    @cached_property
    def ocr_service(self) -> OcrService:
        return OcrService()

    @cached_property
    def receipt_parser(self) -> ReceiptParser:
        return ReceiptParser()

    @cached_property
    def receipt_service(self) -> ReceiptService:
        return ReceiptService(
            repository=self.receipt_repository,
            config=self.config,
            ocr_service=self.ocr_service,
            parser=self.receipt_parser,
        )

    @cached_property
    def budget_service(self) -> BudgetService:
        return BudgetService(repository=self.budget_repository)

    def create_app(self) -> FastAPI:
        # Build the FastAPI application and register middleware/routes.
        @asynccontextmanager
        async def lifespan(_: FastAPI):
            # Ensure directories and schema are ready before requests.
            self.config.ensure_directories()
            self.db.init()
            yield

        app = FastAPI(
            title="Receipt OCR Budget Reconciliation API",
            lifespan=lifespan,
        )

        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        app.include_router(
            build_router(self.config, self.receipt_service, self.budget_service)
        )
        app.mount("/static", StaticFiles(directory=self.config.static_dir), name="static")

        return app
