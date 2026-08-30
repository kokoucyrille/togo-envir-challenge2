"""
DIAGNOSTIC ÉNERGIE, CLIMAT & FORÊTS DU TOGO
Plateforme territoriale d'aide à la décision publique — Horizon 2030.

Point d'entrée. Source de vérité analytique unique : le notebook
Analyse_Energie_Climat_Forets_Togo_REVISE.ipynb (voir README.md).
"""

import streamlit as st

from components.sidebar import render_sidebar_top
from utils.styles import inject_css
from utils.navigation import build_pages
from services.data_loader import load_all_data

st.set_page_config(
    page_title="Diagnostic Énergie, Climat & Forêts du Togo",
    page_icon=":material/eco:",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
data = load_all_data()

render_sidebar_top()

# Navigation native Streamlit (st.navigation) : un seul point de vérité pour le menu,
# ce qui évite tout doublon avec un éventuel menu auto-détecté à partir d'un dossier
# "pages/" — ce projet utilise volontairement "app_views/" pour cette raison.
pages = build_pages(data)
current_page = st.navigation(pages, position="sidebar")

current_page.run()
