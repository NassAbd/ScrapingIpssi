import time
import json
import streamlit as st
import requests
import pandas as pd
import altair as alt
import os
from dotenv import load_dotenv

# --- Clé API TMDB ---
load_dotenv()
API_KEY = os.getenv("API_KEY")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/90.0.4430.212 Safari/537.36"
}

# --- Fonctions TMDB ---
def search_movie_suggestions(query):
    if not query.strip():
        return []
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": API_KEY,
        "query": query,
        "language": "fr-FR",
        "page": 1
    }
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    return data.get("results", [])

def format_title(movie):
    title = movie['title'].lower().replace(" ", "-")
    year = movie['release_date'].split("-")[0] if movie.get('release_date') else "N/A"
    return f"{title}-{year}"

def get_poster_url(movie):
    base_url = "https://image.tmdb.org/t/p/w500"
    poster_path = movie.get("poster_path")
    return base_url + poster_path if poster_path else None

# --- Fonction d'analyse de critiques (Letterboxd API locale) ---
def load_or_fetch_data(film_slug, max_pages=3):
    all_reviews = []

    for page in range(1, max_pages + 1):
        url = f"http://localhost:8000/reviews?film_slug={film_slug}&page={page}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            all_reviews.extend(response.json())
        else:
            st.error(f"{json.loads(response.text).get("detail", "Une erreur est survenue.")}")
            break

    return all_reviews

st.set_page_config(page_title="Analyse de films", layout="centered")
st.title("🎥 Recherche & Analyse de films")

# Recherche de film
st.subheader("🔍 Recherche d’un film")
user_query = st.text_input("Tape le nom d’un film")

if user_query:
    movie_results = search_movie_suggestions(user_query)
    if movie_results:
        movie_choices = {
            format_title(movie): movie for movie in movie_results
        }

        selected_title = st.selectbox("Suggestions :", list(movie_choices.keys()))
        selected_movie = movie_choices[selected_title]
        poster_url = get_poster_url(selected_movie)

        slug_suggestion = format_title(selected_movie)

        st.markdown(f"### 🎬 {selected_movie['title']} ({selected_movie.get('release_date', 'N/A')[:4]})")
        if poster_url:
            st.image(poster_url, width=200)
        else:
            st.text("Aucune image disponible.")

        # Analyse des critiques Letterboxd
        st.subheader("🧠 Analyse des critiques Letterboxd")
        film_slug = st.text_input("Slug Letterboxd (forme conseillée: nom-du-film-année) :", slug_suggestion)
        max_pages = st.slider("Nombre de pages à scraper :", 1, 10, 3)

        if st.button("Charger les données Letterboxd"):
            reviews = load_or_fetch_data(film_slug, max_pages)

            if not reviews:
                st.warning("Aucune critique trouvée.")
                st.stop()

            # Image secondaire si différente
            if reviews[0].get("poster_url"):
                st.image(reviews[0]["poster_url"], width=200, caption="Affiche Letterboxd")

            # DataFrame et visualisations
            df = pd.DataFrame(reviews)
            df["rating"] = pd.to_numeric(df["rating"])
            df["sentiment_score"] = df["sentiment"].apply(lambda x: x["sentiment_score"])
            df["confidence"] = df["sentiment"].apply(lambda x: x["confidence"])

            st.success(f"{len(df)} critiques chargées.")

            st.subheader("📊 Répartition des notes utilisateur")
            st.altair_chart(
                alt.Chart(df).mark_bar().encode(
                    x=alt.X("rating:O", scale=alt.Scale(domain=[1, 2, 3, 4, 5]), title="Note utilisateur"),
                    y="count()",
                    tooltip=["count()", "rating"]
                ).properties(width=600),
                use_container_width=True
            )

            st.subheader("🧠 Sentiments prédits par le modèle")
            st.altair_chart(
                alt.Chart(df).mark_bar(color='orange').encode(
                    x=alt.X("sentiment_score:O", scale=alt.Scale(domain=[1, 2, 3, 4, 5]), title="Score de sentiment"),
                    y="count()",
                    tooltip=["count()", "sentiment_score"]
                ).properties(width=600),
                use_container_width=True
            )

            st.subheader("📈 Corrélation note / sentiment")
            st.altair_chart(
                alt.Chart(df).mark_circle(size=60).encode(
                    x="rating:Q",
                    y="sentiment_score:Q",
                    tooltip=["rating", "sentiment_score", "confidence"]
                ).interactive(),
                use_container_width=True
            )

            st.metric("🔍 Confiance moyenne du modèle", f"{df['confidence'].mean():.2f}")

            st.subheader("📝 Tableau des critiques")
            st.dataframe(df[["rating", "sentiment_score", "confidence", "review"]])
    else:
        st.info("Aucun film trouvé.")
else:
    st.info("Tape un nom de film pour commencer.")
