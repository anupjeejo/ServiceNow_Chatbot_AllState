from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="backend/.env")

class Settings:
    SN_INSTANCE = os.getenv("SN_INSTANCE")
    SN_USER = os.getenv("SN_USER")
    SN_PASSWORD = os.getenv("SN_PASSWORD")
    OLLAMA_URL = os.getenv("OLLAMA_URL")

    def validate(self):
        if not self.SN_INSTANCE:
            raise RuntimeError("SN_INSTANCE is missing")
        if not self.SN_USER or not self.SN_PASSWORD:
            raise RuntimeError("ServiceNow credentials missing")

settings = Settings()
settings.validate()
