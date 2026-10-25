# Logiciel de Génération Automatique de Vues Orthogonales (Dessin Technique ISO)

## Présentation du Projet
Application web complète permettant d'importer une image d'un objet réel, d'analyser sa géométrie 3D (forme, dimensions, cavités/trous) par vision par ordinateur, et de générer automatiquement ses **six vues orthogonales synchronisées** selon les normes de dessin technique (NF EN ISO 5456-2, NF EN ISO 128, NF EN ISO 7200, NF EN ISO 5457).

Le logiciel exporte un fichier **SVG vectoriel A4** conforme (unités mm physiques, cartouche normalisé, symbole de projection du 1er ou 3ème dièdre, traits forts/interrompus/axes de symétrie, cotations).

---

## Fonctionnalités Clés

1. **Zone A — Importation & Analyse Image :**
   - Support des images PNG, JPG, JPEG, WEBP par glisser-déposer.
   - Outil de rotation à 90°.
   - Analyse par vision par ordinateur (OpenCV) avec calcul d'un indice de confiance géométrique et détection des avertissements de reconstruction 3D.

2. **Zone B — Modèle 3D & Dimensions Connues :**
   - Formes géométriques paramétriques : Pavé droit, Cylindre, Plaque avec trou débouchant, Bloc étagé (L).
   - Saisie et calibration des dimensions réelles (Largeur X, Hauteur Y, Profondeur Z, Diamètre de trou).
   - Personnalisation du titre de la pièce.

3. **Zone C — Options ISO & Génération :**
   - Choix de la méthode de projection : **1er Dièdre (Projection Européenne ISO)** ou **3ème Dièdre (Projection Américaine)**.
   - Disposition automatique des 6 vues :
     - *1er Dièdre :* Vue de dessus sous la vue de face, vue de dessous au-dessus, vue de gauche à droite, vue de droite à gauche, vue arrière.
   - Choix de l'orientation de la feuille A4 (Paysage / Portrait).
   - Choix de l'échelle normalisée (2:1, 1:1, 1:2, 1:5, 1:10).

4. **Zone D — Visualisation & Édition Interactive :**
   - Prévisualisation vectorielle dynamique de la feuille A4.
   - Zoom (+ / -) et navigation.
   - Outil d'ajout de lignes de cote (cotations ISO) sur n'importe quelle vue.

5. **Zone E — Exportation SVG A4 Vectoriel :**
   - Fichier SVG 100% vectoriel structuré avec calques/groupes ISO (`contours-visibles`, `arretes-cachees`, `axes-symetrie`, `cartouche-iso-7200`, `cotations`).
   - Cartouche d'ingénierie ISO 7200 complet avec le symbole normalisé de projection du premier ou troisième angle.

---

## Architecture Technique

- **Backend :** Python 3.12 / FastAPI, OpenCV, NumPy, Pytest.
- **Frontend :** React 19 / TypeScript, Vite, Lucide-React, CSS3 moderne responsive.
- **Moteur Géométrique & Projection :**
  - Modélisation CAD 3D paramétrique (`backend/app/geometry`).
  - Moteur de projection orthogonale 3D -> 2D avec calcul exact de la visibilité des arêtes (traits pleins forts pour le contour visible, traits interrompus fins pour les arêtes cachées, traits mixtes pour les axes de symétrie) (`backend/app/projection`).
  - Générateur d'export SVG A4 physique (`backend/app/export`).

---

## Instructions d'Installation et d'Exécution Locales

### Préréquis
- Python 3.12+
- Node.js 20+ et npm

### 1. Démarrage du Backend (FastAPI)

```bash
# Activation de l'environnement virtuel et installation des dépendances
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Lancement du serveur API FastAPI (sur le port 8000)
PYTHONPATH=backend uvicorn app.api.main:app --reload --port 8000
```

### 2. Démarrage du Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```
Ouvrez votre navigateur à l'adresse `http://localhost:5173`.

---

## Exécution des Tests Unitaires et de Validation

Le projet comprend une suite complète de tests unitaires validant la géométrie, l'alignement des 6 vues, le tracé des arêtes cachées, le respect des calques SVG et l'API FastAPI :

```bash
source venv/bin/activate
PYTHONPATH=backend pytest backend/tests
```

---

## Exemples et Livrables de Test

- **Images de test d'exemples :** situées dans `sample_data/images/`
  - `cube_sample.png`
  - `cylinder_sample.png`
  - `plate_with_hole_sample.png`
- **Exemples de fichiers SVG A4 générés :** situés dans `sample_data/outputs/`
  - `pave_droit_6_vues.svg`
  - `cylindre_6_vues.svg`
  - `plaque_percee_6_vues.svg`
