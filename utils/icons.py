"""
Icônes SVG intégrées (autonomes, aucune dépendance réseau) — remplace l'usage de la
police Material Symbols via Google Fonts CDN, qui s'est révélée peu fiable en pratique
(non chargée dans les délais, notamment en environnement sans accès direct au CDN).
Style minimaliste à trait unique (inspiré Lucide/Feather), hérite la couleur via
`currentColor` pour s'intégrer à la palette du projet.
"""

_PATHS = {
    "home": '<path d="M3 11l9-8 9 8"/><path d="M5 10v10h14V10"/><path d="M9 20v-6h6v6"/>',
    "bolt": '<path d="M13 2 4 14h7l-1 8 9-12h-7z" stroke-linejoin="round"/>',
    "flame": '<path d="M12 2c1 4-4 5-4 9a4 4 0 0 0 8 0c0-1-.5-2-1-3 1 0 2 1 2 3a5 5 0 0 1-10 0c0-5 5-6 5-9z" stroke-linejoin="round"/>',
    "thermostat": '<path d="M10 13V4a2 2 0 1 1 4 0v9a4 4 0 1 1-4 0z"/><circle cx="12" cy="17" r="1.4"/>',
    "map": '<path d="M9 3 3 5v16l6-2 6 2 6-2V3l-6 2-6-2z" stroke-linejoin="round"/><path d="M9 3v16"/><path d="M15 5v16"/>',
    "checklist": '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8.5 11.5l2 2 4-4"/><path d="M8 17h8"/>',
    "distance": '<path d="M8 7 3 12l5 5"/><path d="M16 7l5 5-5 5"/><path d="M3 12h18"/>',
    "cloud": '<path d="M17 18a4 4 0 0 0 0-8 5 5 0 0 0-9.6-1.5A4.5 4.5 0 0 0 7 18h10z" stroke-linejoin="round"/>',
    "forest": '<path d="M12 2 7 9h3l-4 6h4l-3 5h10l-3-5h4l-4-6h3z" stroke-linejoin="round"/><path d="M12 22v-4"/>',
    "link": '<path d="M10 14a5 5 0 0 1 0-7l3-3a5 5 0 0 1 7 7l-2 2"/><path d="M14 10a5 5 0 0 1 0 7l-3 3a5 5 0 0 1-7-7l2-2"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6"/><path d="M12 7.5v.01"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 20c1.5-4.2 5-6 8-6s6.5 1.8 8 6"/>',
    "filter": '<path d="M4 5h16"/><path d="M7 12h10"/><path d="M10 19h4"/>',
    "network": '<circle cx="12" cy="5" r="2.2"/><circle cx="5" cy="19" r="2.2"/><circle cx="19" cy="19" r="2.2"/><path d="M12 7.2 6.3 17.1"/><path d="M12 7.2l5.7 9.9"/><path d="M7.2 19h9.6"/>',
    "shield": '<path d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6l7-3z" stroke-linejoin="round"/>',
    "layers": '<path d="M12 3 3 8l9 5 9-5-9-5z" stroke-linejoin="round"/><path d="M3 13l9 5 9-5" stroke-linejoin="round"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 7L2 7"/>',
    "github": '<path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22" stroke-linejoin="round"/>',
    "message-circle": '<path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" stroke-linejoin="round"/>',
}


def icon_svg(name, size=18, color="currentColor", stroke_width=2):
    """Retourne une balise <svg> inline prête à insérer dans du HTML/Markdown Streamlit."""
    path = _PATHS.get(name, "")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke_width}" '
        f'stroke-linecap="round" style="vertical-align:-3px;">{path}</svg>'
    )
