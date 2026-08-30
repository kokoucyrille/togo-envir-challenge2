"""
KPI et indicateurs calculés — logique reprise à l'identique du notebook de référence.
Chaque fonction correspond à une cellule précise du notebook (indiquée en commentaire).
Aucune valeur n'est codée en dur : tout est recalculé depuis les DataFrames chargés par
services/data_loader.py, pour garantir que l'application reproduit exactement les résultats
du notebook (Règle 2 et 6 du cahier des charges).
"""

import numpy as np
import pandas as pd
import streamlit as st

from services.data_loader import get_series
from utils.constants import (
    IND_ACCES_NATIONAL, IND_ACCES_RURAL, IND_ACCES_URBAIN,
    IND_OUTAGES_FIRMES, IND_PERTE_VENTES_OUTAGES,
    IND_BOIS, IND_CHARBON, IND_LPG,
    IND_CUISSON_PROPRE_RURAL, IND_CUISSON_PROPRE_URBAIN, IND_CUISSON_PROPRE_NATIONAL,
    IND_FORET_KM2, IND_FORET_PCT,
    SUPERFICIE_REGION_KM2,
)


@st.cache_data(show_spinner=False)
def get_electricity_series(_indicators):
    """Séries d'accès à l'électricité (notebook, cellule 13)."""
    return {
        "rural": get_series(_indicators, IND_ACCES_RURAL),
        "urbain": get_series(_indicators, IND_ACCES_URBAIN),
        "national": get_series(_indicators, IND_ACCES_NATIONAL),
    }


@st.cache_data(show_spinner=False)
def get_fiabilite_series(_indicators):
    """Fiabilité réseau — proxy entreprises (notebook, cellule 17)."""
    return {
        "pannes": get_series(_indicators, IND_OUTAGES_FIRMES),
        "pertes": get_series(_indicators, IND_PERTE_VENTES_OUTAGES),
    }


@st.cache_data(show_spinner=False)
def get_combustibles_series(_indicators):
    """Combustibles de cuisson (notebook, cellule 21)."""
    return {
        "bois": get_series(_indicators, IND_BOIS),
        "charbon": get_series(_indicators, IND_CHARBON),
        "lpg": get_series(_indicators, IND_LPG),
    }


@st.cache_data(show_spinner=False)
def get_cuisson_propre_series(_indicators):
    """Cuisson propre urbain/rural (notebook, cellule 24)."""
    return {
        "rural": get_series(_indicators, IND_CUISSON_PROPRE_RURAL),
        "urbain": get_series(_indicators, IND_CUISSON_PROPRE_URBAIN),
        "national": get_series(_indicators, IND_CUISSON_PROPRE_NATIONAL),
    }


@st.cache_data(show_spinner=False)
def get_foret_series(_indicators):
    """Superficie forestière (notebook, cellule 27)."""
    return {
        "area_km2": get_series(_indicators, IND_FORET_KM2),
        "pct_land": get_series(_indicators, IND_FORET_PCT),
    }


def calculate_kpis(series, label, unit=""):
    """Identique au notebook : première/dernière valeur, delta, taux annuel moyen."""
    s = series.dropna(subset=["Value"]).sort_values("Year")
    if len(s) < 2:
        return {"indicateur": label, "unite": unit, "n": len(s)}
    v0, v1 = s["Value"].iloc[0], s["Value"].iloc[-1]
    y0, y1 = int(s["Year"].iloc[0]), int(s["Year"].iloc[-1])
    duree = max(y1 - y0, 1)
    return {
        "indicateur": label, "valeur_debut": round(v0, 2), "annee_debut": y0,
        "valeur_fin": round(v1, 2), "annee_fin": y1, "unite": unit,
        "delta_absolu": round(v1 - v0, 2), "taux_annuel_moyen": round((v1 - v0) / duree, 3),
    }


def kpi_electricite(elec):
    """KPI 1 à 5 — accès électricité (notebook, cellule 15)."""
    rural, urbain, national = elec["rural"], elec["urbain"], elec["national"]
    gap_debut = urbain.Value.iloc[0] - rural.Value.iloc[0]
    gap_fin = urbain.Value.iloc[-1] - rural.Value.iloc[-1]
    prog_annuelle = (national.Value.iloc[-1] - national.Value.iloc[0]) / (national.Year.iloc[-1] - national.Year.iloc[0])
    return {
        "kpi1_national": calculate_kpis(national, "Taux national d'accès à l'électricité", "%"),
        "kpi2_rural": calculate_kpis(rural, "Taux rural", "%"),
        "kpi3_urbain": calculate_kpis(urbain, "Taux urbain", "%"),
        "kpi4_gap_debut": gap_debut, "kpi4_gap_fin": gap_fin,
        "kpi4_annee_debut": int(rural.Year.iloc[0]), "kpi4_annee_fin": int(rural.Year.iloc[-1]),
        "kpi5_progression_annuelle": prog_annuelle,
    }


def kpi_biomasse(combustibles):
    """Indice de dépendance à la biomasse (bois+charbon), niveau national (notebook, cellule 23)."""
    wood, charcoal, lpg = combustibles["bois"], combustibles["charbon"], combustibles["lpg"]
    annees_communes = sorted(set(wood.Year) & set(charcoal.Year))
    if not annees_communes:
        return None
    annee_ref = annees_communes[-1]
    w = wood.set_index("Year").loc[annee_ref, "Value"]
    c = charcoal.set_index("Year").loc[annee_ref, "Value"]
    g = lpg.set_index("Year").loc[annee_ref, "Value"] if annee_ref in set(lpg.Year) else np.nan
    return {"annee": int(annee_ref), "bois_pct": w, "charbon_pct": c, "lpg_pct": g, "biomasse_dep_pct": w + c}


def gap_cuisson_propre(cuisson):
    """Gap de cuisson propre urbain/rural, série temporelle (notebook, cellule 25)."""
    clean_urban, clean_rural = cuisson["urbain"], cuisson["rural"]
    annees_communes = sorted(set(clean_urban.Year) & set(clean_rural.Year))
    df = pd.DataFrame({
        "Year": annees_communes,
        "Urbain": clean_urban.set_index("Year").loc[annees_communes, "Value"].values,
        "Rural": clean_rural.set_index("Year").loc[annees_communes, "Value"].values,
    })
    df["Gap"] = df["Urbain"] - df["Rural"]
    return df


def kpi_deforestation(foret):
    """Formules explicites de déforestation (notebook, cellule 29)."""
    fa = foret["area_km2"].sort_values("Year")
    foret_initiale, annee_i = fa["Value"].iloc[0], int(fa["Year"].iloc[0])
    foret_finale, annee_f = fa["Value"].iloc[-1], int(fa["Year"].iloc[-1])
    perte_km2 = foret_initiale - foret_finale
    perte_pct = perte_km2 / foret_initiale * 100
    duree_ans = annee_f - annee_i
    taux_annuel = perte_km2 / duree_ans
    return {
        "foret_initiale": foret_initiale, "annee_i": annee_i, "foret_finale": foret_finale, "annee_f": annee_f,
        "perte_km2": perte_km2, "perte_pct": perte_pct, "duree_ans": duree_ans, "taux_annuel_km2": taux_annuel,
    }


def ges_secteurs(ges_sectoriel):
    """Bilan GES par secteur, année unique (notebook, cellule 32) + vérification de cohérence."""
    tot_national = ges_sectoriel[(ges_sectoriel.secteur == "Total") & (ges_sectoriel.type == "Total")].Value.values[0]
    secteurs_all = ges_sectoriel[(ges_sectoriel.type == "Total") & (ges_sectoriel.secteur != "Total")].copy()
    secteurs_all["part_pct"] = secteurs_all["Value"] / tot_national * 100
    annee = int(ges_sectoriel["Date"].iloc[0])
    return tot_national, secteurs_all.sort_values("Value", ascending=False), annee


def coverage_regionale(forets):
    """Indice de couverture protégée régionale (notebook, cellule 46)."""
    cov = forets.groupby("region_nom_bdd").agg(nb_forets=("area_km2", "size"), superficie_protegee_km2=("area_km2", "sum"))
    cov["superficie_region_km2"] = cov.index.map(SUPERFICIE_REGION_KM2)
    cov["couverture_pct"] = cov["superficie_protegee_km2"] / cov["superficie_region_km2"] * 100
    cov["part_du_nb_total_pct"] = cov["nb_forets"] / cov["nb_forets"].sum() * 100
    return cov.sort_values("couverture_pct", ascending=False)


@st.cache_data(show_spinner=False)
def tendances_par_ville(_temperatures, villes_ordre):
    """Pente OLS simple par ville (notebook, cellule 40) — utilisée pour la carte et le graphique de tendance."""
    tendances = {}
    for ville in villes_ordre:
        sub = _temperatures[(_temperatures.villes == ville) & (_temperatures["libellés"] == "Températures maximales")].groupby("Year")["Value"].mean()
        if len(sub) >= 2:
            pente, _ = np.polyfit(sub.index, sub.values, 1)
            tendances[ville] = pente
    return pd.Series(tendances).reindex(villes_ordre)


def _mann_kendall_original(y, alpha=0.05):
    """Test de Mann-Kendall original + pente de Sen, réimplémentés ici en pur numpy/scipy
    (algorithme identique à pymannkendall.original_test — Mann 1945, Kendall 1975, Sen 1968,
    correction d'ex-aequo incluse).

    Cette fonction remplace la dépendance au paquet tiers ``pymannkendall``, qui provoquait
    des erreurs d'import selon les versions de numpy/scipy résolues au déploiement (le paquet
    n'est plus maintenu et son epsilon de compatibilité est étroit). N'utiliser ici que numpy
    et scipy — déjà des dépendances fermes de l'application — supprime ce point de fragilité."""
    from scipy import stats as scistats

    y = np.asarray(y, dtype=float)
    n = len(y)

    # Score S (somme des signes des différences deux à deux)
    s = 0.0
    for k in range(n - 1):
        s += np.sum(np.sign(y[k + 1:] - y[k]))

    # Variance de S, corrigée des ex-aequo
    valeurs_uniques, effectifs = np.unique(y, return_counts=True)
    if len(valeurs_uniques) == n:
        var_s = (n * (n - 1) * (2 * n + 5)) / 18
    else:
        var_s = (n * (n - 1) * (2 * n + 5) - np.sum(effectifs * (effectifs - 1) * (2 * effectifs + 5))) / 18

    if s > 0:
        z = (s - 1) / np.sqrt(var_s)
    elif s < 0:
        z = (s + 1) / np.sqrt(var_s)
    else:
        z = 0.0

    p = 2 * (1 - scistats.norm.cdf(abs(z)))
    significatif = abs(z) > scistats.norm.ppf(1 - alpha / 2)
    if z > 0 and significatif:
        trend = "increasing"
    elif z < 0 and significatif:
        trend = "decreasing"
    else:
        trend = "no trend"

    # Pente de Sen : médiane des pentes de toutes les paires (i<j)
    pentes = np.array([(y[j] - y[i]) / (j - i) for i in range(n - 1) for j in range(i + 1, n)])
    pente_sen = np.median(pentes)

    return {"trend": trend, "p": float(p), "slope": float(pente_sen)}


@st.cache_data(show_spinner="Calcul des statistiques de tendance (Mann-Kendall, pente de Sen)...")
def stats_climatiques(_temperatures, villes_ordre):
    """Statistiques de tendance formelles : R², p-value, IC95%, Mann-Kendall, pente de Sen
    (notebook, cellule 42) — identique, seuil de significativité 5%.

    Chaque ville est calculée indépendamment, dans son propre bloc try/except : si une
    ville pose problème (série trop courte ou valeurs dégénérées), elle est simplement omise
    du tableau plutôt que de faire planter toute la page avec une trace Python brute. Voir
    app_views/climatologie.py pour le message affiché quand le tableau résultant est partiel
    ou vide."""
    from scipy import stats as scistats

    lignes = []
    erreurs = []
    for ville in villes_ordre:
        try:
            sub = (_temperatures[(_temperatures.villes == ville) & (_temperatures["libellés"] == "Températures maximales")]
                   .groupby("Year")["Value"].mean())
            if len(sub) < 4:
                continue
            x = sub.index.values.astype(float)
            y = sub.values.astype(float)
            if np.nanstd(y) == 0 or np.isnan(y).any():
                continue
            slope, intercept, r, p, se = scistats.linregress(x, y)
            n = len(x)
            tval = scistats.t.ppf(0.975, max(n - 2, 1))
            ic95 = tval * se if np.isfinite(se) else float("nan")
            mk_res = _mann_kendall_original(y)
            trend_fr = {
                "increasing": "Croissante",
                "decreasing": "Décroissante",
                "no trend": "Aucune tendance",
            }.get(mk_res["trend"], mk_res["trend"])
            lignes.append({
                "Ville": ville, "Années": n,
                "Pente OLS (°C/an)": round(slope, 4),
                "IC95% (±)": round(ic95, 4) if np.isfinite(ic95) else None,
                "R²": round(r ** 2, 3) if np.isfinite(r) else None,
                "p-value (OLS)": round(p, 3) if np.isfinite(p) else None,
                "Mann-Kendall": trend_fr,
                "p-value (MK)": round(mk_res["p"], 3),
                "Pente de Sen (°C/an)": round(mk_res["slope"], 4),
            })
        except Exception as exc:  # ville isolée, jamais toute la page
            erreurs.append(f"{ville} : {exc}")

    df = pd.DataFrame(lignes)
    if erreurs:
        df.attrs["erreurs"] = erreurs
    return df
