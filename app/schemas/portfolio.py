from typing import Dict, List, Optional
from pydantic import BaseModel, Field, model_validator


class ConstraintConfig(BaseModel):
    use_risk_limit: bool = True
    use_sector_cap: bool = True
    use_full_allocation: bool = True
    require_min_sectors: bool = True


class ConstraintDefinition(BaseModel):
    key: str
    label: str
    description: str
    default_enabled: bool = True


class OptimizeRequest(BaseModel):
    model_id: str = Field(..., description="Identificador do modelo (ex: 1.0, custom)")
    stock_list: List[str] = Field(min_length=1)
    dy_list: List[float]
    standard_deviation_list: List[float]
    sectors_list: List[str]
    constraints: ConstraintConfig
    max_percentage_per_sector: float = Field(0.2, gt=0, le=1)
    acceptable_risk: Optional[float] = None

    @model_validator(mode="after")
    def validate_lists_length(self):
        n = len(self.stock_list)
        if not (
            len(self.dy_list) == n
            and len(self.standard_deviation_list) == n
            and len(self.sectors_list) == n
        ):
            raise ValueError("All lists must have the same length.")
        return self


class AllocationByAsset(BaseModel):
    stock: str
    sector: str
    percentage: float


class OptimizeResponse(BaseModel):
    model_id: str
    dividend_yield: float
    portfolio_risk: float
    acceptable_risk: float
    stock_allocation: List[AllocationByAsset]
    allocation_by_sector: Dict[str, float]
    constraints_applied: ConstraintConfig
