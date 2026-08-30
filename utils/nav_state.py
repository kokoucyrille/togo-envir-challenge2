"""
Bascule de page (st.switch_page) sans dépendance vers app_views, pour éviter tout
import circulaire avec les pages elles-mêmes (qui appellent switch_to() depuis leurs
boutons d'accès rapide). La liste réelle des st.Page est construite par
utils/navigation.py et déposée dans st.session_state par app.py.
"""

import streamlit as st


def switch_to(page_key):
    pages = st.session_state.get("_nav_pages")
    if pages and page_key in pages:
        st.switch_page(pages[page_key])
