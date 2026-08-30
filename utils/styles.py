"""CSS institutionnel — vert/blanc, accent jaune-vert avec parcimonie, aucun emoji.
Design professionnel : cartes avec relief léger, navigation soignée, onglets et
tableaux harmonisés avec la palette du projet.
"""

import streamlit as st

from utils.constants import (
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_ACCENT, COLOR_ACCENT_BRIGHT, COLOR_ALERT,
    COLOR_BG_SOFT, COLOR_TEXT,
)

_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/icon?family=Material+Symbols+Outlined');

html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}}

/* -------- Mise en page générale -------- */
.block-container {{
    padding-top: 1.6rem;
    padding-bottom: 3rem;
    max-width: 1320px;
}}
h2, h3, h4 {{ color: {COLOR_TEXT}; font-weight: 700; letter-spacing: -0.01em; }}
hr {{ border-color: #E3E7E1; }}

/* -------- Barre latérale -------- */
section[data-testid="stSidebar"] {{
    background: {COLOR_BG_SOFT};
    border-right: 1px solid #E3E7E1;
}}
section[data-testid="stSidebar"] .block-container {{ padding-top: 0.6rem; }}

/* -------- Logo institutionnel (st.logo), affiché en entier (texte inclus) en haut de
   barre, avec une petite marge au-dessus -------- */
[data-testid="stSidebarHeader"] {{
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding: 0.85rem 0.75rem 1rem 0.75rem;
    height: auto !important;
    min-height: 0 !important;
}}
[data-testid="stSidebarHeader"] img,
[data-testid="stSidebarHeader"] svg {{
    height: auto !important;
    width: auto !important;
    max-width: 150px !important;
    max-height: 190px !important;
    box-sizing: border-box !important;
    border-radius: 10px !important;
    object-fit: contain !important;
    background: #FFFFFF;
    padding: 0.5rem;
    border: 1px solid #E3E7E1;
    box-shadow: 0 4px 14px rgba(16, 24, 20, 0.10);
}}
[data-testid="stLogo"],
[data-testid="stSidebarLogo"],
.stLogo {{
    height: auto !important;
    width: auto !important;
    max-width: 150px !important;
    border-radius: 10px !important;
}}

/* Sections de navigation groupée (st.navigation en mode dict) : libellés de section
   discrets, en petites majuscules, pour séparer "Analyse" et "Informations" */
[data-testid="stNavSectionHeader"] {{
    text-transform: uppercase;
    font-size: 0.68rem !important;
    letter-spacing: 0.08em;
    color: #8A9186 !important;
    font-weight: 700 !important;
    margin: 1rem 0 0.3rem 0.75rem !important;
}}

/* Navigation native st.navigation : boutons espacés, coins arrondis, retour visuel
   soigné au survol et état actif marqué par un dégradé + liseré, sans décalage de mise
   en page (accent en box-shadow plutôt qu'en bordure). */
[data-testid="stSidebarNav"] a,
[data-testid="stSidebarNavLink"] {{
    border-radius: 10px !important;
    margin: 3px 0.6rem !important;
    padding: 0.55rem 0.8rem !important;
    font-weight: 500 !important;
    color: {COLOR_TEXT} !important;
    transition: background-color 0.16s ease, transform 0.16s ease, box-shadow 0.16s ease;
}}
[data-testid="stSidebarNav"] a:hover,
[data-testid="stSidebarNavLink"]:hover {{
    background-color: rgba(27, 67, 50, 0.09) !important;
    transform: translateX(2px);
}}
[data-testid="stSidebarNav"] a[aria-current="page"],
[data-testid="stSidebarNavLink"][aria-current="page"] {{
    background: linear-gradient(90deg, rgba(27, 67, 50, 0.15), rgba(45, 106, 79, 0.07)) !important;
    color: {COLOR_PRIMARY} !important;
    font-weight: 700 !important;
    box-shadow: inset 3px 0 0 {COLOR_PRIMARY};
}}

/* -------- Bandeau "hero" page d'accueil -------- */
.tg-hero {{
    background: linear-gradient(135deg, {COLOR_PRIMARY} 0%, {COLOR_SECONDARY} 100%);
    border-radius: 16px;
    padding: 2.6rem 2.6rem;
    color: white;
    margin-bottom: 1.8rem;
    box-shadow: 0 8px 24px rgba(27, 67, 50, 0.18);
}}
.tg-hero h1 {{
    font-size: 2.15rem;
    font-weight: 800;
    margin: 0 0 0.45rem 0;
    color: white;
    letter-spacing: -0.02em;
}}
.tg-hero p {{
    font-size: 1.06rem;
    opacity: 0.94;
    margin: 0;
}}
.tg-hero .tg-accent-bar {{
    width: 56px; height: 4px; background: {COLOR_ACCENT_BRIGHT};
    border-radius: 2px; margin-bottom: 1rem;
}}

/* -------- Cartes KPI : grille CSS responsive (auto-fit) -------- */
/* Rendu en grille plutôt qu'en st.columns : les cartes passent naturellement à la
   ligne sur écran étroit au lieu de se compresser jusqu'à devenir illisibles —
   c'est le principal gain de fluidité demandé sur les pages à forte densité de KPI. */
.tg-kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    gap: 0.85rem;
    margin: 0.4rem 0 0.2rem 0;
}}
.tg-kpi-card {{
    background: white;
    border: 1px solid #E9ECE6;
    border-radius: 14px;
    padding: 1.0rem 1.05rem 0.85rem 1.05rem;
    box-shadow: 0 1px 3px rgba(16, 24, 20, 0.06);
    transition: box-shadow 0.15s ease, transform 0.15s ease;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 128px;
}}
.tg-kpi-card:hover {{ box-shadow: 0 6px 16px rgba(16, 24, 20, 0.12); transform: translateY(-1px); }}
.tg-kpi-top {{
    display: flex;
    align-items: center;
    gap: 0.55rem;
    margin-bottom: 0.55rem;
}}
.tg-kpi-icon-badge {{
    flex: 0 0 auto;
    width: 30px;
    height: 30px;
    border-radius: 8px;
    background: rgba(27, 67, 50, 0.09);
    display: flex;
    align-items: center;
    justify-content: center;
}}
.tg-kpi-label {{
    font-size: 0.8rem;
    color: {COLOR_TEXT};
    opacity: 0.78;
    font-weight: 600;
    line-height: 1.25;
}}
.tg-kpi-value {{
    font-size: 1.62rem;
    font-weight: 800;
    color: {COLOR_PRIMARY};
    line-height: 1.1;
    letter-spacing: -0.01em;
}}
.tg-kpi-delta {{ font-size: 0.8rem; color: {COLOR_PRIMARY}; margin-top: 3px; font-weight: 600; }}
.tg-kpi-meta {{
    font-size: 0.71rem;
    color: #6C757D;
    margin-top: 0.55rem;
    padding-top: 0.4rem;
    border-top: 1px dashed #E9ECE6;
}}

/* -------- Panneau de contrôles / filtres (regroupe les widgets, distinct des résultats) --------
   Le regroupement visuel repose sur st.container(border=True) (bordure native Streamlit,
   garantie stable d'une version à l'autre) plutôt que sur un sélecteur CSS visant la
   structure interne du DOM, qui varie selon la version de Streamlit installée. */
.tg-controls-label {{
    text-transform: uppercase;
    font-size: 0.7rem;
    letter-spacing: 0.06em;
    font-weight: 700;
    color: #6C757D;
    margin-bottom: 0.5rem;
}}

/* -------- Bannière image (page d'accueil) -------- */
.tg-banner-wrap {{
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 8px 22px rgba(16, 24, 20, 0.14);
    margin-bottom: 0.5rem;
    line-height: 0;
}}
.tg-banner-wrap img {{ width: 100%; height: auto; display: block; }}
.tg-banner-caption {{
    font-size: 0.78rem;
    color: #6C757D;
    margin: 0.4rem 0 1.4rem 0;
    font-style: italic;
}}

/* -------- Liste compacte de constats (page d'accueil) -------- */
.tg-mini-constat {{
    display: flex;
    gap: 0.6rem;
    padding: 0.55rem 0;
    border-bottom: 1px solid #EEF1EC;
}}
.tg-mini-constat:last-child {{ border-bottom: none; }}
.tg-mini-dot {{
    flex: 0 0 auto;
    width: 8px; height: 8px; border-radius: 50%;
    background: {COLOR_ACCENT_BRIGHT};
    margin-top: 0.45rem;
}}
.tg-mini-title {{ font-weight: 700; font-size: 0.92rem; color: {COLOR_TEXT}; line-height: 1.35; }}
.tg-mini-sub {{ font-size: 0.79rem; color: #6C757D; margin-top: 0.15rem; }}

/* -------- Blocs de storytelling (Question / Constat / Enjeu / Action) -------- */
.tg-story-block {{
    border-radius: 10px;
    padding: 0.85rem 1.1rem;
    margin-bottom: 0.7rem;
    background: {COLOR_BG_SOFT};
    border-left: 3px solid {COLOR_PRIMARY};
}}
.tg-story-label {{
    text-transform: uppercase;
    font-size: 0.71rem;
    letter-spacing: 0.07em;
    font-weight: 700;
    color: {COLOR_PRIMARY};
    margin-bottom: 0.25rem;
}}
.tg-alert-block {{ border-left: 3px solid {COLOR_ALERT}; background: #FBF2F0; }}
.tg-alert-block .tg-story-label {{ color: {COLOR_ALERT}; }}

/* -------- Bandeau avertissement (projections, proxys) -------- */
.tg-notice {{
    background: #FBF7EC;
    border: 1px solid #EADFC0;
    border-radius: 8px;
    padding: 0.65rem 0.95rem;
    font-size: 0.87rem;
    color: #5A4A1F;
    margin: 0.5rem 0 1rem 0;
}}

/* -------- Séparateurs d'axe (page recommandations) -------- */
.tg-axe-title {{
    color: {COLOR_PRIMARY};
    font-weight: 700;
    font-size: 1.08rem;
    border-bottom: 2px solid {COLOR_ACCENT_BRIGHT};
    padding-bottom: 0.3rem;
    margin: 1.3rem 0 0.7rem 0;
}}

/* -------- Onglets (st.tabs) -------- */
div[data-baseweb="tab-list"] {{
    gap: 4px;
    border-bottom: 1px solid #E3E7E1;
}}
button[data-baseweb="tab"] {{
    font-weight: 600;
    font-size: 0.92rem;
    color: #6C757D;
    padding: 0.5rem 1rem;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: {COLOR_PRIMARY};
}}
div[data-baseweb="tab-highlight"] {{
    background-color: {COLOR_PRIMARY} !important;
    height: 3px;
}}

/* -------- Boutons -------- */
.stButton > button {{
    border-radius: 8px;
    font-weight: 600;
    border: 1px solid {COLOR_PRIMARY};
    color: {COLOR_PRIMARY};
}}
.stButton > button:hover {{
    border-color: {COLOR_PRIMARY};
    color: white;
    background-color: {COLOR_PRIMARY};
}}
.stButton > button[kind="primary"] {{
    background-color: {COLOR_PRIMARY};
    color: white;
}}

/* -------- Tableaux et métriques -------- */
[data-testid="stMetric"] {{
    background: white;
    border: 1px solid #E9ECE6;
    border-radius: 10px;
    padding: 0.7rem 0.9rem;
}}
[data-testid="stMetricValue"] {{ color: {COLOR_PRIMARY}; }}

footer {{visibility: hidden;}}
#MainMenu {{visibility: hidden;}}
</style>
"""


def inject_css():
    st.markdown(_CSS, unsafe_allow_html=True)
