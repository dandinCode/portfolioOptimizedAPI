from typing import Dict, List, Optional
from mip import Model, xsum, maximize, CONTINUOUS

def optimize_portfolio(
    lista_acoes: List[str],
    lista_dy: List[float],
    lista_desvio_padrao: List[float],
    lista_setor: List[str],
    percentual_maximo_por_setor: float = 0.2,
) -> Optional[Dict]:
    n = len(lista_acoes)
    m = Model("PortfolioOptimized")

    # decision variables: allocation weight of each asset (>= 0)
    x = [m.add_var(var_type=CONTINUOUS, lb=0.0) for _ in range(n)]

    # risk threshold (same formula you used: average of std devs)
    risco_aceitavel = sum(lista_desvio_padrao) / n

    # objective: maximize portfolio DY
    m.objective = maximize(xsum(x[i] * lista_dy[i] for i in range(n)))

    # constraint: weighted risk <= acceptable risk
    m += xsum(x[i] * lista_desvio_padrao[i] for i in range(n)) <= risco_aceitavel

    # constraint: cap per sector (your code capped sector exposure, not per-asset)
    setor_indices: Dict[str, List[int]] = {}
    for i, setor in enumerate(lista_setor):
        setor_indices.setdefault(setor, []).append(i)
    for indices in setor_indices.values():
        m += xsum(x[i] for i in indices) <= percentual_maximo_por_setor

    # constraint: invest 100% of capital
    m += xsum(x[i] for i in range(n)) == 1.0

    m.optimize()

    if m.num_solutions <= 0:
        return None

    # build result
    alocacoes = []
    risco_carteira = 0.0
    dy_carteira = 0.0
    for i in range(n):
        wi = x[i].x or 0.0
        if wi > 1e-6:
            risco_carteira += wi * lista_desvio_padrao[i]
            dy_carteira += wi * lista_dy[i]
            alocacoes.append({
                "ativo": lista_acoes[i],
                "percentual": wi * 100.0,
                "setor": lista_setor[i],
            })

    # aggregate by sector
    alocacao_setor: Dict[str, float] = {}
    for a in alocacoes:
        alocacao_setor[a["setor"]] = alocacao_setor.get(a["setor"], 0.0) + a["percentual"]

    return {
        "dividend_yield": dy_carteira,
        "risco_carteira": risco_carteira,
        "risco_aceitavel": risco_aceitavel,
        "alocacao_por_ativo": sorted(alocacoes, key=lambda k: -k["percentual"]),
        "alocacao_por_setor": {k: round(v, 6) for k, v in sorted(alocacao_setor.items())},
    }
