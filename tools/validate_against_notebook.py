"""
Matrice de validation interne : Application Streamlit vs Notebook de référence.

Ce script recalcule, avec les services de l'application, les indicateurs clés du
notebook et les compare aux valeurs de référence extraites de l'exécution réelle du
notebook (Analyse_Energie_Climat_Forets_Togo_REVISE.ipynb, sorties de cellules
capturées lors de son exécution complète — voir commentaires ci-dessous pour la
provenance de chaque valeur de référence).

Usage : python tools/validate_against_notebook.py
Sortie : tableau de conformité (cahier des charges, Section 38) — aucun résultat n'est
déclaré conforme sans comparaison numérique explicite.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.data_loader import load_all_data
from services import indicators as ind
from services import analysis as an
from utils.constants import SUPERFICIE_REGION_KM2

TOLERANCE = 0.05  # tolérance relative acceptée (arrondis)


def close(a, b, tol=TOLERANCE):
    if a is None or b is None:
        return a == b
    if b == 0:
        return abs(a - b) < 1e-6
    return abs(a - b) / abs(b) <= tol


def main():
    data = load_all_data()
    elec = ind.get_electricity_series(data["indicators"])
    comb = ind.get_combustibles_series(data["indicators"])
    foret = ind.get_foret_series(data["indicators"])
    kpi_elec = ind.kpi_electricite(elec)
    biomasse = ind.kpi_biomasse(comb)
    defor = ind.kpi_deforestation(foret)
    tot_ges, secteurs, annee_ges = ind.ges_secteurs(data["ges_sectoriel"])
    part_afat = secteurs[secteurs["secteur"].str.contains("AFAT")]["part_pct"].values[0]
    cov = ind.coverage_regionale(data["forets"])

    forets_c, G, _ = an.build_centrality(data["forets"], data["coords_m"], 4)
    forets_v = an.add_vulnerabilite_defaut(forets_c)
    prio = an.indice_priorite_territoriale(
        forets_v, elec["national"].Value.iloc[-1], biomasse["biomasse_dep_pct"], SUPERFICIE_REGION_KM2
    )

    # Valeurs de référence extraites de l'exécution réelle du notebook (sorties de cellules)
    reference = {
        "Accès national (dernier point)": (kpi_elec["kpi1_national"]["valeur_fin"], 57.2),
        "Accès rural (dernier point)": (kpi_elec["kpi2_rural"]["valeur_fin"], 25.0),
        "Accès urbain (dernier point)": (kpi_elec["kpi3_urbain"]["valeur_fin"], 96.5),
        "Gap urbain-rural (dernier point)": (kpi_elec["kpi4_gap_fin"], 71.5),
        "Dépendance biomasse (bois+charbon)": (biomasse["biomasse_dep_pct"], 89.4),
        "Superficie forestière initiale (1990)": (defor["foret_initiale"], 13617),
        "Superficie forestière finale (2021)": (defor["foret_finale"], 12063),
        "Perte forestière absolue (km²)": (defor["perte_km2"], 1554),
        "Perte forestière relative (%)": (defor["perte_pct"], 11.4),
        "Taux annuel de perte (km²/an)": (defor["taux_annuel_km2"], 50),
        "Bilan GES total (Mt CO2e, 2018)": (tot_ges, 40.84),
        "Part AFAT du bilan GES (%)": (part_afat, 87.7),
        "Superficie protégée région Centrale (km²)": (cov.loc["Centrale", "superficie_protegee_km2"], 255.49),
        "Superficie protégée région Kara (km²)": (cov.loc["Kara", "superficie_protegee_km2"], 246.73),
        "Superficie protégée région Maritime (km²)": (cov.loc["Maritime", "superficie_protegee_km2"], 0.605),
        "Superficie protégée région Plateaux (km²)": (cov.loc["Plateaux", "superficie_protegee_km2"], 319.84),
        "Superficie protégée région Savanes (km²)": (cov.loc["Savanes", "superficie_protegee_km2"], 92.33),
        "Indice de priorité territoriale — région en tête": (prio.index[0], "Maritime"),
    }

    print(f"{'Élément':45s} | {'Notebook':>12s} | {'Application':>12s} | Conforme")
    print("-" * 90)
    all_ok = True
    for label, (app_val, notebook_val) in reference.items():
        if isinstance(notebook_val, str):
            ok = app_val == notebook_val
        else:
            ok = close(app_val, notebook_val)
        all_ok = all_ok and ok
        app_str = f"{app_val:.2f}" if isinstance(app_val, float) else str(app_val)
        nb_str = f"{notebook_val:.2f}" if isinstance(notebook_val, float) else str(notebook_val)
        print(f"{label:45s} | {nb_str:>12s} | {app_str:>12s} | {'OK' if ok else 'ECART'}")

    print("-" * 90)
    print("RESULTAT GLOBAL :", "CONFORME" if all_ok else "ECARTS DETECTES — A INVESTIGUER")


if __name__ == "__main__":
    main()
