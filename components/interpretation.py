"""
Blocs courts de storytelling et bandeaux d'avertissement réutilisés sur toutes les pages
(cahier des charges, Section 28 : Question / Donnée / Constat / Enjeu / Action, explications
courtes et précises — jamais un paragraphe par graphique).
"""

import streamlit as st


def story_block(label, text, alert=False):
    css_class = "tg-story-block tg-alert-block" if alert else "tg-story-block"
    st.markdown(
        f'<div class="{css_class}"><div class="tg-story-label">{label}</div>{text}</div>',
        unsafe_allow_html=True,
    )


def constat(text):
    story_block("Constat", text)


def enjeu(text):
    story_block("Enjeu", text)


def message_cle(text):
    story_block("Message clé", text, alert=True)


def projection_notice():
    """Avertissement obligatoire à proximité de toute projection (cahier des charges, Section 26)."""
    st.markdown(
        '<div class="tg-notice">Scénario statistique basé sur les tendances historiques — '
        'ne constitue pas une prévision officielle.</div>',
        unsafe_allow_html=True,
    )


def proxy_notice(text=None):
    """Avertissement obligatoire pour tout proxy / estimation dérivée (cahier des charges, Section 20)."""
    default = "Estimation dérivée — proxy régional, et non mesure directe."
    st.markdown(f'<div class="tg-notice">{text or default}</div>', unsafe_allow_html=True)


def data_year_notice(text):
    """Rappel de l'année des données quand ce n'est pas déjà visible dans le graphique/KPI
    (cahier des charges, Section 7 : ne jamais présenter une ancienne donnée comme actuelle)."""
    st.caption(text)
