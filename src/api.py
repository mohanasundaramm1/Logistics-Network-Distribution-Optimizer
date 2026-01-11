from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.optimizer import LogisticsOptimizer
import uvicorn

app = FastAPI(
    title="Logistics Network & Distribution API",
    description="Operationalized Optimization Engine for Distribution Network Management",
    version="1.0.0"
)

class OptimizationResult(BaseModel):
    status: str
    optimal_profit: float
    chosen_trucks: list[str]
    assignments: dict

@app.get("/")
def read_root():
    return {"message": "Supply Chain Optimization API is online."}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/optimize", response_model=OptimizationResult)
def run_optimization():
    try:
        optimizer = LogisticsOptimizer()
        result = optimizer.solve()
        
        if result.get("status") == "ERROR":
            raise HTTPException(status_code=500, detail=result.get("message"))
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
