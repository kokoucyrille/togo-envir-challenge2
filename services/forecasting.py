"""
Machine Learning et projections 2030 — méthodologie reprise à l'identique du notebook
de référence (Sections 13-14) : 3 modèles comparés par validation temporelle
walk-forward, sélection du modèle minimisant la RMSE de validation (jamais un choix
arbitraire), projection bornée pour les indicateurs en %.

Rappel obligatoire (cahier des charges, Section 26) : toute projection est un scénario
statistique, pas une prévision officielle. Les modèles à base d'arbres ne peuvent pas
extrapoler au-delà de la plage observée à l'entraînement.
"""

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from utils.constants import OBJECTIFS_2030


def build_forecast(annees, valeurs, annee_cible=2030, borne=None, test_frac=0.2, min_test=3):
    """Identique au notebook : compare régression linéaire / Random Forest / Gradient Boosting
    par validation walk-forward, projette `annee_cible`. Retourne (tableau, meilleur_modele)
    ou (None, None) si la série est trop courte (<8 points)."""
    X = np.asarray(annees, dtype=float).reshape(-1, 1)
    y = np.asarray(valeurs, dtype=float)
    n = len(y)
    if n < 8:
        return None, None
    n_test = max(min_test, int(round(n * test_frac)))
    n_train = n - n_test
    Xtr, Xte = X[:n_train], X[n_train:]
    ytr, yte = y[:n_train], y[n_train:]

    modeles = {
        "Régression linéaire": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=300, random_state=42, max_depth=4),
        "Gradient Boosting": GradientBoostingRegressor(random_state=42, n_estimators=200, max_depth=2, learning_rate=0.05),
    }
    lignes = []
    for nom, modele in modeles.items():
        modele.fit(Xtr, ytr)
        pred_test = modele.predict(Xte)
        mae = mean_absolute_error(yte, pred_test)
        rmse = np.sqrt(mean_squared_error(yte, pred_test))
        r2 = r2_score(yte, pred_test) if n_test >= 2 else np.nan
        modele.fit(X, y)
        pred_brute = float(modele.predict([[annee_cible]])[0])
        pred_bornee = float(np.clip(pred_brute, borne[0], borne[1])) if borne else pred_brute
        lignes.append({
            "Modèle": nom, "MAE (validation)": round(mae, 3), "RMSE (validation)": round(rmse, 3),
            "R² (validation)": round(r2, 3), f"Projection brute {annee_cible}": round(pred_brute, 2),
            f"Projection retenue {annee_cible}": round(pred_bornee, 2),
        })
    tableau = pd.DataFrame(lignes)
    meilleur = tableau.sort_values("RMSE (validation)").iloc[0]["Modèle"]
    return tableau, meilleur


@st.cache_data(show_spinner="Entraînement et validation des modèles ML...")
def run_all_forecasts(_cibles):
    """`_cibles` : dict {nom: (années, valeurs, borne)}. Retourne {nom: (tableau, meilleur)}."""
    resultats = {}
    for nom, (annees, valeurs, borne) in _cibles.items():
        resultats[nom] = build_forecast(annees, valeurs, annee_cible=2030, borne=borne)
    return resultats


def table_projection_2030(cibles_series, resultats_ml, objectifs_map):
    """Assemble le tableau Indicateur | Dernière valeur | Année | Projection 2030 | Objectif | Gap
    (notebook, cellule 70). `objectifs_map` : dict nom -> valeur objectif ou None."""
    lignes = []
    for nom, (annees, valeurs, borne) in cibles_series.items():
        tableau, meilleur = resultats_ml.get(nom, (None, None))
        if tableau is None:
            lignes.append({
                "Indicateur": nom, "Dernière valeur observée": None, "Année": None,
                "Modèle retenu": "Série trop courte (<8 points)", "Projection 2030": None,
                "Objectif officiel 2030": objectifs_map.get(nom), "Gap objectif − projection": None,
            })
            continue
        ligne_meilleure = tableau[tableau["Modèle"] == meilleur].iloc[0]
        derniere_valeur = valeurs[-1]
        derniere_annee = int(annees[-1])
        proj_2030 = ligne_meilleure["Projection retenue 2030"]
        objectif = objectifs_map.get(nom)
        lignes.append({
            "Indicateur": nom, "Dernière valeur observée": round(derniere_valeur, 1), "Année": derniere_annee,
            "Modèle retenu": meilleur, "Projection 2030": proj_2030,
            "Objectif officiel 2030": objectif, "Gap objectif − projection": round(objectif - proj_2030, 1) if objectif is not None else None,
        })
    return pd.DataFrame(lignes)
