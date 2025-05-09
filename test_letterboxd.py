import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

def get_ratings_and_reviews(film_slug: str, page: int = 1):
    url = f"https://letterboxd.com/film/{film_slug}/reviews/by/activity/page/{page}/"

    try:
        response = requests.get(url)
        response.raise_for_status()
    except RequestException as e:
        raise Exception(f"Erreur HTTP : {str(e)}")

    soup = BeautifulSoup(response.text, 'html.parser')
    reviews = []

    review_blocks = soup.find_all('div', class_='film-detail-content')

    for block in review_blocks:
        # Note
        rating_tag = block.find('span', class_='rating')
        rating = rating_tag.text.strip() if rating_tag else None

        # Texte de la critique
        review_text_tag = block.find('div', class_='body-text')
        review = review_text_tag.get_text(separator=" ", strip=True) if review_text_tag else None

        if review:  # inclure seulement si la critique a du texte
            reviews.append({
                'rating': rating,
                'review': review
            })

    return reviews

# Exemple d'utilisation
if __name__ == "__main__":
    film_slug = "conclave"
    results = get_ratings_and_reviews(film_slug)
    for item in results:
        print(item)
