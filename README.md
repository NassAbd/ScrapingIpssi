# 📊 Projet Web Scraping: Abdallah Nassur | Lucas Taranne

Application Python conçue pour rechercher des films via l'API TMDB (The Movie DataBase), récupérer et analyser des critiques depuis Letterboxd, et visualiser les résultats à l'aide de Streamlit.

## 🚀 Fonctionnalités

- Recherche de films en utilisant l'API TMDB.
- Récupération des critiques de films depuis Letterboxd.
- Analyse de sentiment des critiques (avec un modèle IA d'analyse de sentiment).
- Visualisation interactive des données avec Streamlit.

## 🛠️ Installation

1. Clonez le dépôt :

   ```bash
   git clone https://github.com/NassAbd/ScrapingIpssi.git
   cd ScrapingIpssi
   ```

2. Installez les dépendances :

   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Utilisation

1. Assurez-vous d'avoir une clé API TMDB et définissez-la dans un fichier `.env` :

   ```bash
   API_KEY=your_tmdb_api_key
   ```

2. Lancez le serveur fastapi + l'app streamlit :

   ```bash
   python .\run_app.py
   ```

3. Ou lancer séparément :

   ```bash
   uvicorn main:app --reload
   streamlit run code_fusion.py
   ```