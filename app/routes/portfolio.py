from typing import Dict, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.optimizer import optimize_portfolio

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])

# Request model
class OptimizeRequest(BaseModel):
    lista_acoes: List[str] = Field(min_length=1)
    lista_dy: List[float]
    lista_desvio_padrao: List[float]
    lista_setor: List[str]
    percentual_maximo_por_setor: float = Field(0.2, gt=0, le=1)

# Response models
class AllocationByAsset(BaseModel):
    ativo: str
    setor: str
    percentual: float  # in %

class OptimizeResponse(BaseModel):
    dividend_yield: float
    risco_carteira: float
    risco_aceitavel: float
    alocacao_por_ativo: List[AllocationByAsset]
    alocacao_por_setor: Dict[str, float]

@router.post("/optimize", response_model=OptimizeResponse)
def optimize(req: OptimizeRequest):
    n = len(req.lista_acoes)
    if not (len(req.lista_dy) == n and len(req.lista_desvio_padrao) == n and len(req.lista_setor) == n):
        raise HTTPException(status_code=400, detail="All lists must have the same length.")

    result = optimize_portfolio(
        req.lista_acoes,
        req.lista_dy,
        req.lista_desvio_padrao,
        req.lista_setor,
        req.percentual_maximo_por_setor,
    )

    if result is None:
        raise HTTPException(status_code=422, detail="No feasible solution with given constraints.")

    return result
