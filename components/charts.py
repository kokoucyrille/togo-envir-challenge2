"""
Graphiques interactifs (Plotly) — reproduisent fidèlement les analyses matplotlib du
notebook, avec les mêmes couleurs, mêmes titres, mêmes calculs. L'interactivité
(zoom, tooltip, légende cliquable) remplace les widgets ipywidgets du notebook,
dans le même esprit (cahier des charges, Section 22).
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.constants import (
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_ACCENT, COLOR_ALERT, COLOR_BLUE,
    COLOR_PURPLE, COLOR_GREY, REGION_COLORS, CHART_TEMPLATE,
)

# Séparation nette titre / légende : le titre reste seul dans la marge haute (bande
# dédiée, sobre, sans concurrence visuelle), la légende est repositionnée sous le
# graphique (bande basse dédiée). Les deux ne se chevauchent donc plus jamais, quel
# que soit le nombre de séries ou la longueur du titre — contrairement au réglage
# précédent qui plaçait légende et titre dans la même bande haute.
_LAYOUT_DEFAULTS = dict(
    template=CHART_TEMPLATE,
    font=dict(family="Inter, sans-serif", size=13),
    margin=dict(l=10, r=10, t=56, b=64),
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="left", x=0,
                font=dict(size=11.5)),
)

_TITLE_FONT = dict(family="Inter, sans-serif", size=16, color="#1A1A1A")


def _title_dict(html_text):
    """`html_text` doit déjà contenir sa propre mise en forme (ex. <b>...</b>) —
    voir chart_priorite_territoriale pour le cas d'un sous-titre non gras."""
    return dict(text=html_text, font=_TITLE_FONT, x=0, xanchor="left",
                y=0.97, yanchor="top", pad=dict(b=8))


def _apply_layout(fig, title, yaxis_title=None, ylim=None):
    fig.update_layout(title=_title_dict(f"<b>{title}</b>"), **_LAYOUT_DEFAULTS)
    if yaxis_title:
        fig.update_yaxes(title_text=yaxis_title)
    if ylim:
        fig.update_yaxes(range=ylim)
    # Marge basse auto-ajustée : quand un titre d'axe X est présent en plus de la
    # légende (déjà repositionnée sous le graphique), évite tout chevauchement entre
    # les deux au lieu de dépendre d'une marge fixe.
    fig.update_xaxes(automargin=True)
    return fig


# ------------------------------------------------------------------
# Électrification (notebook, cellule 13)
# ------------------------------------------------------------------
def chart_electrification(elec, annees=None, afficher_national=True):
    rural, urbain, national = elec["rural"], elec["urbain"], elec["national"]
    if annees:
        y0, y1 = annees
        rural = rural[(rural.Year >= y0) & (rural.Year <= y1)]
        urbain = urbain[(urbain.Year >= y0) & (urbain.Year <= y1)]
        national = national[(national.Year >= y0) & (national.Year <= y1)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=urbain.Year, y=urbain.Value, mode="lines+markers", name="Urbain",
                              line=dict(color=COLOR_BLUE, width=3)))
    fig.add_trace(go.Scatter(x=rural.Year, y=rural.Value, mode="lines+markers", name="Rural",
                              line=dict(color=COLOR_ACCENT, width=3)))
    if afficher_national and len(national):
        fig.add_trace(go.Scatter(x=national.Year, y=national.Value, mode="lines", name="National",
                                  line=dict(color=COLOR_GREY, width=1.6, dash="dash")))
    if len(rural) and len(urbain):
        fig.add_trace(go.Scatter(
            x=list(urbain.Year) + list(rural.Year[::-1]),
            y=list(urbain.Value) + list(rural.Value[::-1]),
            fill="toself", fillcolor="rgba(178,46,12,0.08)", line=dict(width=0),
            showlegend=False, hoverinfo="skip",
        ))
    y0v = annees[0] if annees else int(urbain.Year.min())
    y1v = annees[1] if annees else int(urbain.Year.max())
    return _apply_layout(fig, f"Accès à l'électricité — Togo, {y0v}-{y1v}", "% de la population", (0, 100))


# ------------------------------------------------------------------
# Fiabilité du réseau (notebook, cellule 17)
# ------------------------------------------------------------------
def chart_fiabilite(pannes, pertes, metrique="Les deux"):
    titres = []
    n = 2 if metrique == "Les deux" else 1
    fig = make_subplots(rows=1, cols=n, subplot_titles=None)
    col = 1
    if metrique in ("Les deux", "Entreprises touchées"):
        fig.add_trace(go.Bar(x=pannes.Year.astype(str), y=pannes.Value, marker_color=COLOR_ALERT,
                              text=[f"{v:.0f}%" for v in pannes.Value], textposition="outside",
                              name="Entreprises touchées"), row=1, col=col)
        fig.update_yaxes(title_text="% des entreprises", range=[0, 100], row=1, col=col)
        col += 1
    if metrique in ("Les deux", "Pertes financières"):
        fig.add_trace(go.Bar(x=pertes.Year.astype(str), y=pertes.Value, marker_color=COLOR_ACCENT,
                              text=[f"{v:.1f}%" for v in pertes.Value], textposition="outside",
                              name="Pertes financières"), row=1, col=col)
        fig.update_yaxes(title_text="% des ventes (entreprises touchées)", row=1, col=col)
    fig.update_layout(title=_title_dict("<b>Fiabilité du réseau électrique — proxy entreprises</b>"),
                       showlegend=False, **_LAYOUT_DEFAULTS)
    return fig


# ------------------------------------------------------------------
# Combustibles de cuisson (notebook, cellule 21)
# ------------------------------------------------------------------
def chart_combustibles(combustibles, selection=("Bois", "Charbon de bois", "Gaz (LPG)")):
    wood, charcoal, lpg = combustibles["bois"], combustibles["charbon"], combustibles["lpg"]
    years_common = sorted(set(wood.Year) & set(charcoal.Year) & set(lpg.Year))
    series_map = {"Bois": (wood, COLOR_ACCENT), "Charbon de bois": (charcoal, "#8B5A2B"), "Gaz (LPG)": (lpg, COLOR_SECONDARY)}

    fig = go.Figure()
    for label in ["Bois", "Charbon de bois", "Gaz (LPG)"]:
        if label not in selection:
            continue
        serie, color = series_map[label]
        vals = serie.set_index("Year").reindex(years_common)["Value"].values
        fig.add_trace(go.Bar(x=[str(y) for y in years_common], y=vals, name=label, marker_color=color))
    fig.update_layout(barmode="stack")
    return _apply_layout(fig, "Combustible principal de cuisson des ménages", "% des ménages", (0, 100))


# ------------------------------------------------------------------
# Cuisson propre (notebook, cellule 24)
# ------------------------------------------------------------------
def chart_cuisson_propre(cuisson, zones=("Urbain", "Rural")):
    fig = go.Figure()
    if "Urbain" in zones:
        fig.add_trace(go.Scatter(x=cuisson["urbain"].Year, y=cuisson["urbain"].Value, mode="lines+markers",
                                  name="Urbain", line=dict(color=COLOR_BLUE, width=3)))
    if "Rural" in zones:
        fig.add_trace(go.Scatter(x=cuisson["rural"].Year, y=cuisson["rural"].Value, mode="lines+markers",
                                  name="Rural", line=dict(color=COLOR_ALERT, width=3)))
    return _apply_layout(fig, "Accès à des solutions de cuisson propres", "% de la population")


def chart_gap_cuisson(gap_df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=gap_df.Year, y=gap_df.Gap, mode="lines", fill="tozeroy",
                              line=dict(color=COLOR_ALERT, width=2.5), fillcolor="rgba(176,46,12,0.15)"))
    return _apply_layout(fig, "Gap de cuisson propre urbain/rural — Togo", "Écart en points de %")


# ------------------------------------------------------------------
# Forêt vs biomasse/renouvelables (notebook, cellule 27)
# ------------------------------------------------------------------
def chart_foret_biomasse(foret_area, renouvelables_s, periode=None):
    fa = foret_area
    rs = renouvelables_s
    if periode:
        y0, y1 = periode
        fa = fa[(fa.Year >= y0) & (fa.Year <= y1)]
        rs = rs[(rs.date >= y0) & (rs.date <= y1)]

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=fa.Year, y=fa.Value, mode="lines", name="Superficie forestière (km²)",
                              line=dict(color=COLOR_PRIMARY, width=3)), secondary_y=False)
    fig.add_trace(go.Scatter(x=rs["date"], y=rs["value"], mode="lines", name="Renouvelables + biomasse (% énergie totale)",
                              line=dict(color=COLOR_ACCENT, width=2.5, dash="dash")), secondary_y=True)
    fig.update_yaxes(title_text="Superficie forestière (km²)", secondary_y=False)
    fig.update_yaxes(title_text="Part renouvelables/biomasse (%)", range=[0, 100], secondary_y=True)
    fig.update_layout(title=_title_dict("<b>Recul du couvert forestier vs. poids de la biomasse dans le mix énergétique</b>"),
                       **_LAYOUT_DEFAULTS)
    return fig


# ------------------------------------------------------------------
# GES par secteur (notebook, cellule 32)
# ------------------------------------------------------------------
_LABEL_MAP = {
    "Agriculture, Foresterie et autres Affectations des Terres (AFAT)": "Agriculture, Foresterie<br>& affectation des terres (AFAT)",
    "Energie": "Énergie",
    "Procédés Industriels et Utilisation des Produits (PIUP)": "Procédés industriels<br>& produits (PIUP)",
    "Déchets": "Déchets",
}


def chart_ges_secteurs(secteurs_all, tot_national, annee, secteurs_choisis=None, base_pct="Total national"):
    sub = secteurs_all if secteurs_choisis is None else secteurs_all[secteurs_all["secteur"].isin(secteurs_choisis)]
    sub = sub.sort_values("Value", ascending=True).copy()
    denom = tot_national if base_pct == "Total national" else sub["Value"].sum()
    sub["part_pct"] = sub.Value / denom * 100
    sub["label"] = sub["secteur"].map(lambda x: _LABEL_MAP.get(x, x))

    def color_for(s):
        if "AFAT" in s or "Agri" in s:
            return COLOR_PRIMARY
        if s == "Energie":
            return COLOR_BLUE
        if s == "Déchets":
            return COLOR_GREY
        return COLOR_ACCENT

    fig = go.Figure(go.Bar(
        x=sub["Value"], y=sub["label"], orientation="h",
        marker_color=[color_for(s) for s in sub["secteur"]],
        text=[f"{v:,.2f} Mt CO2e  ({p:.1f}%)" for v, p in zip(sub["Value"], sub["part_pct"])],
        textposition="outside",
    ))
    base_lbl = "du total national" if base_pct == "Total national" else "des secteurs sélectionnés"
    fig.update_layout(xaxis_title="Émissions (Mt CO2e)")
    return _apply_layout(fig, f"Émissions de GES par secteur — Togo, {annee} (% {base_lbl})")


def chart_co2_trend(co2_e, periode=None):
    sub = co2_e
    if periode:
        y0, y1 = periode
        sub = sub[(sub.date >= y0) & (sub.date <= y1)]
    fig = go.Figure(go.Scatter(x=sub["date"], y=sub["value"], mode="lines", fill="tozeroy",
                                line=dict(color=COLOR_BLUE, width=2.5), fillcolor="rgba(27,94,140,0.12)"))
    return _apply_layout(fig, "Émissions de CO2 du secteur de l'énergie — évolution", "Mt CO2e")


# ------------------------------------------------------------------
# Climatologie (notebook, cellules 38, 40)
# ------------------------------------------------------------------
def chart_temperatures(temperatures, villes_ordre, villes_sel, periode, metriques=("Max", "Min")):
    y0, y1 = periode
    sub = temperatures[(temperatures.Year >= y0) & (temperatures.Year <= y1) & (temperatures.villes.isin(villes_sel))]
    m = sub.groupby(["villes", "libellés"])["Value"].mean().unstack().reindex(
        [v for v in villes_ordre if v in villes_sel]
    )

    fig = go.Figure()
    if "Max" in metriques and "Températures maximales" in m.columns:
        fig.add_trace(go.Scatter(x=m.index, y=m["Températures maximales"], mode="lines+markers",
                                  name="T° maximale moyenne", line=dict(color=COLOR_ALERT, width=3)))
    if "Min" in metriques and "Températures minimales" in m.columns:
        fig.add_trace(go.Scatter(x=m.index, y=m["Températures minimales"], mode="lines+markers",
                                  name="T° minimale moyenne", line=dict(color=COLOR_BLUE, width=3)))
    if {"Max", "Min"}.issubset(metriques) and {"Températures maximales", "Températures minimales"}.issubset(m.columns):
        fig.add_trace(go.Scatter(
            x=list(m.index) + list(m.index[::-1]),
            y=list(m["Températures maximales"]) + list(m["Températures minimales"][::-1]),
            fill="toself", fillcolor="rgba(214,140,69,0.15)", line=dict(width=0), showlegend=False, hoverinfo="skip",
        ))
    fig.update_layout(xaxis_title=None)
    return _apply_layout(fig, f"Températures moyennes ({y0}-{y1}) — du Sud (Lomé) au Nord (Dapaong)", "Température (°C)")


def chart_tendance_rechauffement(tendances_s):
    colors = [COLOR_ALERT if v > 0 else COLOR_BLUE for v in tendances_s.values]
    fig = go.Figure(go.Bar(x=tendances_s.index, y=tendances_s.values, marker_color=colors))
    fig.add_hline(y=0, line_color="#333333", line_width=1)
    return _apply_layout(fig, "Tendance de la température maximale moyenne annuelle, 2013-2019 (indicatif)", "Tendance (°C / an)")


def chart_stats_climatiques(stats_df):
    """Visuel accompagnant le tableau de statistiques de tendance formelles : pente de
    Sen par station, avec la significativité du test de Mann-Kendall (seuil 5%) portée
    par la couleur — deux traces (plutôt qu'un marker_color par barre) pour que la
    légende explique la couleur au lieu de la laisser implicite."""
    df = stats_df.reset_index(drop=True)
    ordre_villes = list(df["Ville"])
    sig = df["p-value (MK)"] < 0.05

    fig = go.Figure()
    for masque, label, color in [(sig, "Tendance significative (p&lt;0,05)", COLOR_ALERT),
                                  (~sig, "Non significative", COLOR_GREY)]:
        sous = df[masque]
        if sous.empty:
            continue
        fig.add_trace(go.Bar(
            x=sous["Ville"], y=sous["Pente de Sen (°C/an)"], name=label, marker_color=color,
            customdata=sous["p-value (MK)"],
            text=[f"p={p:.3f}" for p in sous["p-value (MK)"]], textposition="outside",
            hovertemplate="<b>%{x}</b><br>Pente de Sen : %{y:.4f} °C/an<br>p-value (MK) : %{customdata:.3f}<extra></extra>",
        ))
    fig.add_hline(y=0, line_color="#333333", line_width=1)
    fig.update_xaxes(categoryorder="array", categoryarray=ordre_villes)
    return _apply_layout(
        fig, "Pente de Sen par station — test de Mann-Kendall (seuil de significativité 5%)",
        "Pente de Sen (°C/an)",
    )


# ------------------------------------------------------------------
# Réseau de centralité (notebook, cellule 51) — reproduction Plotly du réseau de proximité
# ------------------------------------------------------------------
def chart_reseau_centralite(forets, G, colorer_par="Région", top_n_labels=5):
    pos = {i: (forets.loc[i, "lon"], forets.loc[i, "lat"]) for i in G.nodes()}

    edge_x, edge_y = [], []
    for u, v in G.edges():
        edge_x += [pos[u][0], pos[v][0], None]
        edge_y += [pos[u][1], pos[v][1], None]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode="lines", line=dict(color="#c9c9c9", width=0.8),
                              hoverinfo="skip", showlegend=False))

    if colorer_par == "Région":
        for region, color in REGION_COLORS.items():
            sub = forets[forets.region_nom_bdd == region]
            fig.add_trace(go.Scatter(
                x=sub["lon"], y=sub["lat"], mode="markers", name=region,
                marker=dict(size=8 + 30 * sub["centralite_intermediarite"], color=color,
                            line=dict(color="white", width=1)),
                text=sub["etab_nom"], hovertemplate="%{text}<extra></extra>",
            ))
    else:
        fig.add_trace(go.Scatter(
            x=forets["lon"], y=forets["lat"], mode="markers", name="Centralité",
            marker=dict(size=8 + 30 * forets["centralite_intermediarite"], color=forets["centralite_intermediarite"],
                        colorscale="YlOrRd", showscale=True, colorbar=dict(title="Intermédiarité"),
                        line=dict(color="white", width=1)),
            text=forets["etab_nom"], hovertemplate="%{text}<extra></extra>", showlegend=False,
        ))

    top_idx = forets["centralite_intermediarite"].sort_values(ascending=False).head(top_n_labels).index
    fig.add_trace(go.Scatter(
        x=forets.loc[top_idx, "lon"], y=forets.loc[top_idx, "lat"], mode="text",
        text=forets.loc[top_idx, "etab_nom"].str.slice(0, 22), textposition="top center",
        showlegend=False, hoverinfo="skip",
    ))

    fig.update_layout(xaxis_title="Longitude", yaxis_title="Latitude")
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return _apply_layout(fig, "Réseau de proximité des 53 forêts classées (K=4 plus proches voisines)")


# ------------------------------------------------------------------
# Matrice de priorisation vulnérabilité x centralité (notebook, cellule 57)
# ------------------------------------------------------------------
def chart_matrice_priorisation(forets, colorer_par="Région"):
    rng = np.random.RandomState(42)
    jitter = rng.uniform(-1.6, 1.6, size=len(forets))
    x = forets["centralite_score"] + jitter
    med_x, med_y = forets["centralite_score"].median(), forets["score_vulnerabilite"].median()

    if colorer_par == "Région":
        fig = go.Figure()
        for region, color in REGION_COLORS.items():
            sub = forets[forets.region_nom_bdd == region]
            sub_x = sub["centralite_score"] + jitter[sub.index]
            fig.add_trace(go.Scatter(
                x=sub_x, y=sub["score_vulnerabilite"], mode="markers", name=region,
                marker=dict(size=8 + sub["area_km2"].clip(upper=60) * 0.9, color=color,
                            line=dict(color="white", width=1), opacity=0.8),
                text=sub["etab_nom"], hovertemplate="%{text}<extra></extra>",
            ))
    else:
        fig = go.Figure(go.Scatter(
            x=x, y=forets["score_vulnerabilite"], mode="markers",
            marker=dict(size=8 + forets["area_km2"].clip(upper=60) * 0.9, color=forets["area_km2"],
                        colorscale="Viridis", showscale=True, colorbar=dict(title="Superficie (km²)"),
                        line=dict(color="white", width=1), opacity=0.8),
            text=forets["etab_nom"], hovertemplate="%{text}<extra></extra>",
        ))

    fig.add_vline(x=med_x, line_dash="dash", line_color="#999999")
    fig.add_hline(y=med_y, line_dash="dash", line_color="#999999")
    fig.add_annotation(x=98, y=98, text="URGENCE CORRIDOR", showarrow=False, font=dict(color=COLOR_ALERT, size=11), xanchor="right")
    fig.add_annotation(x=2, y=98, text="FRAGILE ISOLÉE", showarrow=False, font=dict(color=COLOR_ACCENT, size=11), xanchor="left")
    fig.add_annotation(x=98, y=2, text="SURVEILLANCE", showarrow=False, font=dict(color=COLOR_BLUE, size=11), xanchor="right")
    fig.add_annotation(x=2, y=2, text="STABLE", showarrow=False, font=dict(color=COLOR_GREY, size=11), xanchor="left")

    fig.update_xaxes(title_text="Centralité structurelle (score 0-100, rôle de corridor)", range=[-4, 106])
    fig.update_yaxes(title_text="Vulnérabilité (score 0-100, taille + date inconnue)")
    return _apply_layout(fig, "Matrice de priorisation : vulnérabilité × centralité (taille = superficie)")


# ------------------------------------------------------------------
# Projection 2030 (notebook, cellule 71)
# ------------------------------------------------------------------
def chart_projection(nom, annees, valeurs, tableau_ml, meilleur, objectif=None):
    proj_2030 = tableau_ml[tableau_ml["Modèle"] == meilleur].iloc[0]["Projection retenue 2030"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=annees, y=valeurs, mode="lines+markers", name="Observé",
                              line=dict(color=COLOR_BLUE, width=2.5)))
    fig.add_trace(go.Scatter(x=[annees[-1], 2030], y=[valeurs[-1], proj_2030], mode="lines+markers",
                              name=f"Projection ({meilleur})", line=dict(color=COLOR_ALERT, width=2.2, dash="dash"),
                              marker=dict(symbol="x", size=10)))
    if objectif is not None:
        fig.add_hline(y=objectif, line_dash="dot", line_color=COLOR_PRIMARY,
                      annotation_text=f"Objectif 2030 ({objectif}%)", annotation_position="top left")
    fig.update_yaxes(range=[0, 105])
    return _apply_layout(fig, nom)


# ------------------------------------------------------------------
# Indice de priorité territoriale (notebook, cellule 75)
# ------------------------------------------------------------------
def chart_priorite_territoriale(reg_stats, poids_txt=""):
    sub = reg_stats.sort_values("indice_priorite", ascending=True)
    colors = [REGION_COLORS.get(r, COLOR_GREY) for r in sub.index]
    fig = go.Figure(go.Bar(x=sub["indice_priorite"], y=sub.index, orientation="h", marker_color=colors,
                            text=[f"{v:.1f}" for v in sub["indice_priorite"]], textposition="outside"))
    fig.update_layout(xaxis_title="Indice de priorité énergétique et environnementale (0-100)")
    title_html = "<b>Indice de priorité territoriale par région</b>"
    if poids_txt:
        title_html += f"<br><sub>{poids_txt}</sub>"
    fig.update_layout(title=_title_dict(title_html), **_LAYOUT_DEFAULTS)
    return fig
