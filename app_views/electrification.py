"""Page 2/6 — Électrification : mesurer la fracture ville/campagne."""

import streamlit as st

from components.header import page_title
from components.kpi_cards import kpi_row
from components import charts as ch
from components import interpretation as itp
from services import indicators as ind
from utils.constants import ACTUALISATION_ACCES_ELECTRICITE


def render(data):
    page_title(
        "Électrification — Mesurer la fracture ville/campagne",
        question="Quelle est l'ampleur de la fracture entre accès urbain et rural à l'électricité ?",
        icon="bolt",
    )

    elec = ind.get_electricity_series(data["indicators"])
    kpi = ind.kpi_electricite(elec)

    kpi_row([
        dict(label="Accès national", value=f"{kpi['kpi1_national']['valeur_fin']:.1f}", unit=" %",
             year=kpi['kpi1_national']['annee_fin'], source="Banque mondiale (WDI)"),
        dict(label="Accès rural", value=f"{kpi['kpi2_rural']['valeur_fin']:.1f}", unit=" %",
             year=kpi['kpi2_rural']['annee_fin'], source="Banque mondiale (WDI)"),
        dict(label="Accès urbain", value=f"{kpi['kpi3_urbain']['valeur_fin']:.1f}", unit=" %",
             year=kpi['kpi3_urbain']['annee_fin'], source="Banque mondiale (WDI)"),
        dict(label="Gap urbain-rural", value=f"{kpi['kpi4_gap_fin']:.1f}", unit=" pts",
             year=kpi['kpi4_annee_fin'], source="Calculé (WDI)"),
    ])

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Évolution de l'accès à l'électricité")
    annee_min, annee_max = int(elec["urbain"].Year.min()), int(elec["urbain"].Year.max())
    c1, c2 = st.columns([3, 1])
    with c2:
        with st.container(border=True):
            st.markdown('<div class="tg-controls-label">Filtres</div>', unsafe_allow_html=True)
            periode = st.slider("Période", annee_min, annee_max, (annee_min, annee_max), key="elec_periode")
            afficher_national = st.checkbox("Afficher le national", value=True, key="elec_national")
    with c1:
        st.plotly_chart(ch.chart_electrification(elec, periode, afficher_national), width='stretch')

    rural_p = elec["rural"][(elec["rural"].Year >= periode[0]) & (elec["rural"].Year <= periode[1])]
    urbain_p = elec["urbain"][(elec["urbain"].Year >= periode[0]) & (elec["urbain"].Year <= periode[1])]
    if len(rural_p) and len(urbain_p):
        gap_debut = urbain_p.Value.iloc[0] - rural_p.Value.iloc[0]
        gap_fin = urbain_p.Value.iloc[-1] - rural_p.Value.iloc[-1]
        itp.constat(
            f"Accès rural : {rural_p.Value.iloc[0]:.1f}% ({int(rural_p.Year.iloc[0])}) → "
            f"{rural_p.Value.iloc[-1]:.1f}% ({int(rural_p.Year.iloc[-1])}). "
            f"Accès urbain : {urbain_p.Value.iloc[0]:.1f}% → {urbain_p.Value.iloc[-1]:.1f}%. "
            f"Écart ville-campagne : {gap_debut:.1f} pts → {gap_fin:.1f} pts."
        )
    itp.message_cle("La fracture ville/campagne persiste malgré la progression de l'accès rural.")

    st.markdown("#### Actualisation documentée (2023-2025)")
    st.caption("Deux sources, deux méthodologies différentes — non fusionnées (voir note méthodologique).")
    cols = st.columns(len(ACTUALISATION_ACCES_ELECTRICITE))
    for col, entry in zip(cols, ACTUALISATION_ACCES_ELECTRICITE):
        with col:
            st.metric(f"{entry['source']} — {entry['annee']}", f"{entry['national']:.1f} %")
            if "urbain" in entry:
                st.caption(f"Urbain : {entry['urbain']:.1f}% · Rural : {entry['rural']:.1f}%")
    st.caption(
        "Note méthodologique : l'estimation nationale la plus récente est sensiblement plus optimiste que la "
        "dernière valeur WDI (2022), mais son détail urbain est plus bas que le dernier point WDI urbain — signe "
        "de méthodologies distinctes. Aucune valeur n'est présentée comme supérieure à l'autre."
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Fiabilité du réseau")
    fiab = ind.get_fiabilite_series(data["indicators"])
    metrique = st.radio("Indicateur", ["Les deux", "Entreprises touchées", "Pertes financières"],
                         horizontal=True, key="fiab_metrique")
    st.plotly_chart(ch.chart_fiabilite(fiab["pannes"], fiab["pertes"], metrique), width='stretch')
    itp.story_block(
        "Précision sur la définition",
        "« Firms experiencing electrical outages » mesure la part des <b>entreprises formelles</b> interrogées "
        "dans les Enterprise Surveys de la Banque mondiale (dernier point disponible : 2016) — ce n'est pas une "
        "mesure sur les ménages, et ne doit jamais être généralisé à l'ensemble de la population.",
    )
