"""
Analyse par graphes (centralité structurelle de proximité géographique), indice de
vulnérabilité par forêt, matrice de priorisation, et indice de priorité territoriale
régional — logique reprise à l'identique du notebook de référence (Sections 9 à 11 et 16).

Terminologie obligatoire (cahier des charges, Section 18) : on parle de « centralité
structurelle basée sur la proximité géographique », jamais de « centralité écologique ».
Le graphe modélise une proximité spatiale entre les 53 forêts classées, pas une
connectivité écologique mesurée.
"""

import numpy as np
import pandas as pd
import networkx as nx
import streamlit as st
from scipy.spatial import cKDTree


def calculate_centrality(forets_df, coords_m, k_voisins):
    """Construit le graphe de proximité à k voisins et renvoie les indices de centralité
    (degré, intermédiarité, proximité) — identique au notebook (calculate_centrality())."""
    tree_ = cKDTree(coords_m)
    dist_, idx_ = tree_.query(coords_m, k=k_voisins + 1)
    Gk = nx.Graph()
    for i in range(len(forets_df)):
        Gk.add_node(i)
    for i in range(len(forets_df)):
        for pos in range(1, k_voisins + 1):
            j = int(idx_[i, pos])
            d_km = dist_[i, pos] / 1000
            if d_km > 0:
                Gk.add_edge(i, j, distance_km=d_km)
    deg = nx.degree_centrality(Gk)
    btw = nx.betweenness_centrality(Gk, weight="distance_km", normalized=True)
    clo = nx.closeness_centrality(Gk, distance="distance_km")
    return Gk, deg, btw, clo


@st.cache_data(show_spinner="Calcul du graphe de proximité et de la centralité...")
def build_centrality(_forets, _coords_m, k_voisins=4):
    """Graphe par défaut K=4 (notebook, cellule 50) : degré, intermédiarité, proximité,
    score percentile, et eigenvector centrality (si convergence)."""
    forets = _forets.copy()
    G, deg_c, btw_c, close_c = calculate_centrality(forets, _coords_m, k_voisins)
    forets["centralite_degre"] = forets.index.map(deg_c)
    forets["centralite_intermediarite"] = forets.index.map(btw_c)
    forets["centralite_proximite"] = forets.index.map(close_c)
    forets["centralite_score"] = (forets["centralite_intermediarite"].rank(pct=True) * 100).round(1)
    try:
        eig_c = nx.eigenvector_centrality(G, weight="distance_km", max_iter=1000)
        forets["centralite_eigenvector"] = forets.index.map(eig_c)
        eig_ok = True
    except nx.PowerIterationFailedConvergence:
        eig_ok = False
    return forets, G, eig_ok


@st.cache_data(show_spinner="Test de robustesse du graphe (K=3 à 6)...")
def robustesse_k(_forets, _coords_m):
    """Test de robustesse K=3,4,5,6 (notebook, cellule 53) : rang percentile moyen +
    écart-type de rang par forêt, pour identifier les zones structurellement stables."""
    resultats_k = {}
    for k in [3, 4, 5, 6]:
        _, _, btw_k, _ = calculate_centrality(_forets, _coords_m, k)
        resultats_k[k] = pd.Series(btw_k)
    robustesse_df = pd.DataFrame(resultats_k)
    robustesse_df.columns = [f"K={k}" for k in [3, 4, 5, 6]]
    robustesse_df["nom"] = _forets["etab_nom"].values
    robustesse_df["region"] = _forets["region_nom_bdd"].values
    for k in [3, 4, 5, 6]:
        robustesse_df[f"rang_K={k}"] = robustesse_df[f"K={k}"].rank(pct=True) * 100
    cols_rang = [f"rang_K={k}" for k in [3, 4, 5, 6]]
    robustesse_df["score_robuste"] = robustesse_df[cols_rang].mean(axis=1)
    robustesse_df["ecart_type_rang"] = robustesse_df[cols_rang].std(axis=1)
    return robustesse_df.sort_values("score_robuste", ascending=False)


def calcul_priorite_foret(forets, w_taille=60, w_date=40, w_centralite=0):
    """Score de vulnérabilité par forêt (notebook, cellule 56) : pondération taille +
    date de création inconnue + centralité (modifiable par l'utilisateur)."""
    risque_taille = 1 - forets["area_km2"].rank(pct=True)
    date_inconnue = forets["etab_creation_date"].isin(["Nsp", "Nps", "Jadis"]).astype(int)
    total = max(w_taille + w_date + w_centralite, 1)
    score = (w_taille * risque_taille * 100 + w_date * date_inconnue * 100 +
             w_centralite * forets["centralite_score"]) / total
    return score.round(1), risque_taille, date_inconnue


@st.cache_data(show_spinner=False)
def add_vulnerabilite_defaut(_forets):
    """Ajoute le score de vulnérabilité par défaut (60% taille, 40% date inconnue, 0% centralité) —
    pondération de référence utilisée dans tout le reste du notebook."""
    forets = _forets.copy()
    forets["risque_taille"] = 1 - forets["area_km2"].rank(pct=True)
    forets["date_inconnue"] = forets["etab_creation_date"].isin(["Nsp", "Nps", "Jadis"]).astype(int)
    score, _, _ = calcul_priorite_foret(forets, 60, 40, 0)
    forets["score_vulnerabilite"] = score
    return forets


def indice_priorite_territoriale(forets, elec_national_dernier, biomasse_dep_pct, superficie_region_km2,
                                  w_vuln=30, w_couv=25, w_centr=20, w_biomasse=15, w_elec=10):
    """Indice de priorité territoriale régional (notebook, cellule 75) — combine des variables
    mesurées régionalement (vulnérabilité et centralité moyennes par forêt, couverture protégée)
    avec un PROXY national appliqué uniformément (accès électrique, dépendance biomasse), faute de
    données régionalisées pour ces deux dimensions. Voir avertissement affiché dans l'application."""
    reg_stats = forets.groupby("region_nom_bdd").agg(
        vulnerabilite_moyenne=("score_vulnerabilite", "mean"),
        centralite_moyenne=("centralite_score", "mean"),
        superficie_protegee_km2=("area_km2", "sum"),
    )
    reg_stats["superficie_region_km2"] = reg_stats.index.map(superficie_region_km2)
    reg_stats["couverture_protegee_pct"] = reg_stats["superficie_protegee_km2"] / reg_stats["superficie_region_km2"] * 100
    reg_stats["acces_elec_national_pct"] = elec_national_dernier
    reg_stats["biomasse_dependance_pct"] = biomasse_dep_pct

    def normaliser(s, inverser=False):
        if s.max() == s.min():
            return pd.Series(50.0, index=s.index)
        n = (s - s.min()) / (s.max() - s.min()) * 100
        return 100 - n if inverser else n

    reg_stats["n_vulnerabilite"] = normaliser(reg_stats["vulnerabilite_moyenne"])
    reg_stats["n_faible_couverture"] = normaliser(reg_stats["couverture_protegee_pct"], inverser=True)
    reg_stats["n_centralite"] = normaliser(reg_stats["centralite_moyenne"])
    reg_stats["n_biomasse"] = normaliser(pd.Series([reg_stats["biomasse_dependance_pct"].iloc[0]] * len(reg_stats), index=reg_stats.index))
    reg_stats["n_faible_acces_elec"] = normaliser(pd.Series([100 - reg_stats["acces_elec_national_pct"].iloc[0]] * len(reg_stats), index=reg_stats.index))

    total = max(w_vuln + w_couv + w_centr + w_biomasse + w_elec, 1)
    reg_stats["indice_priorite"] = ((w_vuln * reg_stats["n_vulnerabilite"] + w_couv * reg_stats["n_faible_couverture"] +
                                      w_centr * reg_stats["n_centralite"] + w_biomasse * reg_stats["n_biomasse"] +
                                      w_elec * reg_stats["n_faible_acces_elec"]) / total).round(1)
    return reg_stats.sort_values("indice_priorite", ascending=False)
