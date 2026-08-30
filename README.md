# Diagnostic Énergie, Climat & Forêts du Togo

**Plateforme territoriale d'aide à la décision publique — Horizon 2030**

Application Streamlit développée pour le Data Challenge 2 — Environnement, sur le défi
*« Vers une énergie propre et inclusive au Togo »*.

---

## Présentation

Cette application transforme en outil décisionnel interactif l'analyse conduite dans le
notebook **`Analyse_Energie_Climat_Forets_Togo_REVISE.ipynb`**, qui reste la **source de
vérité analytique unique** du projet. Aucune donnée, KPI, corrélation, causalité,
territoire prioritaire, recommandation ou source n'est ajouté au-delà de ce que ce
notebook établit.

## Problématique

Le Togo cumule une fracture électrique ville/campagne persistante, une dépendance quasi
générale des ménages au bois-énergie, un recul mesurable du couvert forestier, et un
bilan de gaz à effet de serre dominé par le secteur agriculture-foresterie plutôt que par
l'énergie. L'application permet de répondre en quelques minutes à cinq questions :

1. **Électrification** — quelle est l'ampleur de la fracture urbain/rural ?
2. **Biomasse** — quelle dépendance au bois-énergie, et quelle pression sur les forêts ?
3. **Émissions** — quelle contribution du secteur énergétique aux émissions ?
4. **Climat** — quels signaux d'évolution des températures ?
5. **Action territoriale** — quels territoires ou forêts sont prioritaires ?

## Objectifs

- Reproduire fidèlement les résultats du notebook dans une interface professionnelle.
- Distinguer systématiquement donnée observée / actualisation / projection statistique.
- Offrir une cartographie et une priorisation territoriale exploitables pour la décision.
- Formuler des recommandations opérationnelles directement reliées aux données.

## Données

Six jeux de données exploités (voir l'onglet **Qualité & méthodologie** de l'application
pour le détail — sources, périodes, unités, valeurs manquantes, doublons) :

| Dataset | Source | Période exploitée |
|---|---|---|
| Accès électricité, cuisson propre, combustibles, forêt, fiabilité réseau | Banque mondiale (WDI) | 1990-2022 |
| Émissions de CO2, secteur énergie | Banque mondiale / Climate Watch | 1970-2022 |
| Bilan GES sectoriel national | Inventaire national des émissions de GES | 2018 (année unique) |
| Températures, 10 stations | Service météorologique national du Togo | 2013-2019 |
| Forêts classées / zones protégées | Cadastre national (portail géospatial togolais) | Extraction 23/12/2024 |
| Dictionnaire de données du cadastre | idem | Description des champs (non analytique) |

Un fichier `data/zones-protegees-forets-classees.csv` est un **dictionnaire de données**
(description des champs), à distinguer du véritable fichier géographique des 53 forêts
classées (`file-zones-protegees-forets-classees-...csv`).

**Points d'attention explicitement traités par le notebook et repris ici :**
- Le bilan GES sectoriel est fourni en **Gg CO2e**, converti en **Mt CO2e** (÷1000) —
  jamais mélangé avec l'unité source.
- Les **53 forêts classées** du cadastre sont un sous-ensemble du dispositif national
  d'aires protégées (WDPA/Protected Planet recense 83 désignations nationales), pas son
  inventaire exhaustif.
- La fenêtre climatique (2013-2019) est trop courte pour une normale climatique de long
  terme : les tendances sont présentées comme un signal indicatif, appuyé par un test de
  Mann-Kendall formel.

## Méthodologie

- **Centralité structurelle** : graphe de proximité géographique (k plus proches
  voisins, k=4 par défaut), avec test de robustesse k=3 à 6. Terminologie imposée :
  « centralité structurelle basée sur la proximité géographique », jamais
  « centralité écologique ».
- **Indice de vulnérabilité par forêt** : combinaison pondérée (taille, date de création
  inconnue, centralité) — un indice de priorisation/proxy, pas une mesure absolue.
- **Indice de priorité territoriale (régional)** : combine des variables mesurées
  régionalement (vulnérabilité et centralité moyennes, couverture protégée) avec un
  **proxy national** appliqué uniformément pour l'accès électrique et la dépendance à la
  biomasse, faute de données régionalisées — signalé explicitement dans l'application.
- **Machine Learning** : régression linéaire, Random Forest, Gradient Boosting, comparés
  par validation temporelle *walk-forward* (jamais de k-fold aléatoire, qui biaiserait
  l'évaluation d'une tâche de prévision). Le modèle retenu minimise la RMSE de validation.
  Les projections en % sont bornées à [0, 100].

## Architecture

```
togo-energy-dashboard/
├── app.py                          # Point d'entrée
├── requirements.txt
├── app_views/                       # Six pages de l'application (nommé "app_views" et
│                                     #  non "pages" pour éviter la détection automatique
│                                     #  de multipage de Streamlit, qui doublonnait la
│                                     #  navigation — voir Note technique ci-dessous)
│   ├── accueil.py
│   ├── electrification.py
│   ├── biomasse_carbone.py
│   ├── climatologie.py
│   ├── cartographie_priorisation.py
│   └── recommandations_2030.py
├── components/                     # Composants d'interface réutilisables
│   ├── header.py, sidebar.py, kpi_cards.py, filters.py, charts.py, maps.py, interpretation.py
├── services/                       # Logique analytique (fidèle au notebook)
│   ├── data_loader.py, indicators.py, analysis.py, forecasting.py, recommendations.py
├── utils/                          # Constantes, styles, fonctions utilitaires
│   ├── constants.py, styles.py, helpers.py
├── data/                           # Jeux de données sources (CSV)
└── assets/images/                  # Ressources visuelles
```

Chaque fonction de `services/` correspond à une cellule identifiée du notebook de
référence — voir les commentaires en tête de chaque fichier.

**Note technique — navigation :** l'application utilise l'API native `st.navigation` /
`st.Page` (voir `utils/navigation.py`), construite une seule fois et partagée par
`app.py`. Le dossier des pages est nommé `app_views/` plutôt que `pages/` : un dossier
littéralement nommé `pages/` déclenche la détection automatique historique de Streamlit
(multipage app), qui aurait ajouté un second menu de navigation en plus de celui géré
explicitement — d'où le renommage.

## Identité visuelle

- Logo du Ministère affiché via `st.logo()` (API native Streamlit) — coin supérieur
  gauche de l'application et de la barre latérale (`assets/images/logo_ministere.png`),
  agrandi et centré en haut de la barre latérale via CSS ciblé (`utils/styles.py`).
  Ce placement natif est le plus robuste pour garantir que le logo apparaisse
  au-dessus du menu de navigation, quel que soit l'ordre d'appel dans le script (le
  widget de navigation natif réserve toujours le haut de la barre latérale).
- Le portrait de l'auteur n'apparaît plus dans la barre latérale (présente sur toutes
  les pages) : il est réservé à la page dédiée « À propos » (`app_views/a_propos.py`,
  accessible via un bouton en bas de barre latérale et via la navigation groupée),
  avec le reste des informations d'identité — `assets/images/auteur_cyrille.png`,
  configurable dans `utils/constants.py` (dict `AUTEUR`).
- Navigation groupée en deux sections (« Analyse » / « Informations ») via le mode
  dict natif de `st.navigation` (voir `utils/navigation.py`).
- Illustration générée (`assets/images/hero_energie_afrique.svg`, vectorielle,
  palette du projet) en bannière de la page d'accueil.
- Icônes SVG intégrées (`utils/icons.py`), sans dépendance à une police externe.

## Note sur la carte interactive (Folium)

Les cartes interactives (onglets « Carte interactive » et « Centralité structurelle »
de la page Cartographie & Priorisation) utilisent Folium/Leaflet, qui charge son fond
de carte (tuiles CartoDB) et sa bibliothèque JS **depuis internet** au moment de
l'affichage — comme toute carte Folium. Une connexion internet normale est donc requise
au lancement local pour que les cartes s'affichent correctement ; ce n'est pas
spécifique à ce projet, c'est le fonctionnement standard de Folium.

## Fonctionnalités

- Six pages : Accueil, Électrification, Biomasse & Carbone, Climatologie, Cartographie &
  Priorisation, Recommandations & 2030.
- Carte interactive (Folium) : couches par région, forêts prioritaires, nœuds de
  centralité, densité, stations climatiques — filtrable par région, aire, vulnérabilité,
  centralité.
- Graphiques interactifs (Plotly) : zoom, info-bulles, légendes cliquables.
- Filtres utiles uniquement (période, station, secteur, région, seuils, pondérations) —
  jamais de filtre décoratif.
- Chaque KPI affiche systématiquement **valeur + unité + année + source**.
- Tout proxy ou estimation dérivée est signalé explicitement comme tel.
- Toute projection est accompagnée de l'avertissement : *« Scénario statistique basé sur
  les tendances historiques — ne constitue pas une prévision officielle. »*

## Validation interne (notebook vs application)

Un script de validation (`tools/validate_against_notebook.py`) recalcule, avec les
services de l'application, 18 indicateurs clés et les compare aux valeurs extraites de
l'exécution réelle du notebook de référence (accès électricité, gap urbain/rural,
biomasse, déforestation, bilan GES, couverture forestière régionale, indice de priorité
territoriale). Exécution :

```bash
python tools/validate_against_notebook.py
```

Résultat à la dernière exécution : **18/18 éléments conformes** (écarts résiduels dus
uniquement aux arrondis d'affichage du notebook, tolérance 5% appliquée). Aucun résultat
n'est déclaré conforme sans cette vérification numérique explicite.

## Installation

```bash
git clone <url-du-repo>
cd togo-energy-dashboard
python -m venv venv
source venv/bin/activate      # Windows : venv\Scripts\activate
pip install -r requirements.txt
```

## Lancement

```bash
streamlit run app.py
```

L'application s'ouvre sur `http://localhost:8501`. Tous les chemins sont relatifs : le
projet fonctionne après un simple `git clone` suivi de `streamlit run app.py`, sans
configuration spécifique à une machine.

## Sources

Voir l'onglet **Recommandations & 2030 → Qualité & méthodologie** dans l'application pour
la table complète (dataset, source, URL, année). Sources principales :

- Banque mondiale — World Development Indicators (WDI)
- Banque mondiale / Climate Watch (CO2 secteur énergie)
- Inventaire national des émissions de GES du Togo (2018)
- Service météorologique national du Togo
- Cadastre national des forêts classées (portail géospatial togolais)
- Protected Planet / World Database on Protected Areas (WDPA) — comparaison de périmètre
- Pacte National de l'Énergie du Togo (sept. 2025) / Banque mondiale, Mission 300 —
  objectifs officiels 2030

## Limites

- Plusieurs indicateurs datent de 2016 à 2022 selon la source ; le bilan GES sectoriel
  est une année unique (2018), sans tendance intersectorielle calculable.
- Le graphe de centralité modélise une proximité géographique, pas une connectivité
  écologique mesurée.
- L'indice de priorité territoriale régional s'appuie sur un proxy national pour l'accès
  électrique et la dépendance à la biomasse, faute de données régionalisées.
- Les séries climatiques (2013-2019) sont trop courtes pour une normale climatique de
  long terme.
- Aucune analyse de cette application n'établit de lien de causalité : les résultats sont
  présentés en termes d'association, de tendance ou de signal.

## Avertissement sur les projections

Toutes les projections à l'horizon 2030 sont des **scénarios statistiques** construits à
partir des tendances historiques disponibles. Elles ne constituent **en aucun cas** une
prévision officielle du gouvernement togolais, et sont systématiquement présentées avec
leur méthode, leurs métriques de validation (MAE, RMSE, R²) et leur écart à l'objectif
officiel lorsque celui-ci existe et est comparable.
