from fastapi import APIRouter, HTTPException

from app.custom_optimizer import optimize_portfolio_custom
from app.optimizer import optimize_portfolio
from app.schemas.portfolio import (
    ConstraintConfig,
    ConstraintDefinition,
    OptimizeRequest,
    OptimizeResponse,
)

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])

MIN_SECTORS = 5
MODEL_1_0 = "1.0"
MODEL_CUSTOM = "custom"

AVAILABLE_CONSTRAINTS = [
    ConstraintDefinition(
        key="use_risk_limit",
        label="Limite de risco",
        description="A carteira não pode ultrapassar o risco aceitável (volatilidade ponderada).",
        default_enabled=True,
    ),
    ConstraintDefinition(
        key="use_sector_cap",
        label="Limite por setor",
        description="Nenhum setor pode concentrar mais do que o percentual máximo definido.",
        default_enabled=True,
    ),
    ConstraintDefinition(
        key="use_full_allocation",
        label="Alocação total",
        description="Todo o capital deve ser distribuído entre os ativos (100%).",
        default_enabled=True,
    ),
    ConstraintDefinition(
        key="require_min_sectors",
        label="Diversificação mínima",
        description=f"Exige pelo menos {MIN_SECTORS} setores diferentes na seleção.",
        default_enabled=True,
    ),
]

DEFAULT_CONSTRAINTS = ConstraintConfig()


def _validate_min_sectors(sectors_list: list[str]) -> None:
    if len(set(sectors_list)) < MIN_SECTORS:
        raise HTTPException(
            status_code=400,
            detail=f"São necessários pelo menos {MIN_SECTORS} setores diferentes.",
        )


@router.get("/constraints", response_model=list[ConstraintDefinition])
def list_constraints():
    return AVAILABLE_CONSTRAINTS


@router.post("/optimize", response_model=OptimizeResponse)
def optimize(req: OptimizeRequest):
    if req.model_id == MODEL_1_0:
        _validate_min_sectors(req.sectors_list)
        result = optimize_portfolio(
            req.stock_list,
            req.dy_list,
            req.standard_deviation_list,
            req.sectors_list,
            req.acceptable_risk,
            req.max_percentage_per_sector,
        )
        constraints_applied = DEFAULT_CONSTRAINTS
    elif req.model_id == MODEL_CUSTOM:
        if req.constraints.require_min_sectors:
            _validate_min_sectors(req.sectors_list)
        result = optimize_portfolio_custom(
            req.stock_list,
            req.dy_list,
            req.standard_deviation_list,
            req.sectors_list,
            req.acceptable_risk,
            req.max_percentage_per_sector,
            req.constraints,
        )
        constraints_applied = req.constraints
    else:
        raise HTTPException(
            status_code=400,
            detail=f'Modelo "{req.model_id}" não suportado pela API de otimização.',
        )

    if result is None:
        raise HTTPException(
            status_code=422,
            detail="Não existe solução viável com as restrições dadas.",
        )

    return OptimizeResponse(
        model_id=req.model_id,
        constraints_applied=constraints_applied,
        **result,
    )
