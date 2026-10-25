from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ----------------------------------------------------------------------
# 1. Schemas de Ensaios Individuais (Amostra Simples / Legado)
# ----------------------------------------------------------------------
class AssayInputSchema(BaseModel):
    client_code: str = Field(
        ...,
        description="Código do cliente/bitola",
        json_schema_extra={"example": "10000039806"},
    )
    concessionaire: str = Field(
        ...,
        description="Concessionária (CPFL, ENEL, EDP)",
        json_schema_extra={"example": "CPFL"},
    )
    water_absorption: float = Field(
        ...,
        description="Absorção de Água (%) - NBR 17173-3/Item 29",
        json_schema_extra={"example": 4.5},
    )
    break_torque: float = Field(
        ...,
        description="Torque de Ruptura (Nm) - EN 50483-4/Item 6",
        json_schema_extra={"example": 15.0},
    )
    flammability: str = Field(
        ...,
        description="Classe de Flamabilidade - UL 94/Item 33",
        json_schema_extra={"example": "HB40"},
    )


class AssayResponseSchema(AssayInputSchema):
    id: int
    status: str
    water_absorption_status: str
    break_torque_status: str
    flammability_status: str

    model_config = ConfigDict(from_attributes=True)


# ----------------------------------------------------------------------
# 2. Schemas de Normas e Limites Técnicos
# ----------------------------------------------------------------------
class NormCreateSchema(BaseModel):
    concessionaire: str = Field(..., description="Concessionária (ex: CPFL)")
    assay_name: str = Field(..., description="Nome do ensaio")
    norm_reference: str = Field(..., description="Referência da norma técnica")
    min_value: Optional[float] = Field(None, description="Limite mínimo aceitável")
    max_value: Optional[float] = Field(None, description="Limite máximo aceitável")
    expected_text: Optional[str] = Field(None, description="Texto/Classe esperado")


class NormResponseSchema(NormCreateSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)


# ----------------------------------------------------------------------
# 3. Schemas de Lote e Inserção Dinâmica de Ensaios
# ----------------------------------------------------------------------
class AssayItemInput(BaseModel):
    assay_name: str = Field(..., description='Nome do ensaio (ex: "Absorção de Água")')
    measured_numeric: Optional[float] = Field(None, description="Valor numérico medido")
    measured_text: Optional[str] = Field(None, description='Texto medido (ex: "HB40")')


class AssayItemResponse(AssayItemInput):
    id: int
    norm_reference: Optional[str] = None
    status: str

    model_config = ConfigDict(from_attributes=True)


class BatchInputSchema(BaseModel):
    client_code: str = Field(..., description='Código do cliente (ex: "10000039806")')
    concessionaire: str = Field(..., description='Concessionária (ex: "CPFL")')
    assays: List[AssayItemInput] = Field(..., description="Lista de ensaios do lote")


class BatchResponseSchema(BaseModel):
    id: int
    client_code: str
    concessionaire: str
    status_general: str
    items: List[AssayItemResponse]

    model_config = ConfigDict(from_attributes=True)