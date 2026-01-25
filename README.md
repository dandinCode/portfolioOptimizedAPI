# Portfolio Optimization API

## Descrição do Projeto

Este projeto é uma API desenvolvida em **Python 3.11.6** utilizando **FastAPI** para otimização de carteiras de investimentos.  
O sistema recebe listas de ativos, dividend yields, desvio padrão e setores, e retorna uma alocação ótima que maximize o **Dividend Yield** da carteira com base no perfil do investidor, respeitando restrições de risco e limites por setor.

O núcleo da otimização é baseado na **Programação Linear (PL)** utilizando o solver **MIP (Mixed Integer/Linear Programming)** através da biblioteca [**Python-MIP**](https://python-mip.readthedocs.io/).

---

## Funcionalidades

- Receber uma lista de ativos (`lista_acoes`) e suas características:
  - Dividend Yield (`lista_dy`)
  - Risco (`lista_desvio_padrao`)
  - Setor (`lista_setor`)
- Permitir definir:
  - `risco_aceitavel` (opcional; se não informado, é calculado automaticamente com base no perfil moderado)
  - `percentual_maximo_por_setor`
- Retornar:
  - Dividend Yield da carteira otimizada
  - Risco da carteira
  - Alocação por ativo
  - Alocação por setor

---

## Requisitos

- Python 3.11.6
- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/) (para rodar o servidor)
- [Python-MIP](https://python-mip.readthedocs.io/)

---

## Instalação

1. Clone este repositório:

```bash
git clone https://github.com/dandinCode/portfolioOptimizedAPI.git
cd portfolio-optimization-api
```

2. Crie e ative um ambiente virtual:

```bash
python -m venv venv
venv\Scripts\activate
```

3. Instale as dependências:

```bash
pip install requirements.txt
```

---

## Como Rodar 

1. Execute o servidor localmente:

```bash
python -m uvicorn main:app --reload
```

2. O servidor estará disponível em: http://127.0.0.1:8000
3. Exemplo de corpo da requisição:
```bash
{
  "lista_acoes": ["PETR4", "ITUB4", "PETR3", "BBAS3"],
  "lista_dy": [23.82, 1.25, 22.51, 6.88],
  "lista_desvio_padrao": [2.0, 1.47, 2.05, 1.52],
  "lista_setor": ["Energy", "Financial Services", "Energy", "Financial Services"],
  "risco_aceitavel": 2.27
}
```
