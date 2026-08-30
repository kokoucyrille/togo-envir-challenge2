"""Page "À propos" — identité de l'auteur uniquement, séparée de la barre latérale
(qui reste réservée à la navigation) et des pages d'analyse."""

import base64

import streamlit as st

from components.header import page_title
from utils.constants import AUTEUR, PHOTO_AUTEUR_PATH
from utils.icons import icon_svg


def _img_to_base64(path):
    if not path.exists():
        return None
    return base64.b64encode(path.read_bytes()).decode()


def render(data):
    page_title("À propos de l'auteur", icon="info")

    col_photo, col_bio = st.columns([1, 2.4], gap="large")

    with col_photo:
        photo_b64 = _img_to_base64(PHOTO_AUTEUR_PATH)
        if photo_b64:
            st.markdown(
                f'<img src="data:image/png;base64,{photo_b64}" '
                'style="width:100%;max-width:220px;aspect-ratio:1/1;border-radius:16px;'
                'object-fit:cover;border:1px solid #E3E7E1;box-shadow:0 4px 14px rgba(16,24,20,0.12);">',
                unsafe_allow_html=True,
            )

    with col_bio:
        st.markdown(f"### {AUTEUR['nom']}")
        st.markdown(
            f'<div style="color:#6C757D;font-weight:600;font-size:0.95rem;margin-top:-0.6rem;margin-bottom:0.7rem;">'
            f'{AUTEUR["titre"]}</div>',
            unsafe_allow_html=True,
        )
        st.write(AUTEUR["bio"])

        whatsapp_href = "https://wa.me/" + "".join(c for c in AUTEUR["whatsapp"] if c.isdigit())
        contacts = [
            ("link", "Profil LinkedIn", AUTEUR["linkedin"]),
            ("mail", AUTEUR["email"], f"mailto:{AUTEUR['email']}"),
            ("github", "GitHub", AUTEUR["github"]),
            ("message-circle", AUTEUR["whatsapp"], whatsapp_href),
        ]
        badges = "".join(
            f'<a href="{href}" target="_blank" style="text-decoration:none;">'
            '<span style="display:inline-flex;align-items:center;gap:6px;font-size:0.85rem;'
            'color:#1B4332;font-weight:600;border:1px solid #1B4332;border-radius:18px;padding:5px 16px;">'
            f'{icon_svg(icon, size=15, color="#1B4332")} {label}</span></a>'
            for icon, label, href in contacts
        )
        st.markdown(
            f'<div style="display:flex;flex-wrap:wrap;gap:10px;margin-top:0.6rem;">{badges}</div>',
            unsafe_allow_html=True,
        )
