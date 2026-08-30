"""Page 5/6 — Cartographie & Priorisation : quels territoires ou forêts sont prioritaires ?"""

import streamlit as st
from streamlit_folium import st_folium

from components.header import page_title
from components import charts as ch
from components import maps as mp
from components import interpretation as itp
from services import analysis as an
from services import indicators as ind
from utils.constants import REGION_COLORS, VILLES_COORDS, VILLES_ORDRE, SUPERFICIE_REGION_KM2, WDPA_NB_DESIGNATIONS_NATIONALES, WDPA_SOURCE, NB_FORETS_CLASSEES_CADASTRE


def render(data):
    page_title(
        "Cartographie & Priorisation",
        question="Quels territoires ou forêts apparaissent prioritaires selon les indicateurs construits dans le notebook ?",
        icon="map",
    )

    forets = data["forets"]
    coords_m = data["coords_m"]

    st.markdown(
        f"""<div class="tg-notice">Le cadastre exploité contient <b>{NB_FORETS_CLASSEES_CADASTRE} forêts classées
        géoréférencées</b> — un sous-ensemble du dispositif national des aires protégées, pas son inventaire
        exhaustif. Le registre international de référence (Protected Planet / WDPA) recense
        {WDPA_NB_DESIGNATIONS_NATIONALES} désignations nationales pour le Togo ({WDPA_SOURCE}).</div>""",
        unsafe_allow_html=True,
    )

    forets_c, G, eig_ok = an.build_centrality(forets, coords_m, k_voisins=4)
    forets_v = an.add_vulnerabilite_defaut(forets_c)

    tab_carte, tab_centralite, tab_vuln, tab_territorial = st.tabs(
        ["Carte interactive", "Centralité structurelle", "Vulnérabilité & priorisation", "Indice territorial"]
    )

    # ------------------------------------------------------------------
    # Carte interactive
    # ------------------------------------------------------------------
    with tab_carte:
        with st.container(border=True):
            st.markdown('<div class="tg-controls-label">Filtres</div>', unsafe_allow_html=True)
            regions_sel = st.multiselect("Régions", list(REGION_COLORS.keys()), default=list(REGION_COLORS.keys()), key="map_regions")
            c1, c2, c3 = st.columns(3)
            with c1:
                aire_min = st.slider("Aire min (km²)", 0.0, float(forets_v["area_km2"].max()), 0.0, key="map_aire_min")
            with c2:
                vuln_min = st.slider("Vulnérabilité min", 0, 100, 0, step=5, key="map_vuln_min")
            with c3:
                centr_min = st.slider("Centralité min", 0, 100, 0, step=5, key="map_centr_min")

        sub = forets_v[
            forets_v["region_nom_bdd"].isin(regions_sel)
            & (forets_v["area_km2"] >= aire_min)
            & (forets_v["score_vulnerabilite"] >= vuln_min)
            & (forets_v["centralite_score"] >= centr_min)
        ]
        st.caption(f"**{len(sub)}** forêt(s) sur **{len(forets_v)}** correspondent aux filtres sélectionnés.")

        tendances_s = ind.tendances_par_ville(data["temperatures"], VILLES_ORDRE)
        moyennes = data["temperatures"].groupby(["villes", "libellés"])["Value"].mean().unstack().reindex(VILLES_ORDRE)
        top15 = forets_v.sort_values("score_vulnerabilite", ascending=False).head(15)
        top10 = forets_v.sort_values("centralite_score", ascending=False).head(10)

        carte = mp.construire_carte(sub if len(sub) else forets_v, top15, top10, VILLES_COORDS, tendances_s, moyennes)
        st_folium(carte, use_container_width=True, height=560, returned_objects=[])

    # ------------------------------------------------------------------
    # Centralité structurelle
    # ------------------------------------------------------------------
    with tab_centralite:
        itp.story_block(
            "Terminologie",
            "Le graphe mesure une <b>centralité structurelle basée sur la proximité géographique</b> entre les "
            "53 forêts classées — jamais une « centralité écologique ». Il modélise une proximité spatiale, pas "
            "une connectivité écologique mesurée (flux de faune, continuité de couvert végétal).",
        )
        colorer_par = st.radio("Colorer par", ["Région", "Centralité"], horizontal=True, key="reseau_couleur")
        carte_centralite = mp.construire_carte_centralite(forets_v, G, colorer_par)
        st_folium(carte_centralite, use_container_width=True, height=520, returned_objects=[])
        st.caption(
            "Taille et intensité des points proportionnelles à la centralité d'intermédiarité. "
            "Les traits gris relient chaque forêt à ses K=4 plus proches voisines (graphe de proximité géographique)."
        )

        st.markdown("<br>", unsafe_allow_html=True)
        col_top, col_rob = st.columns(2, gap="large")
        with col_top:
            st.markdown("##### Top 8 forêts par centralité d'intermédiarité")
            st.caption("Nœuds de corridor")
            st.dataframe(
                forets_v.nlargest(8, "centralite_intermediarite")[
                    ["etab_nom", "region_nom_bdd", "centralite_intermediarite", "centralite_score"]
                ].rename(columns={"etab_nom": "Forêt", "region_nom_bdd": "Région",
                                   "centralite_intermediarite": "Intermédiarité (brute)", "centralite_score": "Score (0-100)"}),
                hide_index=True, width='stretch', height=320,
            )
        with col_rob:
            st.markdown("##### Test de robustesse (K = 3 à 6)")
            st.caption("Plus proches voisins")
            rob = an.robustesse_k(forets_v, coords_m)
            st.dataframe(
                rob.head(10)[["nom", "region", "rang_K=3", "rang_K=4", "rang_K=5", "rang_K=6", "score_robuste", "ecart_type_rang"]]
                .rename(columns={"nom": "Forêt", "region": "Région", "score_robuste": "Score robuste", "ecart_type_rang": "Écart-type de rang"}),
                hide_index=True, width='stretch', height=320,
            )
        itp.constat(
            "Un faible écart-type de rang signale une forêt dont l'importance structurelle ne dépend pas du "
            "choix arbitraire de K — ce sont les candidates les plus solides pour une priorisation opérationnelle."
        )

    # ------------------------------------------------------------------
    # Vulnérabilité & priorisation
    # ------------------------------------------------------------------
    with tab_vuln:
        itp.proxy_notice(
            "L'indice de vulnérabilité est un indice de priorisation / proxy (taille + date de création inconnue "
            "+ centralité), pas une mesure absolue du risque écologique."
        )
        with st.container(border=True):
            st.markdown('<div class="tg-controls-label">Pondération de l\'indice</div>', unsafe_allow_html=True)
            w1, w2, w3 = st.columns(3)
            with w1:
                w_taille = st.slider("Poids taille", 0, 100, 60, step=5, key="vuln_w_taille")
            with w2:
                w_date = st.slider("Poids date inconnue", 0, 100, 40, step=5, key="vuln_w_date")
            with w3:
                w_centralite = st.slider("Poids centralité", 0, 100, 0, step=5, key="vuln_w_centr")

        score, _, _ = an.calcul_priorite_foret(forets_v, w_taille, w_date, w_centralite)
        forets_v = forets_v.copy()
        forets_v["score_vulnerabilite"] = score

        colorer_matrice = st.radio("Colorer la matrice par", ["Région", "Superficie"], horizontal=True, key="matrice_couleur")
        st.plotly_chart(ch.chart_matrice_priorisation(forets_v, colorer_matrice), width='stretch')

        med_x, med_y = forets_v["centralite_score"].median(), forets_v["score_vulnerabilite"].median()
        urgence = forets_v[(forets_v["centralite_score"] >= med_x) & (forets_v["score_vulnerabilite"] >= med_y)]
        itp.constat(f"Forêts en zone « URGENCE CORRIDOR » (vulnérables ET centrales) : {len(urgence)}.")
        st.dataframe(
            urgence[["etab_nom", "region_nom_bdd", "area_km2", "score_vulnerabilite", "centralite_score"]]
            .sort_values("score_vulnerabilite", ascending=False)
            .rename(columns={"etab_nom": "Forêt", "region_nom_bdd": "Région", "area_km2": "Aire (km²)",
                              "score_vulnerabilite": "Vulnérabilité", "centralite_score": "Centralité"}),
            hide_index=True, width='stretch',
        )

    # ------------------------------------------------------------------
    # Indice de priorité territoriale (régional)
    # ------------------------------------------------------------------
    with tab_territorial:
        itp.proxy_notice(
            "L'accès régional à l'électricité n'est pas une mesure directement observée. Cette estimation est "
            "dérivée du différentiel national urbain/rural appliqué uniformément aux régions — un proxy, pas "
            "une mesure directe de l'accès à l'électricité par région."
        )
        elec = ind.get_electricity_series(data["indicators"])
        comb = ind.get_combustibles_series(data["indicators"])
        biomasse = ind.kpi_biomasse(comb)

        with st.expander("Ajuster la pondération des critères", expanded=False):
            r1c1, r1c2, r1c3 = st.columns(3)
            with r1c1:
                w_vuln = st.slider("Poids vulnérab.", 0, 100, 30, step=5, key="terr_w_vuln")
            with r1c2:
                w_couv = st.slider("Poids couverture", 0, 100, 25, step=5, key="terr_w_couv")
            with r1c3:
                w_centr = st.slider("Poids centralité", 0, 100, 20, step=5, key="terr_w_centr")
            r2c1, r2c2 = st.columns(2)
            with r2c1:
                w_biomasse = st.slider("Poids biomasse", 0, 100, 15, step=5, key="terr_w_biomasse")
            with r2c2:
                w_elec = st.slider("Poids accès élec.", 0, 100, 10, step=5, key="terr_w_elec")

        reg_stats = an.indice_priorite_territoriale(
            forets_v, elec["national"].Value.iloc[-1], biomasse["biomasse_dep_pct"], SUPERFICIE_REGION_KM2,
            w_vuln, w_couv, w_centr, w_biomasse, w_elec,
        )
        poids_txt = f"poids : {w_vuln}% vulnérab. · {w_couv}% faible couverture · {w_centr}% centralité · {w_biomasse}% biomasse · {w_elec}% accès élec."
        st.plotly_chart(ch.chart_priorite_territoriale(reg_stats, poids_txt), width='stretch')

        st.dataframe(
            reg_stats[["vulnerabilite_moyenne", "couverture_protegee_pct", "centralite_moyenne", "indice_priorite"]]
            .rename(columns={"vulnerabilite_moyenne": "Vulnérabilité moyenne", "couverture_protegee_pct": "Couverture protégée (%)",
                              "centralite_moyenne": "Centralité moyenne", "indice_priorite": "Indice de priorité"})
            .round(2),
            width='stretch',
        )
        itp.message_cle(
            f"{reg_stats.index[0]} ressort en tête de l'indice de priorité territoriale, malgré un nombre de "
            "forêts classées parfois élevé — du fait de sa très faible couverture rapportée à sa superficie "
            "régionale, et non d'un simple décompte de forêts."
        )
