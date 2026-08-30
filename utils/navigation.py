"""
Construction centralisée des objets st.Page — un seul point de vérité pour la liste
des pages, utilisé par app.py pour construire le menu via st.navigation. La bascule
programmatique (boutons d'accès rapide) se fait via utils.nav_state.switch_to, qui ne
dépend pas de ce module (évite tout import circulaire avec app_views).

La navigation est groupée en deux sections ("Analyse" et "Informations") via le mode
dict natif de st.navigation : cela sépare visuellement les six pages d'analyse de la
page "À propos" (identité de l'auteur, cadre méthodologique), pour une hiérarchie de
navigation plus claire.
"""

from functools import partial

import streamlit as st

from app_views import (
    accueil, electrification, biomasse_carbone, climatologie,
    cartographie_priorisation, recommandations_2030, a_propos,
)

PAGE_DEFS = [
    ("accueil", accueil, "Accueil", ":material/home:"),
    ("electrification", electrification, "Électrification", ":material/bolt:"),
    ("biomasse_carbone", biomasse_carbone, "Biomasse & Carbone", ":material/local_fire_department:"),
    ("climatologie", climatologie, "Climatologie", ":material/thermostat:"),
    ("cartographie_priorisation", cartographie_priorisation, "Cartographie & Priorisation", ":material/map:"),
    ("recommandations_2030", recommandations_2030, "Recommandations & 2030", ":material/checklist:"),
]

INFO_PAGE_DEFS = [
    ("a_propos", a_propos, "À propos", ":material/info:"),
]


def build_pages(data):
    """Retourne un dict {section: [st.Page, ...]} prêt pour st.navigation, et dépose
    aussi un dict plat {clé: st.Page} dans st.session_state pour que les pages
    puissent l'utiliser avec utils.nav_state.switch_to (boutons d'accès rapide)."""
    flat = {}

    analyse_pages = []
    for i, (key, module, title, icon) in enumerate(PAGE_DEFS):
        p = st.Page(partial(module.render, data), title=title, icon=icon,
                    url_path=key, default=(i == 0))
        flat[key] = p
        analyse_pages.append(p)

    info_pages = []
    for key, module, title, icon in INFO_PAGE_DEFS:
        p = st.Page(partial(module.render, data), title=title, icon=icon, url_path=key)
        flat[key] = p
        info_pages.append(p)

    st.session_state["_nav_pages"] = flat
    return {"Analyse": analyse_pages, "Informations": info_pages}
