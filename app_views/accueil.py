"""Page 1/6 — Accueil : diagnostic exécutif."""

import base64

import streamlit as st

from components.header import hero
from components.kpi_cards import kpi_row
from services import indicators as ind
from services.recommendations import CONSTATS, FIL_CONDUCTEUR
from utils.constants import SOURCE_OBJECTIFS_2030, HERO_IMAGE_PATH


def _image_to_base64(path):
    if not path.exists():
        return None
    return base64.b64encode(path.read_bytes()).decode()


def _banner():
    b64 = _image_to_base64(HERO_IMAGE_PATH)
    if not b64:
        return
    mime = "image/jpeg" if HERO_IMAGE_PATH.suffix.lower() in (".jpg", ".jpeg") else "image/svg+xml"
    st.markdown(
        f'<div class="tg-banner-wrap"><img src="data:{mime};base64,{b64}" '
        'alt="Photo : installation solaire, éoliennes et raccordement au réseau au coucher du soleil, Togo"></div>'
        '<div class="tg-banner-caption">Installation solaire, éoliennes et raccordement au réseau électrique — '
        'village togolais, au coucher du soleil.</div>',
        unsafe_allow_html=True,
    )


def _mini_constats(items):
    rows = "".join(
        '<div class="tg-mini-constat"><div class="tg-mini-dot"></div><div>'
        f'<div class="tg-mini-title">{c["constat"]}</div>'
        f'<div class="tg-mini-sub">{c["donnee"]}</div>'
        '</div></div>'
        for c in items
    )
    st.markdown(rows, unsafe_allow_html=True)


def render(data):
    hero(
        "Diagnostic Énergie, Climat &amp; Forêts du Togo",
        "Plateforme territoriale d'aide à la décision publique — Horizon 2030",
    )

    _banner()

    elec = ind.get_electricity_series(data["indicators"])
    comb = ind.get_combustibles_series(data["indicators"])
    foret = ind.get_foret_series(data["indicators"])
    kpi_elec = ind.kpi_electricite(elec)
    biomasse = ind.kpi_biomasse(comb)
    tot_ges, secteurs_ges, annee_ges = ind.ges_secteurs(data["ges_sectoriel"])
    part_afat = secteurs_ges[secteurs_ges["secteur"].str.contains("AFAT")]["part_pct"].values[0]
    defor = ind.kpi_deforestation(foret)

    st.markdown("#### Indicateurs stratégiques")
    kpi_row([
        dict(label="Accès national électricité", value=f"{kpi_elec['kpi1_national']['valeur_fin']:.1f}", unit=" %",
             year=kpi_elec['kpi1_national']['annee_fin'], source="Banque mondiale (WDI)", icon="bolt"),
        dict(label="Gap urbain-rural", value=f"{kpi_elec['kpi4_gap_fin']:.1f}", unit=" pts",
             year=kpi_elec['kpi4_annee_fin'], source="Calculé (WDI)", icon="distance"),
        dict(label="Dépendance biomasse (bois+charbon)", value=f"{biomasse['biomasse_dep_pct']:.1f}", unit=" %",
             year=biomasse['annee'], source="Banque mondiale (WDI)", icon="flame"),
        dict(label="Part AFAT du bilan GES", value=f"{part_afat:.1f}", unit=" %",
             year=annee_ges, source="Inventaire national GES", icon="cloud"),
        dict(label="Perte forestière", value=f"{defor['taux_annuel_km2']:,.0f}", unit=" km²/an",
             year=f"{defor['annee_i']}-{defor['annee_f']}", source="Banque mondiale (WDI)", icon="forest"),
    ])

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.3, 1], gap="large")
    with col1:
        st.markdown("#### Synthèse exécutive")
        st.write(FIL_CONDUCTEUR)
        st.markdown(
            '<div class="tg-story-block tg-alert-block"><div class="tg-story-label">Message clé</div>'
            "L'électrification rurale par réseau centralisé n'est pas, à elle seule, le levier prioritaire : "
            "le nœud du problème est domestique et rural (cuisson au bois) et territorialement concentré."
            '</div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown("#### Principaux constats")
        _mini_constats(CONSTATS[:4])

