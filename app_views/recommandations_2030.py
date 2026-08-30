"""Page 6/6 — Recommandations & 2030 : décisions possibles, projections et qualité des données."""

import streamlit as st

from components.header import page_title
from components import charts as ch
from components import interpretation as itp
from services import indicators as ind
from services import forecasting as fc
from services.recommendations import RECOMMANDATIONS, MATRICE_EFFORT_IMPACT
from services.data_loader import inventaire_fichiers
from utils.constants import OBJECTIFS_2030, SOURCE_OBJECTIFS_2030, SOURCES_TABLE


def render(data):
    page_title(
        "Recommandations & 2030",
        question="Quelles actions peuvent être envisagées, et où en sera-t-on à l'horizon 2030 ?",
        icon="checklist",
    )

    tab_reco, tab_2030, tab_qualite = st.tabs(["Recommandations opérationnelles", "Vision 2030 & Machine Learning", "Qualité & méthodologie"])

    # ------------------------------------------------------------------
    # Recommandations
    # ------------------------------------------------------------------
    with tab_reco:
        for bloc in RECOMMANDATIONS:
            st.markdown(f"<div class='tg-axe-title'>{bloc['axe']}</div>", unsafe_allow_html=True)
            itp.enjeu(bloc["enjeu"])
            st.markdown("**Actions**")
            for a in bloc["actions"]:
                st.markdown(f"- {a}")
            c1, c2 = st.columns(2)
            with c1:
                st.caption(f"Cible : {bloc['cible']}")
            with c2:
                st.caption(f"Impact attendu : {bloc['impact_attendu']}")
            st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("#### Priorisation synthétique (matrice effort / impact, qualitative)")
        st.dataframe(
            MATRICE_EFFORT_IMPACT,
            column_config={
                "action": "Action", "effort": "Effort de mise en œuvre",
                "impact": "Impact attendu", "horizon": "Horizon",
            },
            hide_index=True, width='stretch',
        )
        st.caption("Aucun impact quantitatif n'est inventé : cette matrice reste qualitative, telle que formulée dans le notebook.")

    # ------------------------------------------------------------------
    # Vision 2030 & Machine Learning
    # ------------------------------------------------------------------
    with tab_2030:
        itp.projection_notice()
        st.caption(f"Objectifs officiels 2030 : {SOURCE_OBJECTIFS_2030}.")

        elec = ind.get_electricity_series(data["indicators"])
        cuisson = ind.get_cuisson_propre_series(data["indicators"])
        foret = ind.get_foret_series(data["indicators"])

        cibles = {
            "Accès à l'électricité, rural (%)": (elec["rural"].Year.values, elec["rural"].Value.values, (0, 100)),
            "Accès à l'électricité, urbain (%)": (elec["urbain"].Year.values, elec["urbain"].Value.values, (0, 100)),
            "Accès à l'électricité, national (%)": (elec["national"].Year.values, elec["national"].Value.values, (0, 100)),
            "Cuisson propre, rural (%)": (cuisson["rural"].Year.values, cuisson["rural"].Value.values, (0, 100)),
            "Cuisson propre, urbain (%)": (cuisson["urbain"].Year.values, cuisson["urbain"].Value.values, (0, 100)),
            "Superficie forestière (km²)": (foret["area_km2"].Year.values, foret["area_km2"].Value.values, (0, None)),
        }
        objectifs_map = {
            "Accès à l'électricité, rural (%)": OBJECTIFS_2030["acces_electricite_rural"]["valeur"],
            "Accès à l'électricité, urbain (%)": OBJECTIFS_2030["acces_electricite_urbain"]["valeur"],
            "Accès à l'électricité, national (%)": OBJECTIFS_2030["acces_electricite_national"]["valeur"],
            "Cuisson propre, rural (%)": OBJECTIFS_2030["cuisson_propre_rural"]["valeur"],
            "Cuisson propre, urbain (%)": OBJECTIFS_2030["cuisson_propre_urbain"]["valeur"],
            "Superficie forestière (km²)": None,
        }

        resultats_ml = fc.run_all_forecasts(cibles)
        table = fc.table_projection_2030(cibles, resultats_ml, objectifs_map)
        st.markdown("#### Situation observée → tendance → scénario 2030 → objectif → écart")
        st.dataframe(table, hide_index=True, width='stretch')

        st.markdown("#### Détail par indicateur (modèle retenu, MAE, RMSE, R²)")
        noms_indicateurs = list(cibles.keys())
        indicateur_choisi = st.pills(
            "Indicateur", noms_indicateurs, default=noms_indicateurs[0], key="ml_indicateur",
        )
        if not indicateur_choisi:
            # st.pills désélectionne (renvoie None) si on reclique le bouton déjà actif :
            # on retombe alors sur le dernier indicateur valide plutôt que de casser la page.
            indicateur_choisi = st.session_state.get("_dernier_ml_indicateur", noms_indicateurs[0])
        st.session_state["_dernier_ml_indicateur"] = indicateur_choisi
        annees, valeurs, borne = cibles[indicateur_choisi]
        tableau_ml, meilleur = resultats_ml[indicateur_choisi]
        if tableau_ml is None:
            st.info("Série trop courte (moins de 8 points) pour une validation robuste — non modélisée.")
        else:
            st.dataframe(tableau_ml, hide_index=True, width='stretch')
            st.caption(f"Modèle retenu (RMSE de validation la plus faible) : {meilleur}.")
            st.plotly_chart(
                ch.chart_projection(indicateur_choisi, annees, valeurs, tableau_ml, meilleur, objectifs_map.get(indicateur_choisi)),
                width='stretch',
            )
        itp.story_block(
            "Méthodologie",
            "Trois modèles comparés (régression linéaire, Random Forest, Gradient Boosting) par validation "
            "temporelle <i>walk-forward</i> (entraînement sur le passé, test sur les dernières années observées). "
            "Le modèle retenu minimise la RMSE de validation — jamais un choix arbitraire. Les modèles à base "
            "d'arbres ne peuvent pas extrapoler au-delà de la plage observée à l'entraînement.",
        )

    # ------------------------------------------------------------------
    # Qualité & méthodologie
    # ------------------------------------------------------------------
    with tab_qualite:
        st.markdown("#### Inventaire des fichiers sources")
        st.dataframe(inventaire_fichiers(), hide_index=True, width='stretch')

        st.markdown("#### Contrôles de cohérence")
        for j in data["journal"]:
            st.markdown(f"- **{j['étape']}** — {j['détail']}")

        st.markdown("#### Sources et références")
        st.dataframe(
            SOURCES_TABLE,
            column_config={"dataset": "Dataset", "source": "Source", "url": "URL", "annees": "Année(s)"},
            hide_index=True, width='stretch',
        )

        st.markdown("#### Limites et précautions d'interprétation")
        st.markdown(
            """
- Les indicateurs mobilisés couvrent des périodes hétérogènes (2016 à 2022 selon l'indicateur).
- Le bilan GES sectoriel est une année d'inventaire unique (2018) : aucune tendance intersectorielle n'est calculable.
- Le cadastre forestier (53 polygones) est un sous-ensemble du dispositif national d'aires protégées.
- Le graphe de centralité repose sur la seule proximité géographique, pas une connectivité écologique mesurée.
- Les séries de température (2013-2019) sont trop courtes pour une tendance climatique au sens de l'OMM (≥30 ans).
- Les projections 2030 dépendent entièrement des données historiques disponibles et ne sont pas des prévisions officielles.
- L'indice de priorité territoriale utilise un proxy national pour l'accès électrique et la biomasse, faute de données régionalisées.
- Aucune analyse de cette application n'établit de lien de causalité.
            """
        )
