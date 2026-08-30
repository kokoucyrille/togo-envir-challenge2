"""
Chargement et nettoyage des données — logique reprise à l'identique du notebook
de référence (Analyse_Energie_Climat_Forets_Togo_REVISE.ipynb, Section 3
"Qualité et préparation des données").

Toute transformation ici doit être traçable à une cellule précise du notebook.
Rien n'est recalculé "à la main" avec des valeurs différentes : le code est
le même, donc les résultats sont nécessairement identiques (Règle 2 — fidélité
au notebook).
"""

from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import streamlit as st
from shapely import wkt

from utils.constants import DATA_DIR


# ------------------------------------------------------------------
# Fonctions génériques (identiques au notebook, Section 3)
# ------------------------------------------------------------------
def load_data(path, **kwargs):
    """Charge un CSV, lève une erreur explicite si le fichier est absent."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")
    return pd.read_csv(path, **kwargs)


def clean_data(df, subset_dropna=None, dedup_subset=None):
    """Nettoyage standard : retire les lignes sans valeur, dé-doublonne."""
    out = df.copy()
    if subset_dropna:
        out = out.dropna(subset=subset_dropna)
    if dedup_subset:
        out = out.drop_duplicates(subset=dedup_subset)
    else:
        out = out.drop_duplicates()
    return out.reset_index(drop=True)


def validate_data(df, name, year_col=None, value_col=None, value_range=None):
    """Contrôles automatiques : lignes>0, pas de doublons, années/valeurs plausibles.
    Retourne (ok: bool, liste_problemes: list[str])."""
    problems = []
    if df.shape[0] == 0:
        problems.append("dataframe vide")
    if df.duplicated().sum() > 0:
        problems.append(f"{df.duplicated().sum()} doublon(s) exact(s)")
    if year_col is not None and year_col in df.columns:
        if df[year_col].isna().any():
            problems.append(f"années manquantes dans '{year_col}'")
        if (df[year_col] < 1900).any() or (df[year_col] > 2035).any():
            problems.append(f"année hors plage plausible dans '{year_col}'")
    if value_col is not None and value_range is not None and value_col in df.columns:
        vmin, vmax = value_range
        out_of_range = df[(df[value_col] < vmin) | (df[value_col] > vmax)]
        if len(out_of_range):
            problems.append(f"{len(out_of_range)} valeur(s) hors intervalle [{vmin}, {vmax}] dans '{value_col}'")
    return (len(problems) == 0), problems


def get_series(indicators_df, indicator_name):
    """Extrait une série temporelle propre (Year, Value) pour un indicateur WDI donné —
    identique à get_series() dans le notebook."""
    s = (indicators_df[indicators_df["Indicator Name"] == indicator_name]
         .dropna(subset=["Value"])
         .drop_duplicates(subset=["Year"])
         .sort_values("Year"))
    return s[["Year", "Value"]].reset_index(drop=True)


# ------------------------------------------------------------------
# Chargement principal (mise en cache — Section 34 du cahier des charges)
# ------------------------------------------------------------------
@st.cache_data(show_spinner="Chargement des données sources...")
def load_all_data():
    """Charge et nettoie les 6 jeux de données utiles, exactement comme le notebook
    (cellules 'Chargement typé' et 'Contrôles automatiques'). Retourne un dict de DataFrames
    + un journal de contrôle qualité (liste de dicts) à afficher dans 'Qualité & méthodologie'."""

    journal = []

    # 1) Indicateurs Banque mondiale (WDI)
    indicators = pd.read_csv(DATA_DIR / "indicators-tgo.csv", skiprows=[1])
    n_before = len(indicators)
    indicators = indicators.drop_duplicates()
    journal.append({"étape": "indicators-tgo.csv", "détail": f"{n_before - len(indicators):,} doublon(s) exact(s) retiré(s)"})

    # 2) Séries dédiées CO2 énergie & renouvelables/biomasse
    co2_energie = pd.read_csv(DATA_DIR / "emissions-de-dioxyde-de-carbone-co2-du-secteur-de-lenergie-mt-co2e-.csv")
    renouvelables = pd.read_csv(DATA_DIR / "energies-renouvelables-combustibles-et-dechets-de-lenergie-totale-.csv")

    # 3) Bilan GES sectoriel — correction d'unité Gg -> Mt (voir notebook, Section 3 puis Section 7)
    ges_sectoriel = pd.read_csv(DATA_DIR / "observationdata-xorttne.csv")
    unites_ges = set(ges_sectoriel["Unit"].unique())
    if unites_ges != {"Gg"}:
        journal.append({"étape": "observationdata-xorttne.csv", "détail": f"ALERTE : unité inattendue : {unites_ges}"})
    ges_sectoriel["Value_Gg"] = ges_sectoriel["Value"]
    ges_sectoriel["Value"] = ges_sectoriel["Value_Gg"] / 1000.0  # Gg -> Mt CO2e
    journal.append({"étape": "observationdata-xorttne.csv", "détail": "Conversion Gg -> Mt CO2e appliquée (÷1000)"})

    # 4) Températures mensuelles, 10 villes
    temperatures = pd.read_csv(DATA_DIR / "observationdata-yvlucze.csv")
    temperatures["Year"] = temperatures["Date"].str.extract(r"(\d{4})").astype(int)
    temperatures["Month"] = temperatures["Date"].str.extract(r"M(\d+)").astype(int)

    # 5) Forêts classées / zones protégées (géométries WKT -> GeoDataFrame)
    forets = pd.read_csv(DATA_DIR / "file-zones-protegees-forets-classees-23-12-2024-09-53-17.csv")
    forets["geometry"] = forets["geometry"].apply(wkt.loads)
    forets = gpd.GeoDataFrame(forets, geometry="geometry", crs="EPSG:4326")

    # --- Préparation géospatiale (projection UTM 31N — Section 9/12 du notebook) ---
    forets_m = forets.to_crs(32631)
    forets["area_km2"] = forets_m.geometry.area / 1e6
    forets["centroid"] = forets_m.geometry.centroid.to_crs(4326)
    forets["lon"] = forets["centroid"].x
    forets["lat"] = forets["centroid"].y
    forets = forets.reset_index(drop=True)
    coords_m = np.column_stack([forets_m.geometry.centroid.x, forets_m.geometry.centroid.y])

    # --- Contrôles automatiques post-chargement ---
    checks = [
        ("indicators-tgo.csv", indicators, "Year", None, None),
        ("CO2 secteur énergie", co2_energie.dropna(subset=["value"]), "date", "value", (0, 50)),
        ("Renouvelables + biomasse (% énergie)", renouvelables.dropna(subset=["value"]), "date", "value", (0, 100)),
        ("GES sectoriel (converti en Mt)", ges_sectoriel, None, "Value", (0, 100)),
        ("Températures (10 villes)", temperatures, "Year", "Value", (-5, 55)),
    ]
    for name, df, ycol, vcol, vrange in checks:
        ok, problems = validate_data(df, name, year_col=ycol, value_col=vcol, value_range=vrange)
        journal.append({"étape": name, "détail": "OK" if ok else "ALERTE : " + " ; ".join(problems)})

    # Contrôle de cohérence sectorielle GES : somme des secteurs = total national
    tot_national = ges_sectoriel[(ges_sectoriel.secteur == "Total") & (ges_sectoriel.type == "Total")]["Value"].values[0]
    sum_secteurs = ges_sectoriel[(ges_sectoriel.type == "Total") & (ges_sectoriel.secteur != "Total")]["Value"].sum()
    coherent = abs(tot_national - sum_secteurs) < 0.01
    journal.append({
        "étape": "Cohérence sectorielle GES",
        "détail": f"{'OK' if coherent else 'INCOHERENT'} — somme secteurs = {sum_secteurs:.2f} Mt vs total déclaré = {tot_national:.2f} Mt",
    })

    return {
        "indicators": indicators,
        "co2_energie": co2_energie,
        "renouvelables": renouvelables,
        "ges_sectoriel": ges_sectoriel,
        "temperatures": temperatures,
        "forets": forets,
        "coords_m": coords_m,
        "journal": journal,
        "tot_national_ges": tot_national,
        "sum_secteurs_ges": sum_secteurs,
        "coherence_ges": coherent,
    }


@st.cache_data(show_spinner=False)
def inventaire_fichiers():
    """Reproduit l'inventaire technique des fichiers sources (notebook, cellule 'Inventaire')."""
    rows = []
    for p in sorted(DATA_DIR.glob("*.csv")):
        tmp = pd.read_csv(p, low_memory=False, encoding="utf-8-sig", on_bad_lines="skip")
        rows.append({
            "fichier": p.name,
            "lignes": tmp.shape[0],
            "colonnes": tmp.shape[1],
            "valeurs_manquantes_%": round(tmp.isna().mean().mean() * 100, 1),
            "doublons_exacts": int(tmp.duplicated().sum()),
        })
    return pd.DataFrame(rows).sort_values("lignes", ascending=False).reset_index(drop=True)
