"""Petites fonctions de formatage partagées par les pages et composants."""


def fmt_pct(value, decimals=1):
    if value is None:
        return "n/d"
    return f"{value:.{decimals}f}%".replace(".", ",")


def fmt_num(value, decimals=0, unit=""):
    if value is None:
        return "n/d"
    txt = f"{value:,.{decimals}f}".replace(",", " ").replace(".", ",")
    return f"{txt} {unit}".strip()


def source_caption(source, year=None):
    """Légende standard 'Source — année' affichée sous chaque graphique/KPI (Section 7 du cahier des charges)."""
    if year is not None:
        return f"Source : {source} — {year}"
    return f"Source : {source}"


def kpi_caption(value_str, year, source):
    """Format 'valeur — année — source' imposé par le cahier des charges (Section 29)."""
    return f"{value_str} — {year} — {source}"


def missing_indicator_notice(label):
    """Message à afficher quand un indicateur n'est pas disponible plutôt que de l'inventer
    (cahier des charges, Section 2 : 'ne pas afficher l'indicateur ou signaler explicitement
    qu'il n'est pas disponible')."""
    return f"Indicateur non disponible dans les données du notebook : « {label} »."
