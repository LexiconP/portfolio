from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    base_dir: Path
    data_dir: Path
    receipts_dir: Path
    db_path: Path
    static_dir: Path

    @classmethod
    def from_environment(cls) -> "AppConfig":
        base_dir = Path(__file__).resolve().parents[1]
        data_dir = base_dir / "data"
        receipts_dir = data_dir / "receipts"
        db_path = data_dir / "app.db"
        static_dir = base_dir / "static"
        return cls(
            base_dir=base_dir,
            data_dir=data_dir,
            receipts_dir=receipts_dir,
            db_path=db_path,
            static_dir=static_dir,
        )

    def ensure_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.receipts_dir.mkdir(parents=True, exist_ok=True)
