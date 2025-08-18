from typing import Dict, List, Optional
from mip import Model, xsum, maximize, CONTINUOUS

def optimize_portfolio(
    stock_list: List[str],
    dy_list: List[float],
    standard_deviation_list: List[float],
    sectors_list: List[str],
    acceptable_risk: Optional[float],
    max_percentage_per_sector: float = 0.2,
) -> Optional[Dict]:
    n = len(stock_list)
    m = Model("PortfolioOptimized")

    if acceptable_risk is None:
        acceptable_risk = sum(standard_deviation_list) / len(standard_deviation_list)

    # decision variables: allocation weight of each asset (>= 0)
    x = [m.add_var(var_type=CONTINUOUS, lb=0.0) for _ in range(n)]

    # objective: maximize portfolio DY
    m.objective = maximize(xsum(x[i] * dy_list[i] for i in range(n)))

    # constraint: weighted risk <= acceptable risk
    m += xsum(x[i] * standard_deviation_list[i] for i in range(n)) <= acceptable_risk

    # constraint: cap per sector (your code capped sector exposure, not per-asset)
    sector_indices: Dict[str, List[int]] = {}
    for i, sector in enumerate(sectors_list):
        sector_indices.setdefault(sector, []).append(i)
    for indices in sector_indices.values():
        m += xsum(x[i] for i in indices) <= max_percentage_per_sector

    # constraint: invest 100% of capital
    m += xsum(x[i] for i in range(n)) == 1.0

    m.optimize()

    if m.num_solutions <= 0:
        return None

    # build result
    allocations = []
    portfolio_risk = 0.0
    dy_portfolio = 0.0
    for i in range(n):
        wi = x[i].x or 0.0
        if wi > 1e-6:
            portfolio_risk += wi * standard_deviation_list[i]
            dy_portfolio += wi * dy_list[i]
            allocations.append({
                "stock": stock_list[i],
                "percentage": wi * 100.0,
                "sector": sectors_list[i],
            })

    # aggregate by sector
    sector_allocation: Dict[str, float] = {}
    for a in allocations:
        sector_allocation[a["sector"]] = sector_allocation.get(a["sector"], 0.0) + a["percentage"]

    return {
        "dividend_yield": dy_portfolio,
        "portfolio_risk": portfolio_risk,
        "acceptable_risk": acceptable_risk,
        "stock_allocation": sorted(allocations, key=lambda k: -k["percentage"]),
        "allocation_by_sector": {k: round(v, 6) for k, v in sorted(sector_allocation.items())},
    }
