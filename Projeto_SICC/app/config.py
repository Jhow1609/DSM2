import os

class Settings:
    PROJECT_NAME: str = "Sistema Integrado de Conformidade (SICC)"
    VERSION: str = "1.0.0"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sicc_database.db")

settings = Settings()