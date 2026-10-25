from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.database.connection import engine, Base
from app.api.routes import router

# Cria as tabelas do banco de dados na inicialização
Base.metadata.create_all(bind=engine)

# Instância única da aplicação FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Motor de regras de conformidade técnica para ensaios laboratoriais."
)

# Obtém o caminho absoluto do diretório 'app'
BASE_DIR = Path(__file__).resolve().parent

# Configura a pasta de templates (app/templates)
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Inclui as rotas de API sob o prefixo /api/v1
app.include_router(router, prefix="/api/v1")

# Rota principal (Interface Web / Dashboard)
@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html"
    )

# Rota secundária/auxiliar de verificação da API
@app.get("/health")
def health_check():
    return {"message": "SICC API rodando com sucesso!"}