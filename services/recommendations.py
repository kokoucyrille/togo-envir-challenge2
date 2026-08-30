"""
Recommandations opérationnelles — contenu repris tel quel du notebook de référence
(Section 17 "Recommandations opérationnelles"). Aucun impact quantitatif n'est inventé :
seules les familles d'actions et la matrice effort/impact qualitative du notebook sont
reproduites (cahier des charges, Section 23).
"""

CONSTATS = [
    {"constat": "Fracture électrique persistante",
     "donnee": "Accès rural : 25 % vs urbain : 96,5 % (2022) — écart en points qui se creuse malgré la progression rurale"},
    {"constat": "Réseau électrique peu fiable",
     "donnee": "94 % des entreprises touchées par des coupures (dernier point, 2016)"},
    {"constat": "Dépendance quasi totale à la biomasse",
     "donnee": "89,4 % des ménages cuisinent au bois/charbon (2017), cuisson propre rurale < 1 %"},
    {"constat": "Déforestation active",
     "donnee": "≈ 1 550 km² de forêt perdus depuis 1990 (~50 km²/an)"},
    {"constat": "Le secteur AFAT domine largement le bilan carbone du Togo",
     "donnee": "AFAT = 87,7 % des émissions de GES (Mt CO2e, 2018), Énergie = 6,2 % seulement"},
    {"constat": "Le Nord se réchauffe plus vite et est le moins protégé (nuancé)",
     "donnee": "Tendance de réchauffement la plus forte à Dapaong/Mango/Niamtougou, et 4 des 53 forêts classées en "
               "région Savanes — mais l'indice de couverture rapporté à la superficie régionale nuance ce constat brut"},
    {"constat": "Le réseau d'aires protégées a des nœuds critiques identifiables",
     "donnee": "L'analyse de centralité isole ~8-10 forêts « pont », dont la perte fragmenterait la connectivité régionale"},
]

FIL_CONDUCTEUR = (
    "L'électrification rurale par réseau centralisé n'est pas la priorité efficace. Le vrai nœud du problème est "
    "domestique et rural — cuisson au bois (qui alimente à la fois la déforestation et une partie croissante des "
    "émissions du secteur énergie) et absence totale d'alternative énergétique locale en zone rurale, singulièrement "
    "dans le Nord, où le climat se durcit et où la couverture en aires protégées est la plus faible."
)

# Structure Constat -> Enjeu -> Action -> Cible -> Impact attendu (cahier des charges, Section 23)
RECOMMANDATIONS = [
    {
        "axe": "A. Électrification décentralisée",
        "enjeu": "Le réseau centralisé reste peu fiable même en zone déjà connectée ; l'extension seule ne "
                 "résout pas la fracture rurale.",
        "actions": [
            "Prioriser les kits solaires domestiques et le solaire communautaire (mini-réseaux) dans les "
            "villages ruraux plutôt que l'extension du réseau centralisé.",
            "Cibler en priorité les villages à proximité immédiate des forêts classées prioritaires : "
            "l'investissement énergétique local réduit simultanément la pression de coupe de bois-énergie sur ces zones.",
        ],
        "cible": "Villages ruraux, en priorité à proximité des forêts prioritaires (carte de priorisation)",
        "impact_attendu": "Électrification + réduction de la pression sur le bois-énergie (qualitatif, non quantifié)",
    },
    {
        "axe": "B. Cuisson propre",
        "enjeu": "89,4 % des ménages dépendent du bois/charbon ; la cuisson propre rurale est quasi inexistante.",
        "actions": [
            "Déployer des foyers améliorés à bois/charbon (gain d'efficacité 40-60 %, technologie déjà éprouvée "
            "en Afrique de l'Ouest) en première étape, moins coûteuse que la conversion au gaz.",
            "Développer une filière GPL subventionnée ou biodigesteurs en zone périurbaine où la logistique de "
            "distribution est possible.",
            "Prioriser les campagnes de sensibilisation/subvention dans les régions Plateaux et Kara, où la "
            "pression combinée cuisson-déforestation est la plus documentée.",
        ],
        "cible": "Ménages ruraux ; régions Plateaux et Kara en priorité",
        "impact_attendu": "Réduction de la dépendance à la biomasse (qualitatif, non quantifié)",
    },
    {
        "axe": "C. Protection forestière ciblée",
        "enjeu": "Toutes les forêts classées ne présentent ni la même vulnérabilité ni le même rôle structurel "
                 "dans le réseau de proximité.",
        "actions": [
            "Concentrer la surveillance sur les forêts du quadrant « Urgence corridor » (vulnérables ET "
            "structurellement centrales).",
            "Traiter en priorité les forêts à date de création inconnue (Nsp/Nps/Jadis) : lancer un état des "
            "lieux cadastral/juridique, préalable indispensable à toute action de protection.",
            "Prioriser les régions selon l'indice de priorité territoriale plutôt que le seul décompte de forêts "
            "— la région Maritime ressort en tête sur ce score composite malgré un nombre élevé de forêts "
            "classées, du fait de sa très faible couverture rapportée à sa superficie.",
        ],
        "cible": "Forêts classées du quadrant « Urgence corridor » ; région Maritime en priorité territoriale",
        "impact_attendu": "Meilleur ciblage de la surveillance et de la protection (qualitatif, non quantifié)",
    },
    {
        "axe": "D. Suivi et gouvernance des données",
        "enjeu": "L'indice de vulnérabilité forestière reste une heuristique transparente, pas une mesure directe ; "
                 "plusieurs indicateurs clés datent de 2016-2022.",
        "actions": [
            "Mettre en place un suivi par télédétection (NDVI, alertes de déforestation type Global Forest Watch) "
            "pour transformer l'indice de vulnérabilité heuristique en mesure directe.",
            "Réactualiser la base des indicateurs d'accès à l'électricité et de fiabilité du réseau (dernier "
            "point utile : 2016-2022 selon l'indicateur) pour un pilotage à jour.",
        ],
        "cible": "Dispositif national de suivi énergie-environnement",
        "impact_attendu": "Fiabilisation et actualisation du pilotage (qualitatif, non quantifié)",
    },
]

# Matrice effort / impact qualitative (notebook, cellule 78) — AUCUN chiffre inventé
MATRICE_EFFORT_IMPACT = [
    {"action": "Kits solaires villages proches des forêts prioritaires", "effort": "Moyen",
     "impact": "Élevé (électrification + réduction pression bois)", "horizon": "Court terme"},
    {"action": "Foyers améliorés (diffusion large)", "effort": "Faible",
     "impact": "Élevé (réduction biomasse immédiate)", "horizon": "Court terme"},
    {"action": "État des lieux juridique des forêts « date inconnue »", "effort": "Faible",
     "impact": "Moyen (préalable à la protection)", "horizon": "Court terme"},
    {"action": "Surveillance des forêts « urgence corridor »", "effort": "Moyen",
     "impact": "Élevé (connectivité écologique)", "horizon": "Moyen terme"},
    {"action": "Filière GPL / biodigesteurs", "effort": "Élevé",
     "impact": "Élevé mais différé", "horizon": "Moyen-long terme"},
    {"action": "Renforcement du réseau électrique centralisé", "effort": "Élevé",
     "impact": "Moyen (fiabilité seule, ne résout pas la fracture rurale)", "horizon": "Long terme"},
]
