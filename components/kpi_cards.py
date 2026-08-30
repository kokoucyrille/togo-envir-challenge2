"""
Cartes KPI — chaque KPI affiche systématiquement libellé + valeur + unité + année +
source (cahier des charges, Sections 7 et 29). Pas d'emoji ; icônes SVG intégrées.

Rendu en grille CSS (voir .tg-kpi-grid dans utils/styles.py) plutôt qu'en colonnes
Streamlit natives (st.columns) : une grille `auto-fit` fait passer les cartes à la
ligne sur écran étroit au lieu de les comprimer jusqu'à l'illisible, ce qui est
l'essentiel du gain d'ergonomie/fluidité recherché sur les pages à 4-5 KPI.

Note technique : le HTML de la grille entière est construit en une seule chaîne,
sur une seule "ligne logique" par carte (pas de saut de ligne au milieu d'un bloc
HTML brut) : Streamlit/CommonMark interprète tout contenu indenté de 4+ espaces
comme un bloc de code dès qu'une ligne vide apparaît au milieu d'un bloc HTML brut
(ce qui arrive dès qu'un champ optionnel — ex. `delta` — est vide) ; rester sur une
seule ligne par carte élimine ce risque.
"""

import streamlit as st

from utils.icons import icon_svg


def _card_html(label, value, unit="", year=None, source=None, icon=None, delta=None):
    meta_parts = []
    if year is not None:
        meta_parts.append(str(year))
    if source:
        meta_parts.append(source)
    meta = " — ".join(meta_parts)

    icon_html = (
        f'<div class="tg-kpi-icon-badge">{icon_svg(icon, size=16, color="#1B4332")}</div>'
        if icon else ""
    )
    delta_html = f'<div class="tg-kpi-delta">{delta}</div>' if delta else ""

    return (
        '<div class="tg-kpi-card">'
        '<div>'
        f'<div class="tg-kpi-top">{icon_html}<div class="tg-kpi-label">{label}</div></div>'
        f'<div class="tg-kpi-value">{value}{unit}</div>'
        f'{delta_html}'
        '</div>'
        f'<div class="tg-kpi-meta">{meta}</div>'
        '</div>'
    )


def kpi_card(label, value, unit="", year=None, source=None, icon=None, delta=None):
    """Affiche une carte KPI unique, dans sa propre grille à une colonne."""
    html = f'<div class="tg-kpi-grid">{_card_html(label, value, unit, year, source, icon, delta)}</div>'
    st.markdown(html, unsafe_allow_html=True)


def kpi_row(cards):
    """`cards` : liste de dicts avec les clés de kpi_card(). Affiche une grille
    responsive (auto-fit) contenant toutes les cartes — un seul appel st.markdown."""
    cards_html = "".join(_card_html(**c) for c in cards)
    st.markdown(f'<div class="tg-kpi-grid">{cards_html}</div>', unsafe_allow_html=True)
