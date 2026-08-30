"""Page 3/6 — Biomasse & Carbone : dépendance au bois-énergie, pression forestière, bilan GES."""

import streamlit as st

from components.header import page_title
from components.kpi_cards import kpi_row
from components import charts as ch
from components import interpretation as itp
from services import indicators as ind


def render(data):
    page_title(
        "Biomasse & Carbone",
        question="Quelle dépendance des ménages au bois-énergie/charbon, et quelle contribution du secteur "
                 "énergétique aux émissions comparée aux autres secteurs ?",
        icon="flame",
    )

    # ------------------------------------------------------------------
    # PARTIE A — Biomasse et cuisson
    # ------------------------------------------------------------------
    st.markdown("### Dépendance des ménages à la biomasse")
    comb = ind.get_combustibles_series(data["indicators"])
    biomasse = ind.kpi_biomasse(comb)

    kpi_row([
        dict(label="Bois", value=f"{biomasse['bois_pct']:.1f}", unit=" %", year=biomasse["annee"],
             source="Banque mondiale (WDI)"),
        dict(label="Charbon de bois", value=f"{biomasse['charbon_pct']:.1f}", unit=" %", year=biomasse["annee"],
             source="Banque mondiale (WDI)"),
        dict(label="Gaz (LPG)", value=f"{biomasse['lpg_pct']:.1f}", unit=" %", year=biomasse["annee"],
             source="Banque mondiale (WDI)"),
        dict(label="Bois + charbon (dépendance biomasse)", value=f"{biomasse['biomasse_dep_pct']:.1f}", unit=" %",
             year=biomasse["annee"], source="Calculé (WDI)"),
    ])
    st.caption(
        "Cette ventilation n'existe qu'au niveau national dans les données disponibles : aucune déclinaison "
        "urbain/rural n'est disponible pour ce triplet d'indicateurs."
    )

    selection = st.multiselect("Combustibles affichés", ["Bois", "Charbon de bois", "Gaz (LPG)"],
                                default=["Bois", "Charbon de bois", "Gaz (LPG)"], key="combustibles_sel")
    st.plotly_chart(ch.chart_combustibles(comb, tuple(selection)), width='stretch')

    st.markdown("#### Cuisson propre urbain/rural")
    cuisson = ind.get_cuisson_propre_series(data["indicators"])
    zones = st.multiselect("Zone", ["Urbain", "Rural"], default=["Urbain", "Rural"], key="cuisson_zones")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(ch.chart_cuisson_propre(cuisson, tuple(zones)), width='stretch')
    with c2:
        gap_df = ind.gap_cuisson_propre(cuisson)
        st.plotly_chart(ch.chart_gap_cuisson(gap_df), width='stretch')
    itp.message_cle(
        "En zone rurale, l'accès à une cuisson propre est quasi inexistant et stagnant (moins de 1% depuis au "
        "moins une décennie) : c'est l'angle mort le plus criant du diagnostic."
    )

    st.markdown("---")
    st.markdown("#### Pression sur les ressources forestières")
    foret = ind.get_foret_series(data["indicators"])
    renouv = data["renouvelables"].dropna(subset=["value"]).sort_values("date")
    defor = ind.kpi_deforestation(foret)

    kpi_row([
        dict(label="Superficie forestière initiale", value=f"{defor['foret_initiale']:,.0f}", unit=" km²",
             year=defor["annee_i"], source="Banque mondiale (WDI)"),
        dict(label="Superficie forestière finale", value=f"{defor['foret_finale']:,.0f}", unit=" km²",
             year=defor["annee_f"], source="Banque mondiale (WDI)"),
        dict(label="Perte relative", value=f"{defor['perte_pct']:.1f}", unit=" %",
             year=f"{defor['annee_i']}-{defor['annee_f']}", source="Calculé (WDI)"),
        dict(label="Taux annuel moyen", value=f"{defor['taux_annuel_km2']:,.0f}", unit=" km²/an",
             year=f"{defor['annee_i']}-{defor['annee_f']}", source="Calculé (WDI)"),
    ])
    st.plotly_chart(ch.chart_foret_biomasse(foret["area_km2"], renouv), width='stretch')
    itp.story_block(
        "Relation biomasse — forêts",
        "Les données ne permettent pas d'affirmer que la biomasse <i>provoque</i> la déforestation. On observe "
        "une pression potentielle sur les ressources forestières, cohérente avec la dépendance élevée au "
        "bois-énergie, mais sans corrélation formelle établie entre ces séries (recouvrement temporel "
        "insuffisant entre les jeux de données).",
    )
    st.caption(
        "L'indicateur « renouvelables + combustibles/déchets » mélange biomasse traditionnelle et renouvelables "
        "modernes : il ne doit pas être lu comme un indicateur pur de transition énergétique propre."
    )

    # ------------------------------------------------------------------
    # PARTIE B — Bilan carbone
    # ------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### Bilan carbone")

    tab1, tab2 = st.tabs(["A — CO2 du secteur énergétique", "B — Bilan GES sectoriel (2018)"])

    with tab1:
        co2_e = data["co2_energie"].dropna(subset=["value"]).sort_values("date")
        c_min, c_max = int(co2_e.date.min()), int(co2_e.date.max())
        periode = st.slider("Période", c_min, c_max, (c_min, c_max), key="co2_periode")
        st.plotly_chart(ch.chart_co2_trend(co2_e, periode), width='stretch')
        sub = co2_e[(co2_e.date >= periode[0]) & (co2_e.date <= periode[1])]
        if len(sub) >= 2 and sub["value"].iloc[0] > 0:
            itp.constat(
                f"CO2 secteur énergie : {sub['value'].iloc[0]:.3f} Mt ({sub['date'].iloc[0]}) → "
                f"{sub['value'].iloc[-1]:.3f} Mt ({sub['date'].iloc[-1]}) — "
                f"facteur x{sub['value'].iloc[-1] / sub['value'].iloc[0]:.1f}."
            )

    with tab2:
        tot_national, secteurs_all, annee = ind.ges_secteurs(data["ges_sectoriel"])
        st.markdown(
            f"<div class='tg-notice'>Le bilan GES sectoriel correspond à une année unique ({annee}) : "
            "aucune tendance intersectorielle n'est calculable avec ce jeu de données. Le graphique ci-dessous "
            "compare les secteurs pour cette seule année.</div>",
            unsafe_allow_html=True,
        )
        st.caption(
            "Correction d'unité appliquée : les données sources sont en Gg CO2e (gigagrammes), converties en "
            "Mt CO2e (÷1000) dans toutes les analyses de cette application — jamais mélangées."
        )
        secteurs_choisis = st.multiselect("Secteurs inclus", options=list(secteurs_all["secteur"]),
                                           default=list(secteurs_all["secteur"]), key="ges_secteurs_sel")
        base_pct = st.radio("Base de calcul du %", ["Total national", "Secteurs sélectionnés"],
                             horizontal=True, key="ges_base_pct")
        st.plotly_chart(
            ch.chart_ges_secteurs(secteurs_all, tot_national, annee, secteurs_choisis or list(secteurs_all["secteur"]), base_pct),
            width='stretch',
        )
        part_afat = secteurs_all[secteurs_all["secteur"].str.contains("AFAT")]["part_pct"].values[0]
        itp.message_cle(
            f"Le secteur AFAT (Agriculture, Foresterie et affectation des terres) constitue le principal "
            f"contributeur au bilan d'émissions de GES du Togo ({part_afat:.1f}% du total national, {annee})."
        )
