"""En-têtes de page — bandeau hero (accueil) et en-têtes de section standard.

Note technique : HTML construit sur une seule ligne (voir kpi_cards.py pour
l'explication détaillée du piège CommonMark/indentation évité par ce choix).
"""

import streamlit as st

from utils.icons import icon_svg


def hero(title, subtitle):
    html = (
        '<div class="tg-hero"><div class="tg-accent-bar"></div>'
        f'<h1>{title}</h1><p>{subtitle}</p></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def page_title(title, question=None, icon=None):
    """En-tête de page standard, avec la question centrale affichée juste en dessous
    (storytelling — cahier des charges Section 28)."""
    icon_html = icon_svg(icon, size=26, color="#1B4332") + " " if icon else ""
    st.markdown(f"## {icon_html}{title}", unsafe_allow_html=True)
    if question:
        html = f'<div class="tg-story-block"><div class="tg-story-label">Question</div>{question}</div>'
        st.markdown(html, unsafe_allow_html=True)
