import streamlit as st
import sys
from pathlib import Path

# src-Ordner importierbar machen
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "src"))

from pipeline import frage_stellen


# --- Setup ---
st.set_page_config(page_title="RAG Politik", layout="centered")
st.markdown("### Politik-Analyse")
st.markdown(
    "*RAG-basierte Auswertung von Regierungs- und Parteidokumenten*"
)
st.caption(
    "Beantwortet präzise politische Fragen zu Regierung, SPD und CDU/CSU "
    "ausschließlich auf Basis offizieller Dokumente."
)
# --- Input ---
frage = st.text_input("Deine Frage:")


if st.button("Frage stellen"): 
    if not frage.strip(): 
        st.warning("Bitte gib eine Frage ein.") 
    else: 
        with st.spinner("Antwort wird erzeugt …"): 
            antwort, docs = frage_stellen(frage) 
        
        st.markdown("#### Antwort") 
        st.write(antwort)


        st.markdown("### Quellen & Textstellen")

        for i, d in enumerate(docs, start=1):
            meta = d.metadata or {}

            label = (
                f"Quelle {i}: "
                f"{meta.get('partei', 'regierung')} | "
                f"{meta.get('chapter', '?')} | "
                f"{meta.get('titel', '?')}"
            )

            with st.expander(label):
                
                st.markdown("**Original-Textstelle:**")
                st.write(d.page_content)

 
