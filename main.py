from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import portfolio

app = FastAPI(title="Portfolio Optimizer API", version="1.0.0")

# (Optional) enable CORS for browser clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(portfolio.router)

@app.get("/")
def root():
    return {"message": "Portfolio Optimizer API is running."}
