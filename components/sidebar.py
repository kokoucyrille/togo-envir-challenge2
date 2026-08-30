"""
Barre latérale — logo institutionnel (rond, en haut) et navigation (gérée nativement
par st.navigation dans app.py). Aucun bloc de bas de barre : la barre latérale s'arrête
au menu de navigation, pour rester sobre et fonctionnelle.

Note sur le placement du logo : `st.logo()` est l'API native Streamlit conçue
précisément pour afficher un logo institutionnel en haut de l'application (coin
supérieur gauche de la page ET de la barre latérale) — c'est la manière la plus
robuste de garantir qu'il apparaît au-dessus du menu de navigation, quel que soit
l'ordre d'appel dans le script (le widget de navigation natif réserve toujours le
haut de la barre latérale). Le logo est affiché en entier (texte inclus, sans
recadrage) avec une petite marge au-dessus ; le cadre (fond blanc, bordure légère)
est assuré par CSS ciblé (voir utils/styles.py, bloc "Logo institutionnel").

Le portrait de l'auteur n'est volontairement pas affiché dans la barre latérale
(présent sur toutes les pages) : il est réservé à la page dédiée "À propos", pour
ne pas alourdir un espace de navigation censé rester sobre et fonctionnel.
"""

import streamlit as st

from utils.constants import LOGO_MINISTERE_PATH


def render_sidebar_top():
    if LOGO_MINISTERE_PATH.exists():
        st.logo(str(LOGO_MINISTERE_PATH), size="large")
