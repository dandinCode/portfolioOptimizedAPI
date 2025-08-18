from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.optimizer import optimize_portfolio

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])

# Request model
class OptimizeRequest(BaseModel):
    stock_list: List[str] = Field(min_length=1)
    dy_list: List[float]
    standard_deviation_list: List[float]
    sectors_list: List[str]
    max_percentage_per_sector: float = Field(0.2, gt=0, le=1) 
    acceptable_risk: Optional[float] = None
# Response models
class AllocationByAsset(BaseModel):
    stock: str
    sector: str
    percentage: float  # in %

class OptimizeResponse(BaseModel):
    dividend_yield: float
    portfolio_risk: float
    acceptable_risk: float
    stock_allocation: List[AllocationByAsset]
    allocation_by_sector: Dict[str, float]

@router.post("/optimize", response_model=OptimizeResponse)
def optimize(req: OptimizeRequest):
    n = len(req.stock_list)
    if not (len(req.dy_list) == n and len(req.standard_deviation_list) == n and len(req.sectors_list) == n):
        raise HTTPException(status_code=400, detail="All lists must have the same length.")

    result = optimize_portfolio(
        req.stock_list,
        req.dy_list,
        req.standard_deviation_list,
        req.sectors_list,
        req.acceptable_risk,
        req.max_percentage_per_sector,
    )

    if result is None:
        raise HTTPException(status_code=422, detail="No feasible solution with given constraints.")

    return result
