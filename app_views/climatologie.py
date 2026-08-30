"""Page 4/6 — Climatologie : dix stations, du Sud au Nord."""

import streamlit as st

from components.header import page_title
from components import charts as ch
from components import interpretation as itp
from services import indicators as ind
from utils.constants import VILLES_ORDRE


def render(data):
    page_title(
        "Climatologie — Dix stations, du Sud au Nord",
        question="Quels signaux d'évolution des températures observe-t-on sur les dix stations météorologiques ?",
        icon="thermostat",
    )

    temperatures = data["temperatures"]
    t_min, t_max = int(temperatures.Year.min()), int(temperatures.Year.max())

    st.markdown(
        f"""<div class="tg-notice">Période disponible : {t_min}-{t_max} ({t_max} partielle). Cette fenêtre est
        courte (≈7 ans) et ne doit pas être présentée comme une normale climatique de long terme — elle est
        interprétée ici comme un signal indicatif, conformément au test de Mann-Kendall.</div>""",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([3, 1])
    with c2:
        with st.container(border=True):
            st.markdown('<div class="tg-controls-label">Filtres</div>', unsafe_allow_html=True)
            villes_sel = st.multiselect("Stations", VILLES_ORDRE, default=VILLES_ORDRE, key="clim_villes")
            periode = st.slider("Période", t_min, t_max, (t_min, t_max), key="clim_periode")
            metriques = st.multiselect("Métrique", ["Max", "Min"], default=["Max", "Min"], key="clim_metriques")
    with c1:
        if villes_sel and metriques:
            st.plotly_chart(
                ch.chart_temperatures(temperatures, VILLES_ORDRE, villes_sel, periode, tuple(metriques)),
                width='stretch',
            )
        else:
            st.info("Sélectionnez au moins une station et une métrique.")

    itp.constat(
        "Le gradient Sud-Nord n'est pas parfaitement linéaire, mais la tendance de fond va dans le sens d'un "
        "climat plus chaud en s'éloignant de la côte, cohérent avec la littérature climatologique régionale."
    )

    st.markdown("---")
    st.markdown("#### Tendance annuelle (2013-2019, indicatif)")
    tendances_s = ind.tendances_par_ville(temperatures, VILLES_ORDRE)
    st.plotly_chart(ch.chart_tendance_rechauffement(tendances_s), width='stretch')

    st.markdown("#### Statistiques de tendance formelles")
    try:
        stats_df = ind.stats_climatiques(temperatures, VILLES_ORDRE)
    except Exception:
        stats_df = None

    if stats_df is None or stats_df.empty:
        st.warning(
            "Les statistiques de tendance formelles (Mann-Kendall, pente de Sen) n'ont pas pu être calculées "
            "pour les stations sélectionnées (série trop courte ou valeurs manquantes). La tendance annuelle "
            "indicative ci-dessus reste affichée."
        )
    else:
        st.plotly_chart(ch.chart_stats_climatiques(stats_df), width='stretch')
        st.dataframe(stats_df, width='stretch', hide_index=True)
        erreurs = stats_df.attrs.get("erreurs")
        if erreurs:
            st.caption(f"Station(s) non calculable(s) et omise(s) du tableau : {'; '.join(erreurs)}.")

        n_sig = (stats_df["p-value (MK)"] < 0.05).sum()
        villes_sig = ", ".join(stats_df.loc[stats_df["p-value (MK)"] < 0.05, "Ville"])
        itp.message_cle(
            f"Seules {n_sig}/{len(stats_df)} station(s) présentent une tendance Mann-Kendall statistiquement "
            f"significative au seuil de 5% : {villes_sig if villes_sig else 'aucune'}. Pour les autres stations, la "
            "pente affichée est un signal indicatif, pas une preuve statistique de réchauffement local sur cette "
            "fenêtre de 7 ans."
        )
    st.caption(
        "Vocabulaire retenu : on parle d'association, de relation observée, de tendance ou de signal — jamais de "
        "causalité (« provoque », « entraîne nécessairement ») sauf démonstration statistique explicite."
    )
