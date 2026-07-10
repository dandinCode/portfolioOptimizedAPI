from typing import Dict, List, Optional

from mip import CONTINUOUS, Model, maximize, xsum

from app.schemas.portfolio import ConstraintConfig


def optimize_portfolio_custom(
    stock_list: List[str],
    dy_list: List[float],
    standard_deviation_list: List[float],
    sectors_list: List[str],
    acceptable_risk: Optional[float],
    max_percentage_per_sector: float,
    constraints: ConstraintConfig,
) -> Optional[Dict]:
    """
    Modelo personalizável: mesma base do optimizer.py (1.0),
    com restrições de programação linear ligáveis pelo usuário.
    """
    n = len(stock_list)
    model = Model("PortfolioOptimizedCustom")

    if acceptable_risk is None:
        acceptable_risk = sum(standard_deviation_list) / len(standard_deviation_list)

    x = [model.add_var(var_type=CONTINUOUS, lb=0.0) for _ in range(n)]

    model.objective = maximize(xsum(x[i] * dy_list[i] for i in range(n)))

    if constraints.use_risk_limit:
        model += xsum(x[i] * standard_deviation_list[i] for i in range(n)) <= acceptable_risk

    if constraints.use_sector_cap:
        sector_indices: Dict[str, List[int]] = {}
        for i, sector in enumerate(sectors_list):
            sector_indices.setdefault(sector, []).append(i)
        for indices in sector_indices.values():
            model += xsum(x[i] for i in indices) <= max_percentage_per_sector

    if constraints.use_full_allocation:
        model += xsum(x[i] for i in range(n)) == 1.0
    else:
        model += xsum(x[i] for i in range(n)) <= 1.0

    model.optimize()

    if model.num_solutions <= 0:
        return None

    allocations = []
    portfolio_risk = 0.0
    dy_portfolio = 0.0
    for i in range(n):
        wi = x[i].x or 0.0
        if wi > 1e-6:
            portfolio_risk += wi * standard_deviation_list[i]
            dy_portfolio += wi * dy_list[i]
            allocations.append(
                {
                    "stock": stock_list[i],
                    "percentage": wi * 100.0,
                    "sector": sectors_list[i],
                }
            )

    sector_allocation: Dict[str, float] = {}
    for allocation in allocations:
        sector_allocation[allocation["sector"]] = (
            sector_allocation.get(allocation["sector"], 0.0) + allocation["percentage"]
        )

    return {
        "dividend_yield": dy_portfolio,
        "portfolio_risk": portfolio_risk,
        "acceptable_risk": acceptable_risk,
        "stock_allocation": sorted(allocations, key=lambda item: -item["percentage"]),
        "allocation_by_sector": {
            key: round(value, 6) for key, value in sorted(sector_allocation.items())
        },
    }
