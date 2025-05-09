import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

def get_all_ratings_and_reviews(film_slug: str, max_pages: int = None):
    page = 1
    all_reviews = []
    #regex pour remplacer les espaces par des tirets 
    film_slug = film_slug.replace(" ", "-").lower()
    while True:
        url = f"https://letterboxd.com/film/{film_slug}/reviews/by/activity/page/{page}/"
        print(f"Scraping page {page} : {url}")
        try:
            response = requests.get(url)
            response.raise_for_status()
        except RequestException as e:
            print(f"Erreur HTTP sur la page {page} : {str(e)}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        review_blocks = soup.find_all('div', class_='film-detail-content')

        if not review_blocks:
            print("Aucun bloc de critique trouvé, fin du scraping.")
            break

        for block in review_blocks:
            rating_tag = block.find('span', class_='rating')
            rating = rating_tag.text.strip() if rating_tag else None

            review_text_tag = block.find('div', class_='body-text')
            review = review_text_tag.get_text(separator=" ", strip=True) if review_text_tag else None

            if review:
                all_reviews.append({
                    'rating': rating,
                    'review': review
                })

        page += 1
        if max_pages and page > max_pages:
            print("Limite de pages atteinte.")
            break

    return all_reviews

# Exemple d'utilisation
if __name__ == "__main__":
    film_slug = "iron man"
    results = get_all_ratings_and_reviews(film_slug, max_pages=5)  # change max_pages selon besoin
    for item in results:
        print(item)

 