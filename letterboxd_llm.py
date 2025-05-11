import requests
from requests.exceptions import RequestException, HTTPError
from bs4 import BeautifulSoup
from transformers import pipeline
import re

# Modèle multilingue avec granularité sentimentale (1 à 5 étoiles)
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="nlptown/bert-base-multilingual-uncased-sentiment"
)

def convert_star_rating(star_str):
    if not star_str:
        return None
    full_stars = star_str.count('★')
    half_star = '½' in star_str
    return full_stars + 0.5 if half_star else full_stars

def analyze_sentiment(review_text: str):
    result = sentiment_pipeline(review_text[:512])  # Tronque si trop long
    label = result[0]['label']  # e.g. '4 stars'
    score = round(result[0]['score'], 3)
    try:
        sentiment_score = int(label[0])  # Extrait le chiffre
    except ValueError:
        sentiment_score = None
    return {
        'sentiment_score': sentiment_score,
        'confidence': score
    }

def get_all_ratings_and_reviews(film_slug: str, max_pages: int = None):
    page = 1
    all_reviews = []
    film_slug = film_slug.replace(" ", "-").lower()

    response_test = requests.get(f"https://letterboxd.com/film/{film_slug}/reviews/by/activity/page/{page}/")
    if response_test.status_code != 200:
        film_slug = re.sub(r"-\d+$", "", film_slug)

    while True:
        url = f"https://letterboxd.com/film/{film_slug}/reviews/by/activity/page/{page}/"
        print(f"Scraping page {page} : {url}")
        try:
            response = requests.get(url)
            if response.status_code == 429:
                raise HTTPError("Too Many Requests", response=response)
            response.raise_for_status()
        except HTTPError as e:
            print(f"Erreur HTTP sur la page {page} : {str(e)}")
            raise

        soup = BeautifulSoup(response.text, 'html.parser')
        review_blocks = soup.find_all('div', class_='film-detail-content')

        if not review_blocks:
            print("Aucun bloc de critique trouvé, fin du scraping.")
            break

        for block in review_blocks:
            rating_tag = block.find('span', class_='rating')
            raw_rating = rating_tag.text.strip() if rating_tag else None
            numeric_rating = convert_star_rating(raw_rating)

            review_text_tag = block.find('div', class_='body-text')
            review = review_text_tag.get_text(separator=" ", strip=True) if review_text_tag else None

            if review:
                sentiment = analyze_sentiment(review)
                all_reviews.append({
                    'rating': numeric_rating,
                    'review': review,
                    'sentiment': sentiment
                })

        page += 1
        if max_pages and page > max_pages:
            print("Limite de pages atteinte.")
            break

    return all_reviews

# Exemple d'utilisation
if __name__ == "__main__":
    film_slug = "spider-man-2002"
    results = get_all_ratings_and_reviews(film_slug, max_pages=3)
    for item in results:
        print(item)
