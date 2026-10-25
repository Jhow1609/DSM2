import io
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import connection, models
from app.schemas import assay as schemas
from app.services.pdf_generator import generate_pdf_report
from app.services.rules_engine import DynamicRulesEngine, RulesEngine

router = APIRouter()

# ----------------------------------------------------------------------
# 1. ROTAS DE ENSAIOS INDIVIDUAIS E GERAÇÃO DE LAUDOS (PDF)
# ----------------------------------------------------------------------


@router.post("/assays/validate-and-save")
def validate_and_save_assay(
    payload: schemas.AssayInputSchema, db: Session = Depends(connection.get_db)
):
    """Valida um ensaio individual com motor estático e grava no banco"""
    data = payload.model_dump()
    eval_result = RulesEngine.evaluate(data)

    status_enum_val = (
        models.StatusEnum.APROVADO
        if eval_result["status_geral"] == models.StatusEnum.APROVADO.value
        else models.StatusEnum.RESTRITO
    )

    db_assay = models.AssayResult(
        client_code=payload.client_code,
        concessionaire=payload.concessionaire,
        water_absorption=payload.water_absorption,
        break_torque=payload.break_torque,
        flammability=payload.flammability,
        status=status_enum_val,
    )
    db.add(db_assay)
    db.commit()
    db.refresh(db_assay)

    return {
        "id": db_assay.id,
        "status_geral": eval_result["status_geral"],
        "detalhes": eval_result["details"],
    }


@router.get("/assays/{assay_id}/pdf")
def generate_assay_pdf(assay_id: int, db: Session = Depends(connection.get_db)):
    """Gera e retorna o relatório em PDF de um ensaio cadastrado"""
    db_assay = (
        db.query(models.AssayResult)
        .filter(models.AssayResult.id == assay_id)
        .first()
    )
    if not db_assay:
        raise HTTPException(
            status_code=404, detail="Resultado de ensaio não encontrado"
        )

    assay_data = {
        "client_code": db_assay.client_code,
        "concessionaire": db_assay.concessionaire,
        "water_absorption": db_assay.water_absorption,
        "break_torque": db_assay.break_torque,
        "flammability": db_assay.flammability,
    }

    eval_result = RulesEngine.evaluate(assay_data)
    pdf_buffer = generate_pdf_report(assay_data, eval_result)
    pdf_buffer.seek(0)

    filename = (
        f"Relatorio_Conformidade_{db_assay.concessionaire}_{db_assay.id}.pdf"
    )
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ----------------------------------------------------------------------
# 2. CONSULTA E CADASTRO DE NORMAS TÉCNICAS
# ----------------------------------------------------------------------


@router.post("/norms/", response_model=schemas.NormResponseSchema)
def create_norm(
    norm: schemas.NormCreateSchema, db: Session = Depends(connection.get_db)
):
    """Cadastra uma norma de referência técnica para uma concessionária"""
    db_norm = models.NormStandard(**norm.model_dump())
    db.add(db_norm)
    db.commit()
    db.refresh(db_norm)
    return db_norm


@router.get("/norms/search", response_model=List[schemas.NormResponseSchema])
def search_norms(
    concessionaire: Optional[str] = Query(
        None, description="Filtra por concessionária (ex: CPFL, ENEL, EDP)"
    ),
    assay_name: Optional[str] = Query(
        None, description="Filtra por tipo de ensaio"
    ),
    db: Session = Depends(connection.get_db),
):
    """Consulta as normas cadastradas no motor de regras"""
    query = db.query(models.NormStandard)
    if concessionaire:
        query = query.filter(
            models.NormStandard.concessionaire.ilike(f"%{concessionaire}%")
        )
    if assay_name:
        query = query.filter(
            models.NormStandard.assay_name.ilike(f"%{assay_name}%")
        )
    return query.all()


# ----------------------------------------------------------------------
# 3. INSERÇÃO E VALIDAÇÃO DE LOTES DE ENSAIOS
# ----------------------------------------------------------------------


@router.post("/batches/insert-and-validate")
def insert_batch_assays(
    payload: schemas.BatchInputSchema, db: Session = Depends(connection.get_db)
):
    """Insere um lote com múltiplos ensaios e valida contra as normas cadastradas"""

    batch = models.AssayBatch(
        client_code=payload.client_code, concessionaire=payload.concessionaire
    )
    db.add(batch)
    db.flush()

    all_approved = True

    for item_data in payload.assays:
        item = models.AssayItem(
            batch_id=batch.id,
            assay_name=item_data.assay_name,
            measured_numeric=item_data.measured_numeric,
            measured_text=item_data.measured_text,
        )

        is_ok = DynamicRulesEngine.evaluate_item(
            item, db, payload.concessionaire, payload.client_code
        )
        if not is_ok:
            all_approved = False

        db.add(item)

    # Resolve o erro de atribuição do Pylance ("str" is not assignable to "Column[str]")
    status_str = "Aprovado para Comercialização" if all_approved else "Lote Restrito"
    setattr(batch, "status_general", status_str)

    db.commit()
    db.refresh(batch)

    return {
        "batch_id": getattr(batch, "id"),
        "client_code": batch.client_code,
        "concessionaire": batch.concessionaire,
        "status_geral": getattr(batch, "status_general"),
        "total_ensaios": len(payload.assays),
    }


@router.get("/assays/batch/{batch_id}/pdf")
def download_batch_pdf(
    batch_id: int, db: Session = Depends(connection.get_db)
):
    """
    Gera e faz o download direto do relatório PDF de um lote de ensaios com suporte a QR Code.
    """
    batch = (
        db.query(models.AssayBatch)
        .filter(models.AssayBatch.id == batch_id)
        .first()
    )
    if not batch:
        raise HTTPException(
            status_code=404, detail="Lote de ensaios não encontrado"
        )

    assay_data = {
        "concessionaire": batch.concessionaire,
        "client_code": batch.client_code,
        "items": [],
    }

    for item in batch.items:
        assay_data["items"].append(
            {
                "assay_name": item.assay_name,
                "norm_reference": getattr(item, "norm_reference", None),
                "measured_value": (
                    item.measured_numeric
                    if item.measured_numeric is not None
                    else item.measured_text
                ),
                "status": getattr(item, "status", None),
            }
        )

    validation_results = {"status_geral": getattr(batch, "status_general")}

    # Resolve o erro do Pylance ("Column[int]" is not assignable to "ConvertibleToInt")
    actual_batch_id = int(getattr(batch, "id"))

    pdf_buffer: io.BytesIO = generate_pdf_report(
        assay_data, validation_results, batch_id=actual_batch_id
    )
    pdf_buffer.seek(0)

    filename = (
        f"Relatorio_Conformidade_{batch.concessionaire}_Lote_{actual_batch_id}.pdf"
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )