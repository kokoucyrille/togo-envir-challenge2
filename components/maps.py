"""
Carte interactive Folium — reproduit fidèlement la carte du notebook (cellule 60) :
couches par région, top prioritaires (vulnérabilité), nœuds de connectivité
(centralité), densité (heatmap), stations climatiques. Technologie Folium retenue
car elle reproduit fidèlement la carte du notebook (cahier des charges, Section 32).
"""

import numpy as np
import folium
from folium.plugins import HeatMap, Fullscreen, MiniMap

from utils.constants import REGION_COLORS, COLOR_PURPLE


def construire_carte(forets_df, top_prioritaires, top_centralite, villes_coords, tendances_s, moyennes,
                      afficher_heatmap=True):
    m = folium.Map(location=[8.6, 1.05], zoom_start=7, tiles="CartoDB positron", control_scale=True)
    Fullscreen(position="topleft").add_to(m)
    MiniMap(toggle_display=True).add_to(m)

    # Couches par région
    for region, color in REGION_COLORS.items():
        sub = forets_df[forets_df.region_nom_bdd == region]
        if not len(sub):
            continue
        fg = folium.FeatureGroup(name=f"Forêts – {region} (n={len(sub)})", show=True)
        for _, r in sub.iterrows():
            popup_html = (f"<b>{r['etab_nom']}</b><br>Région : {r['region_nom_bdd']}<br>"
                          f"Commune : {r['commune_nom_bdd']}<br>Superficie : {r['area_km2']:.2f} km²<br>"
                          f"Créée : {r['etab_creation_date']}<br>"
                          f"Vulnérabilité : {r['score_vulnerabilite']:.0f}/100 · Centralité : {r['centralite_score']:.0f}/100")
            folium.GeoJson(
                r.geometry,
                style_function=lambda x, c=color: {"fillColor": c, "color": c, "weight": 1, "fillOpacity": 0.45},
                highlight_function=lambda x: {"weight": 2.5, "fillOpacity": 0.7},
                tooltip=r["etab_nom"],
                popup=folium.Popup(popup_html, max_width=280),
            ).add_to(fg)
        fg.add_to(m)

    # Couche Top prioritaires (vulnérabilité)
    fg_top = folium.FeatureGroup(name=f"Top {len(top_prioritaires)} prioritaires (vulnérabilité)", show=True)
    for _, r in top_prioritaires.iterrows():
        folium.Marker(
            [r["lat"], r["lon"]], icon=folium.Icon(color="red", icon="star", prefix="fa"),
            popup=folium.Popup(f"<b>{r['etab_nom']}</b><br>Région : {r['region_nom_bdd']}<br>"
                                f"Superficie : {r['area_km2']:.2f} km²<br>Créée : {r['etab_creation_date']}<br>"
                                f"<b>Indice de vulnérabilité : {r['score_vulnerabilite']:.0f}/100</b>", max_width=260),
        ).add_to(fg_top)
    fg_top.add_to(m)

    # Couche nœuds de connectivité (centralité)
    fg_hub = folium.FeatureGroup(name=f"Top {len(top_centralite)} nœuds de connectivité (centralité)", show=False)
    for _, r in top_centralite.iterrows():
        folium.CircleMarker(
            [r["lat"], r["lon"]], radius=6 + r["centralite_score"] / 9, color=COLOR_PURPLE, weight=2,
            fill=True, fill_color=COLOR_PURPLE, fill_opacity=0.55,
            popup=folium.Popup(f"<b>{r['etab_nom']}</b><br>Région : {r['region_nom_bdd']}<br>"
                                f"<b>Centralité structurelle : {r['centralite_score']:.0f}/100</b><br>"
                                f"Rôle : nœud de corridor entre massifs forestiers (proximité géographique)", max_width=260),
        ).add_to(fg_hub)
    fg_hub.add_to(m)

    # Heatmap de densité
    if afficher_heatmap and len(forets_df):
        fg_heat = folium.FeatureGroup(name="Densité des forêts classées", show=False)
        HeatMap(list(zip(forets_df["lat"], forets_df["lon"])), radius=28, blur=18, min_opacity=0.35).add_to(fg_heat)
        fg_heat.add_to(m)

    # Stations climatiques
    fg_villes = folium.FeatureGroup(name="Stations climatiques (10 villes)", show=True)
    for ville, (lon, lat) in villes_coords.items():
        trend = tendances_s.get(ville, 0)
        tmax = moyennes.loc[ville, "Températures maximales"] if ville in moyennes.index else float("nan")
        icon_color = "red" if trend > 0.03 else ("lightgray" if abs(trend) <= 0.03 else "blue")
        folium.Marker(
            [lat, lon], icon=folium.Icon(color=icon_color, icon="thermometer-half", prefix="fa"),
            popup=folium.Popup(f"<b>{ville}</b><br>T° max. moyenne : {tmax:.1f} °C<br>"
                                f"Tendance 2013-2019 : {trend:+.3f} °C/an", max_width=220),
        ).add_to(fg_villes)
    fg_villes.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    return m


def construire_carte_centralite(forets_df, G, colorer_par="Région"):
    """Carte Folium (fond réel du Togo) du réseau de proximité géographique entre les
    53 forêts classées : arêtes du graphe + nœuds dimensionnés/colorés par centralité
    d'intermédiarité. Remplace le nuage de points abstrait par une vraie carte du Togo,
    conformément à la demande explicite sur la page Cartographie & Priorisation."""
    m = folium.Map(location=[8.6, 1.05], zoom_start=7, tiles="CartoDB positron", control_scale=True)
    Fullscreen(position="topleft").add_to(m)

    # Arêtes du graphe de proximité
    fg_edges = folium.FeatureGroup(name="Liens de proximité (K=4)", show=True)
    for u, v in G.edges():
        pu = (forets_df.loc[u, "lat"], forets_df.loc[u, "lon"])
        pv = (forets_df.loc[v, "lat"], forets_df.loc[v, "lon"])
        folium.PolyLine([pu, pv], color="#9AA5A0", weight=1.2, opacity=0.7).add_to(fg_edges)
    fg_edges.add_to(m)

    # Nœuds (forêts), dimensionnés et colorés par centralité d'intermédiarité
    score_max = max(forets_df["centralite_intermediarite"].max(), 1e-9)
    fg_nodes = folium.FeatureGroup(name="Forêts (taille = centralité)", show=True)
    for _, r in forets_df.iterrows():
        intensite = r["centralite_intermediarite"] / score_max
        rayon = 4 + 14 * intensite
        couleur = REGION_COLORS.get(r["region_nom_bdd"], "#6C757D") if colorer_par == "Région" else _couleur_centralite(intensite)
        folium.CircleMarker(
            [r["lat"], r["lon"]], radius=rayon, color=couleur, weight=1.5,
            fill=True, fill_color=couleur, fill_opacity=0.75,
            popup=folium.Popup(
                f"<b>{r['etab_nom']}</b><br>Région : {r['region_nom_bdd']}<br>"
                f"Centralité structurelle (score 0-100) : {r['centralite_score']:.0f}<br>"
                f"Centralité d'intermédiarité (brute) : {r['centralite_intermediarite']:.4f}",
                max_width=260,
            ),
            tooltip=r["etab_nom"],
        ).add_to(fg_nodes)
    fg_nodes.add_to(m)

    # Étiquettes des forêts les plus centrales
    top_idx = forets_df["centralite_intermediarite"].sort_values(ascending=False).head(6).index
    fg_labels = folium.FeatureGroup(name="Étiquettes — top 6 nœuds de corridor", show=True)
    for i in top_idx:
        r = forets_df.loc[i]
        folium.Marker(
            [r["lat"], r["lon"]],
            icon=folium.DivIcon(html=f"""<div style="font-size:10px;font-weight:600;color:#1B4332;
                                          background:rgba(255,255,255,0.75);border-radius:3px;
                                          padding:1px 4px;white-space:nowrap;">{r['etab_nom'][:24]}</div>""")
        ).add_to(fg_labels)
    fg_labels.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    return m


def _couleur_centralite(intensite):
    """Dégradé simple bleu -> rouge selon l'intensité de centralité (0-1)."""
    r = int(30 + intensite * 180)
    g = int(94 - intensite * 60)
    b = int(140 - intensite * 120)
    return f"#{max(0,min(r,255)):02x}{max(0,min(g,255)):02x}{max(0,min(b,255)):02x}"
