import subprocess
import time
import requests
import threading

def start_fastapi():
    print("🚀 Lancement du serveur FastAPI...")
    subprocess.Popen(["uvicorn", "main:app", "--reload"])

def wait_for_api(url, timeout=30):
    print("⏳ Attente de la disponibilité de l'API...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("✅ API FastAPI disponible.")
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    print("❌ Timeout : l'API FastAPI n'est pas disponible.")
    return False

def start_streamlit():
    print("🌐 Lancement de l'interface Streamlit...")
    subprocess.run(["streamlit", "run", "code_fusion.py"])

if __name__ == "__main__":
    thread = threading.Thread(target=start_fastapi)
    thread.start()

    if wait_for_api("http://localhost:8000/ping"):
        start_streamlit()
    else:
        print("💥 Échec : l'interface Streamlit ne sera pas lancée.")
