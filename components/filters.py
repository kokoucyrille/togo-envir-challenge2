"""
Widgets de filtre — repris de l'esprit des filtres ipywidgets du notebook, transformés
en widgets Streamlit natifs. Chaque filtre correspond à une interaction déjà présente
dans le notebook (cahier des charges, Sections 21-22) : aucun filtre artificiel.
"""

import streamlit as st


def periode_slider(label, annee_min, annee_max, key):
    return st.slider(label, min_value=int(annee_min), max_value=int(annee_max),
                      value=(int(annee_min), int(annee_max)), key=key)


def villes_multiselect(villes_ordre, key):
    return st.multiselect("Stations", options=villes_ordre, default=villes_ordre, key=key)


def metrique_multiselect(key):
    return st.multiselect("Métrique", options=["Max", "Min"], default=["Max", "Min"], key=key)


def regions_multiselect(regions, key):
    return st.multiselect("Régions", options=list(regions), default=list(regions), key=key)


def poids_sliders(defaults, key_prefix):
    """`defaults` : dict {label_court: valeur_par_defaut}. Retourne dict des valeurs choisies."""
    cols = st.columns(len(defaults))
    out = {}
    for col, (name, default) in zip(cols, defaults.items()):
        with col:
            out[name] = st.slider(name, 0, 100, default, step=5, key=f"{key_prefix}_{name}")
    return out
