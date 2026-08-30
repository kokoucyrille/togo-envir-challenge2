"""
Constantes du projet — reprises telles quelles du notebook de référence
(Analyse_Energie_Climat_Forets_Togo_REVISE.ipynb).

Toute valeur ici est soit :
  - une constante sourcée utilisée par le notebook (objectifs officiels, superficies
    régionales, comparaison WDPA) ;
  - un paramètre de présentation (couleurs, chemins).

Aucune valeur analytique (KPI, résultat de modèle) ne doit être codée en dur ici :
ces valeurs sont TOUJOURS recalculées depuis les données par services/*.py, pour
garantir la fidélité au notebook (Règle 2 du cahier des charges).
"""

from pathlib import Path

# ------------------------------------------------------------------
# Chemins (relatifs — le projet doit fonctionner après un simple git clone)
# ------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

# ------------------------------------------------------------------
# Palette — reprise à l'identique du notebook de référence (cellule de configuration)
# ------------------------------------------------------------------
COLOR_PRIMARY = "#1B4332"      # vert forêt (AFAT / éléments structurants)
COLOR_SECONDARY = "#2D6A4F"
COLOR_ACCENT = "#D68C45"       # ocre — énergie / biomasse
COLOR_ALERT = "#B02E0C"        # rouge alerte — à utiliser avec parcimonie
COLOR_BLUE = "#1B5E8C"         # bleu — électricité / froid
COLOR_PURPLE = "#7B4B94"       # violet — centralité
COLOR_GREY = "#6C757D"
COLOR_BG = "#FFFFFF"
COLOR_BG_SOFT = "#F5F7F4"
COLOR_TEXT = "#1A1A1A"
COLOR_ACCENT_BRIGHT = "#B7D63A"  # jaune-vert lumineux — accent UI uniquement (hors graphiques notebook)

REGION_COLORS = {
    "Maritime": COLOR_BLUE,
    "Plateaux": COLOR_SECONDARY,
    "Centrale": COLOR_ACCENT,
    "Kara": COLOR_PURPLE,
    "Savanes": COLOR_ALERT,
}

CHART_TEMPLATE = "simple_white"  # gabarit Plotly sobre

# ------------------------------------------------------------------
# Objectifs officiels 2030 (Section 14 du notebook)
# Source : Pacte National de l'Énergie du Togo, sept. 2025 —
# Banque mondiale, "Togo National Energy Compact" (Mission 300, 2026)
# ------------------------------------------------------------------
OBJECTIFS_2030 = {
    "acces_electricite_national": {"valeur": 100, "unite": "%", "libelle": "Accès universel à l'électricité"},
    "acces_electricite_rural": {"valeur": 100, "unite": "%", "libelle": "Accès rural à l'électricité"},
    "acces_electricite_urbain": {"valeur": 100, "unite": "%", "libelle": "Accès urbain à l'électricité"},
    "cuisson_propre_rural": {"valeur": 80, "unite": "%", "libelle": "Accès à la cuisson propre"},
    "cuisson_propre_urbain": {"valeur": 80, "unite": "%", "libelle": "Accès à la cuisson propre"},
    "part_renouvelables_mix_electrique": {"valeur": 50, "unite": "%", "libelle": "Part des renouvelables dans le mix électrique (opérateur)"},
}
SOURCE_OBJECTIFS_2030 = "Pacte National de l'Énergie du Togo (sept. 2025) — Banque mondiale, Mission 300 (2026)"

# Avertissement méthodologique : l'indicateur "renouvelables" du dataset mesure la part
# dans la consommation totale d'énergie finale (y compris biomasse traditionnelle),
# une définition différente de l'objectif officiel qui porte sur le mix électrique.
# -> le gap correspondant N'EST PAS calculé dans l'application (voir notebook, Section 14).
RENOUVELABLES_DEFINITION_NON_COMPARABLE = True

# ------------------------------------------------------------------
# Actualisation documentée (Section 5.1 du notebook) — deux sources, écarts non fusionnés
# ------------------------------------------------------------------
ACTUALISATION_ACCES_ELECTRICITE = [
    {"source": "Banque mondiale (WDI), via Trading Economics", "annee": 2023, "national": 59.2},
    {"source": "AT2ER (Agence togolaise d'électrification rurale)", "annee": 2025, "national": 69.0, "urbain": 85.0, "rural": 25.0},
]

# ------------------------------------------------------------------
# Superficies régionales (Section 9 du notebook) — compilations cartographiques publiques,
# non fournies par le cadastre du Data Challenge ; utilisées uniquement comme dénominateur
# pour l'indice de couverture régionale. À vérifier auprès de l'INSEED/IGN-Togo pour un usage officiel.
# ------------------------------------------------------------------
SUPERFICIE_REGION_KM2 = {
    "Maritime": 6100,
    "Plateaux": 16975,
    "Centrale": 13182,
    "Kara": 11630,
    "Savanes": 8602,
}

# ------------------------------------------------------------------
# Comparaison de périmètre — aires protégées (Section 9 du notebook)
# Source : Protected Planet / World Database on Protected Areas (WDPA), profil Togo
# ------------------------------------------------------------------
WDPA_NB_DESIGNATIONS_NATIONALES = 83
WDPA_SOURCE = "Protected Planet / WDPA — profil Togo, consulté janvier 2026 (https://www.protectedplanet.net/country/TGO)"
NB_FORETS_CLASSEES_CADASTRE = 53  # nombre de polygones dans le fichier fourni — PAS l'inventaire national

# ------------------------------------------------------------------
# Sources — table de référence affichée dans "Qualité & méthodologie"
# ------------------------------------------------------------------
SOURCES_TABLE = [
    {"dataset": "Accès électricité, cuisson propre, combustibles, forêt, fiabilité réseau",
     "source": "Banque mondiale — World Development Indicators (WDI)",
     "url": "https://data.worldbank.org/indicator", "annees": "1990-2022 (selon indicateur)"},
    {"dataset": "Émissions de CO2, secteur énergie",
     "source": "Banque mondiale / Climate Watch",
     "url": "https://data.worldbank.org/indicator", "annees": "1970-2022"},
    {"dataset": "Bilan GES sectoriel national",
     "source": "Inventaire national des émissions de GES",
     "url": "(fichier fourni par l'organisateur du Data Challenge)", "annees": "2018 (année unique)"},
    {"dataset": "Températures, 10 stations",
     "source": "Service météorologique national du Togo",
     "url": "(fichier fourni par l'organisateur du Data Challenge)", "annees": "2013-2019 (2019 partielle)"},
    {"dataset": "Forêts classées / zones protégées",
     "source": "Cadastre national (portail géospatial togolais), extraction du 23/12/2024",
     "url": "(fichier fourni, extraction du 23/12/2024)", "annees": "Créations 1884-auj."},
    {"dataset": "Aires protégées — comparaison de périmètre",
     "source": "Protected Planet / WDPA", "url": "https://www.protectedplanet.net/country/TGO",
     "annees": "Profil consulté janvier 2026"},
    {"dataset": "Objectifs officiels 2030",
     "source": "Pacte National de l'Énergie du Togo / Banque mondiale, Mission 300",
     "url": "worldbank.org — Togo National Energy Compact (2026)", "annees": "Cible 2030"},
]

# ------------------------------------------------------------------
# Indicateurs WDI utilisés (noms exacts dans indicators-tgo.csv)
# ------------------------------------------------------------------
IND_ACCES_RURAL = "Access to electricity, rural (% of rural population)"
IND_ACCES_URBAIN = "Access to electricity, urban (% of urban population)"
IND_ACCES_NATIONAL = "Access to electricity (% of population)"
IND_OUTAGES_FIRMES = "Firms experiencing electrical outages (% of firms)"
IND_PERTE_VENTES_OUTAGES = "Value lost due to electrical outages (% of sales for affected firms)"
IND_BOIS = "Main cooking fuel: wood (% of households)"
IND_CHARBON = "Main cooking fuel: charcoal (% of households)"
IND_LPG = "Main cooking fuel: LPG/natural gas/biogas (% of households)"
IND_CUISSON_PROPRE_RURAL = "Access to clean fuels and technologies for cooking, rural (% of rural population)"
IND_CUISSON_PROPRE_URBAIN = "Access to clean fuels and technologies for cooking, urban (% of urban population)"
IND_CUISSON_PROPRE_NATIONAL = "Access to clean fuels and technologies for cooking (% of population)"
IND_FORET_KM2 = "Forest area (sq. km)"
IND_FORET_PCT = "Forest area (% of land area)"
# NB : l'indicateur "renouvelables/biomasse" ne provient PAS de indicators-tgo.csv mais d'un fichier
# dédié (energies-renouvelables-...csv, colonnes 'date'/'value') — voir services/data_loader.py

# ------------------------------------------------------------------
# Villes climat (ordre Sud -> Nord), coordonnées (lon, lat) — identiques au notebook
# ------------------------------------------------------------------
VILLES_ORDRE = ["Lomé", "Tabligbo", "Kouma konda", "Atakpamé", "Sotouboua",
                "Sokodé", "Kara", "Niamtougou", "Mango", "Dapaong"]

VILLES_COORDS = {
    "Lomé": (1.22, 6.13), "Tabligbo": (1.50, 6.58), "Kouma konda": (0.74, 7.13),
    "Atakpamé": (1.13, 7.53), "Sotouboua": (0.98, 8.58), "Sokodé": (1.13, 8.98),
    "Kara": (1.19, 9.55), "Niamtougou": (1.10, 9.77), "Mango": (0.47, 10.36),
    "Dapaong": (0.20, 10.86),
}

SEUIL_SIGNIFICATIVITE = 0.05  # seuil p-value retenu (Mann-Kendall), identique au notebook

# ------------------------------------------------------------------
# Six rubriques de l'application (Section 8 du cahier des charges)
# ------------------------------------------------------------------
PAGES_ORDRE = ["accueil", "electrification", "biomasse_carbone", "climatologie",
               "cartographie_priorisation", "recommandations_2030"]

# ------------------------------------------------------------------
# Identité visuelle et auteur
# ------------------------------------------------------------------
LOGO_MINISTERE_PATH = ASSETS_DIR / "images" / "logo_ministere.png"
PHOTO_AUTEUR_PATH = ASSETS_DIR / "images" / "auteur_cyrille.png"
HERO_IMAGE_PATH = ASSETS_DIR / "images" / "hero_energie_afrique.jpg"

AUTEUR = {
    "nom": "DAYO Kokou Cyrille",
    "titre": "Ingénieur de Travaux Informatiques — DGTCP, Ministère des Finances et du Budget (Togo)",
    "bio": (
        "Fonctionnaire d'État togolais, je mets mon expertise en ingénierie "
        "informatique au service de la gestion des finances publiques. Passionné par "
        "la data science et l'analyse de données, je poursuis actuellement un Master "
        "Big Data à l'UCAO-UUT afin d'approfondir ces compétences. Ce tableau de bord "
        "illustre cette démarche : transformer des données réelles en diagnostics "
        "utiles et actionnables au service de la décision publique."
    ),
    "linkedin": "https://www.linkedin.com/in/dkc023/",
    "email": "cyridayo@gmail.com",
    "github": "https://github.com/kokoucyrille",
    "whatsapp": "+228 90515928",
}
