from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from letterboxd_llm import get_all_ratings_and_reviews
from requests.exceptions import HTTPError

app = FastAPI(title="Letterboxd Review Sentiment API")

class SentimentResult(BaseModel):
    sentiment_score: Optional[int]
    confidence: float

class ReviewResult(BaseModel):
    rating: Optional[float]
    review: str
    sentiment: SentimentResult


#http://localhost:8000/reviews?film_slug=iron man&max_pages=2
@app.get("/reviews", response_model=List[ReviewResult])
def read_reviews(
    film_slug: str = Query(..., description="Slug Letterboxd du film (ex: iron-man)"),
    max_pages: int = Query(1, description="Nombre de pages à scraper (par défaut : 1)")
):
    try:
        return get_all_ratings_and_reviews(film_slug, max_pages=max_pages)
    except HTTPError as e:
        if e.response is not None and e.response.status_code == 429:
            raise HTTPException(status_code=429, detail="Trop de requêtes envoyées à Letterboxd.")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des critiques.")
