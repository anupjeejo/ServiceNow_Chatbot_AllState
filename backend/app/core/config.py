from pathlib import Path
import os

from dotenv import load_dotenv


def _load_environment() -> None:
    """Load environment variables from common project .env locations."""
    root_dir = Path(__file__).resolve().parents[3]
    candidate_paths = (
        root_dir / ".env",
        root_dir / "backend" / ".env",
        Path.cwd() / ".env",
        Path.cwd() / "backend" / ".env",
    )

    for env_path in candidate_paths:
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=False)


class Settings:
    def __init__(self) -> None:
        _load_environment()
        self.SN_INSTANCE = os.getenv("SN_INSTANCE")
        self.SN_USER = os.getenv("SN_USER")
        self.SN_PASSWORD = os.getenv("SN_PASSWORD")
        self.OLLAMA_URL = os.getenv("OLLAMA_URL")

    def validate_servicenow(self) -> None:
        if not self.SN_INSTANCE:
            raise RuntimeError(
                "SN_INSTANCE is missing. Set it in your environment or .env file."
            )
        if not self.SN_USER or not self.SN_PASSWORD:
            raise RuntimeError(
                "ServiceNow credentials missing. Set SN_USER and SN_PASSWORD."
            )


settings = Settings()
