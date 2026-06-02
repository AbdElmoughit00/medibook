# MediBook — Projet Django

MediBook est une application Django de gestion de rendez-vous médicaux. Le projet contient trois espaces principaux : patient, médecin et administrateur.

## Fonctionnalités

- Authentification patient : inscription, connexion, déconnexion.
- Annuaire des médecins avec recherche par nom et filtre par spécialité.
- Réservation de rendez-vous selon les disponibilités du médecin.
- Espace patient : rendez-vous à venir, historique, annulations.
- Espace médecin : rendez-vous du jour, prochains rendez-vous, changement de statut.
- Dashboard administrateur : statistiques simples par statut et par spécialité.
- Orientation médicale indicative par symptômes, basée sur des mots-clés simples.
- Interface Bootstrap personnalisée avec une charte pastel professionnelle.

## Installation locale

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Puis ouvrir : `http://127.0.0.1:8000/`

## Comptes de démonstration

Après `python manage.py seed_demo` :

- Administrateur : `admin` / `admin12345`
- Médecins : mot de passe `demo12345`
  - `amina.bennani`
  - `youssef.elidrissi`
  - `salma.alaoui`
  - `mehdi.tazi`
  - `nora.fassi`

## Remarques pédagogiques

L’orientation médicale ne constitue pas un diagnostic. Elle est volontairement simple pour rester adaptée au cadre du cours : elle utilise une comparaison de mots-clés et non un modèle médical réel.

## Améliorations ajoutées

- Correction du `requirements.txt` trop lourd et mal encodé.
- Ajout du dossier `static/` et d’un fichier CSS personnalisé.
- Correction du lien de déconnexion.
- Suppression de dépendances lourdes inutiles pour l’orientation IA.
- Ajout d’une commande `seed_demo` pour créer rapidement des données de test.
- Amélioration des templates : accueil, médecins, réservation, login, inscription, dashboards.
- Ajout de la gestion des statuts côté médecin : confirmer, terminer, marquer absent.
