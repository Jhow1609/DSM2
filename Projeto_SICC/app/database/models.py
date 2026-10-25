import datetime
import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.database.connection import Base


class StatusEnum(str, enum.Enum):
    APROVADO = "Aprovado para Comercialização"
    RESTRITO = "Lote Restrito"


class AssayResult(Base):
    __tablename__ = "assay_results"

    id = Column(Integer, primary_key=True, index=True)
    client_code = Column(String, index=True)
    concessionaire = Column(String)
    water_absorption = Column(Float)
    break_torque = Column(Float)
    flammability = Column(String)

    status = Column(SQLEnum(StatusEnum), default=StatusEnum.RESTRITO)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class NormStandard(Base):
    """Cadastro de Normas, Limites Técnicos e Tolerâncias por Concessionária"""
    __tablename__ = "norm_standards"

    id = Column(Integer, primary_key=True, index=True)
    concessionaire = Column(String, index=True)   # ex: CPFL, ENEL, EDP
    assay_name = Column(String, index=True)       # ex: Torque de Ruptura, Absorção de Água
    gauge_range = Column(String, nullable=True)   # ex: "35-70mm²"
    client_code = Column(String, nullable=True)   # ex: "10000039806"
    norm_reference = Column(String)               # ex: EN 50483-4/Item 6
    min_value = Column(Float, nullable=True)      # ex: 12.0
    max_value = Column(Float, nullable=True)      # ex: 18.0
    tolerance_pct = Column(Float, default=0.0)    # ex: 5.0 (5% de tolerância)
    expected_text = Column(String, nullable=True) # ex: HB40


class AssayBatch(Base):
    """Lote/Cabeçalho do Relatório de Ensaios"""
    __tablename__ = "assay_batches"

    id = Column(Integer, primary_key=True, index=True)
    client_code = Column(String, index=True)
    concessionaire = Column(String)
    status_general = Column(String, default="Pendente")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    items = relationship("AssayItem", back_populates="batch", cascade="all, delete-orphan")


class AssayItem(Base):
    """Item/Ensaio do Lote"""
    __tablename__ = "assay_items"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("assay_batches.id"))
    assay_name = Column(String)
    measured_numeric = Column(Float, nullable=True)
    measured_text = Column(String, nullable=True)
    norm_reference = Column(String, nullable=True)
    status = Column(String, nullable=True)

    batch = relationship("AssayBatch", back_populates="items")