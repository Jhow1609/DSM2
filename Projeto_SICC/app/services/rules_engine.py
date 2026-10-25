from typing import Any, Dict, Optional, Tuple, cast
from sqlalchemy.orm import Session
from app.database import models


class RulesEngine:
    """
    Motor de regras estático para validação de normas específicas (NBR, EN, UL 94)
    """

    @staticmethod
    def validate_water_absorption(value: float) -> Tuple[bool, str]:
        if value > 6.0:
            return False, "Reprovado (> 6.0%)"
        return True, "Aprovado"

    @staticmethod
    def validate_break_torque(value: float) -> Tuple[bool, str]:
        if value < 12.0 or value > 18.0:
            return False, "Reprovado (Fora de 12Nm - 18Nm)"
        return True, "Aprovado"

    @staticmethod
    def validate_flammability(value: str) -> Tuple[bool, str]:
        if not value or value.strip().upper() != "HB40":
            return False, "Alerta de Segurança (Diferente de HB40)"
        return True, "Aprovado"

    @classmethod
    def evaluate(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        water_ok, water_msg = cls.validate_water_absorption(data["water_absorption"])
        torque_ok, torque_msg = cls.validate_break_torque(data["break_torque"])
        flam_ok, flam_msg = cls.validate_flammability(data["flammability"])

        all_passed = water_ok and torque_ok and flam_ok
        status_geral = "Aprovado para Comercialização" if all_passed else "Lote Restrito"

        return {
            "status_geral": status_geral,
            "details": {
                "water_absorption": water_msg,
                "break_torque": torque_msg,
                "flammability": flam_msg
            }
        }


class DynamicRulesEngine:
    """
    Motor de regras dinâmico compatível com SQLAlchemy clássico e tipagem do Pylance.
    """

    @staticmethod
    def evaluate_item(
        item_input: Any, 
        db: Session, 
        concessionaire: str, 
        client_code: Optional[str] = None
    ) -> bool:
        # Busca a regra correspondente na base de normas
        query = db.query(models.NormStandard).filter(
            models.NormStandard.concessionaire.ilike(concessionaire),
            models.NormStandard.assay_name.ilike(item_input.assay_name)
        )
        
        if client_code:
            code_match = query.filter(models.NormStandard.client_code == client_code).first()
            rule = code_match if code_match else query.first()
        else:
            rule = query.first()

        if rule is None:
            setattr(item_input, "norm_reference", "Norma não cadastrada")
            setattr(item_input, "status", "Alerta: Sem Regra")
            return False

        setattr(item_input, "norm_reference", str(rule.norm_reference))
        tol: float = float(getattr(rule, "tolerance_pct", 0.0) or 0.0)

        # Validação para valores numéricos
        if item_input.measured_numeric is not None:
            val = float(item_input.measured_numeric)
            min_val = getattr(rule, "min_value", None)
            max_val = getattr(rule, "max_value", None)

            # Limite mínimo com tolerância
            if min_val is not None:
                min_limit = float(min_val) * (1.0 - tol / 100.0)
                if val < min_limit:
                    setattr(item_input, "status", f"Rejeitado (< {min_val})")
                    return False

            # Limite máximo com tolerância
            if max_val is not None:
                max_limit = float(max_val) * (1.0 + tol / 100.0)
                if val > max_limit:
                    setattr(item_input, "status", f"Rejeitado (> {max_val})")
                    return False

            setattr(item_input, "status", "Aprovado")
            return True

        # Validação para valores textuais
        if item_input.measured_text is not None:
            exp_text = getattr(rule, "expected_text", None)
            meas_text = str(item_input.measured_text).strip().upper()
            
            if exp_text and meas_text != str(exp_text).strip().upper():
                setattr(item_input, "status", f"Alerta ({item_input.measured_text} != {exp_text})")
                return False
                
            setattr(item_input, "status", "Aprovado")
            return True

        setattr(item_input, "status", "Dado ausente")
        return False