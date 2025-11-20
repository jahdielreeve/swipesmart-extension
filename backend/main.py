from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class RecommendationRequest(BaseModel):
    url: str
    amount: float
    currency: str = "SGD"

@app.get("/")
def root():
    return {"message": "SwipeSmart backend running"}

@app.post("/recommend-card")
def recommend_card(req: RecommendationRequest):
    # temporary dummy logic
    return {
        "best_card": "DBS Altitude",
        "estimated_miles": req.amount * 1.3,
        "reason": "Dummy logic for now."
    }
