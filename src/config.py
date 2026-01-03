# config.py
from pathlib import Path
from dotenv import load_dotenv
import zipfile
from huggingface_hub import hf_hub_download
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BASE_DIR / "chroma_db"
ZIP_PATH = BASE_DIR / "chroma_db.zip"

HF_REPO_ID = "LenaGeller/rag-politics-chroma-db"
HF_FILENAME = "chroma_db.zip"

def ensure_chroma_db():
    # Wenn Ordner schon da ist -> nichts tun
    if CHROMA_DIR.exists() and any(CHROMA_DIR.iterdir()):
        print("✅ ChromaDB already present:", CHROMA_DIR)
        return

    print("⬇️ Downloading ChromaDB from Hugging Face...")
    downloaded_zip = hf_hub_download(
        repo_id=HF_REPO_ID,
        filename=HF_FILENAME,
        repo_type="dataset",
    )

    # Zip an festen Ort kopieren (optional, aber übersichtlich)
    Path(downloaded_zip).replace(ZIP_PATH)

    print("📦 Unzipping...")
    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        z.extractall(BASE_DIR)

    print("✅ ChromaDB ready at:", CHROMA_DIR)

ensure_chroma_db()

# Alte Collection (nicht mehr aktiv genutzt)
ALT_COLLECTION = "langchain"

# Aktive Collection (Projektstandard)
NEU_COLLECTION = "politik_normalized_test"

EMBEDDING_MODEL = "text-embedding-3-large"
CHAT_MODEL = "gpt-5-mini"

TOP_K = 20
TEMPERATURE = 0.1


