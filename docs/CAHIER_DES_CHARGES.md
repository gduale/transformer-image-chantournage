# Cahier des charges - Transform Image

## 1. Contexte

Le projet consiste à créer une application web permettant de transformer une photo réelle en rendu stencil noir et blanc, exploitable pour impression, découpe, pochoir ou reproduction graphique.

La demande vient d'une conversation de référence intitulée "Transformation photo en stencil", dans laquelle l'utilisateur montre une image finale stylisée et demande comment obtenir ce type de transformation à partir d'une photo réelle. La réponse initiale identifie un pipeline de traitement d'image avec réglages manuels, aperçu en direct et export.

Source fonctionnelle : https://chatgpt.com/share/6a3c3c7d-64a0-83eb-bea6-128009ce8cd3

## 2. Objectif produit

Développer une application web simple et efficace qui permet à un utilisateur non technique de :

- importer une photo ;
- ajuster visuellement les paramètres de transformation ;
- obtenir un rendu stencil noir et blanc propre ;
- exporter le résultat final dans un format réutilisable.

Le résultat doit privilégier la lisibilité du sujet, la netteté des masses noires/blanches et la réduction du bruit visuel.

## 3. Stack technique imposée

L'application doit être développée avec :

- Django pour le backend, les vues, les formulaires et le traitement serveur ;
- Tailwind CSS pour l'interface utilisateur ;
- Python pour le traitement d'image ;
- OpenCV et/ou Pillow pour les opérations de transformation ;
- Git pour le versionnement local du projet.

Le projet devra maintenir un fichier `requirements.txt` à jour à chaque ajout de dépendance.

## 4. Public cible

L'application s'adresse principalement à :

- des créateurs souhaitant préparer une image pour pochoir ;
- des utilisateurs voulant obtenir rapidement un rendu noir et blanc stylisé ;
- des personnes sans connaissance en traitement d'image.

L'interface doit donc être explicite, rapide à prendre en main et éviter les réglages trop techniques dans le parcours principal.

## 5. Parcours utilisateur principal

1. L'utilisateur arrive sur une page de transformation.
2. Il importe une image depuis son ordinateur ou son téléphone.
3. L'application affiche l'image originale et un aperçu stencil.
4. L'utilisateur ajuste les paramètres via des contrôles visuels.
5. L'aperçu est mis à jour après chaque modification ou via un bouton d'application.
6. L'utilisateur télécharge le résultat final.

## 6. Fonctionnalités MVP

### 6.1 Import d'image

- Accepter les formats JPEG, PNG et WebP.
- Contrôler la taille maximale du fichier.
- Afficher un message d'erreur clair si le format ou le poids n'est pas accepté.
- Préserver l'image source uniquement le temps nécessaire au traitement.

### 6.2 Aperçu avant/après

- Afficher l'image originale.
- Afficher le rendu stencil généré.
- Permettre une comparaison visuelle simple entre la source et le résultat.
- Adapter l'affichage aux écrans desktop et mobile.

### 6.3 Réglages de transformation

Prévoir les réglages suivants :

- luminosité ;
- contraste ;
- seuil noir/blanc ;
- niveau de détail ;
- réduction du bruit ;
- inversion noir/blanc.

Les valeurs par défaut doivent produire un résultat exploitable sans réglage obligatoire.

### 6.4 Pipeline de traitement d'image

Le pipeline minimal attendu est :

```text
1. Charger l'image source
2. Redimensionner l'image pour le traitement
3. Convertir en niveaux de gris
4. Ajuster la luminosité et le contraste
5. Appliquer un flou léger pour réduire le bruit
6. Appliquer un seuillage noir/blanc
7. Nettoyer les petits artefacts
8. Générer l'image finale
9. Exporter le résultat
```

Le pipeline doit rester déterministe : les mêmes paramètres sur la même image doivent produire le même rendu.

### 6.5 Export

- Télécharger le rendu final en PNG.
- Prévoir une extension future vers PDF.
- Nommer le fichier exporté de manière lisible, par exemple `stencil-result.png`.

## 7. Fonctionnalités futures

Ces fonctionnalités ne sont pas obligatoires dans le MVP, mais doivent être prises en compte dans l'architecture :

- recadrage manuel avant transformation ;
- rotation et miroir ;
- préréglages de style ;
- export PDF au format A4 ;
- sauvegarde temporaire d'une session de réglages ;
- historique local des derniers rendus ;
- mode haute résolution pour impression ;
- détection automatique du sujet principal ;
- suppression ou simplification de l'arrière-plan.

## 8. Interface utilisateur

L'interface doit être construite avec Tailwind CSS et suivre une logique d'outil, pas de page marketing.

### 8.1 Écran principal

L'écran principal doit contenir :

- une zone d'import d'image ;
- une zone d'aperçu original/résultat ;
- un panneau de réglages ;
- des actions claires : transformer, réinitialiser, télécharger.

### 8.2 Comportement responsive

- Sur desktop, afficher les aperçus et les réglages dans une mise en page confortable.
- Sur mobile, prioriser l'image résultat puis les contrôles.
- Les boutons et sliders doivent rester utilisables au tactile.

### 8.3 États à prévoir

- état initial sans image ;
- image en cours d'envoi ;
- traitement en cours ;
- résultat disponible ;
- erreur de format ;
- erreur de traitement ;
- image trop volumineuse.

## 9. Architecture Django proposée

Structure cible indicative :

```text
transform_image/
├── manage.py
├── requirements.txt
├── project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── images/
│   ├── forms.py
│   ├── services/
│   │   └── stencil.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── templates/
│   └── images/
│       └── transform.html
└── static/
    └── src/
        └── input.css
```

Le traitement d'image doit être isolé dans un service Python dédié, afin de pouvoir le tester sans dépendre des vues Django.

## 10. Contraintes techniques

- Ne pas stocker durablement les images utilisateur sans consentement explicite.
- Limiter la taille maximale des images en entrée.
- Nettoyer les fichiers temporaires après traitement.
- Valider les uploads côté serveur.
- Prévoir des tests unitaires sur le service de transformation.
- Garder les noms de variables, fonctions et commentaires de code en anglais.
- Garder le chat et la documentation projet en français.

## 11. Critères d'acceptation MVP

Le MVP sera considéré comme terminé si :

- l'utilisateur peut importer une image JPEG ou PNG ;
- l'application génère un rendu stencil noir et blanc ;
- au moins trois réglages influencent réellement le résultat ;
- l'utilisateur peut comparer l'original et le résultat ;
- l'utilisateur peut télécharger le PNG final ;
- l'application fonctionne sur desktop et mobile ;
- les erreurs d'upload sont gérées proprement ;
- le traitement d'image est couvert par des tests unitaires ciblés ;
- le projet est versionné avec Git ;
- `requirements.txt` reflète les dépendances utilisées.

## 12. Hors périmètre initial

Les éléments suivants ne font pas partie du MVP :

- authentification utilisateur ;
- galerie publique ;
- paiement ;
- génération d'image par IA ;
- stockage permanent des créations ;
- application mobile native ;
- édition avancée type Photoshop.

## 13. Risques et points d'attention

- Un réglage automatique unique ne donnera pas de bons résultats sur toutes les photos.
- Les photos avec arrière-plan chargé demanderont davantage de nettoyage.
- Les images sombres, floues ou peu contrastées produiront des rendus moins propres.
- Les performances peuvent devenir un problème sur des images très grandes.
- L'aperçu doit rester rapide, quitte à utiliser une version redimensionnée pour la prévisualisation.

## 14. Priorités de réalisation

1. Initialiser le projet Django et Tailwind CSS.
2. Créer la page principale d'import et de prévisualisation.
3. Implémenter le service de transformation stencil.
4. Ajouter les réglages principaux.
5. Ajouter l'export PNG.
6. Ajouter les tests.
7. Améliorer l'ergonomie mobile.
8. Préparer les extensions PDF et recadrage.

