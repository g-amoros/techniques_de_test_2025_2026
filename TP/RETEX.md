# Retour d'expérience - TP Techniques de Test

**Étudiant** : AMOROS Gaël  
**Formation** : M1 ILSEN classique  
**Date** : Décembre 2024

---

## 1. Introduction

Ce document présente mon retour d'expérience sur le projet de développement du microservice Triangulator en suivant une approche Test-Driven Development (TDD). L'objectif était de mettre en pratique les méthodologies de test en écrivant d'abord les tests, puis en implémentant le code pour les faire passer.

---

## 2. Ce qui a bien fonctionné

### 2.1 Organisation et structure du projet

La structure de tests proposée dans le plan initial s'est révélée très pertinente :

-   Séparation claire entre tests unitaires, d'intégration et de performance
-   Organisation en sous-dossiers (`unit/`, `integration/`, `api/`, `performance/`) facilitant la navigation
-   Utilisation de markers pytest (`@pytest.mark.performance`) permettant d'exécuter sélectivement les tests

Cette organisation a grandement facilité le développement itératif et la maintenance des tests.

### 2.2 Approche TDD pour les utilitaires binaires

L'écriture des tests pour `binary_utils.py` avant l'implémentation a été particulièrement bénéfique. Les tests ont servi de **spécification exécutable** du format binaire, ce qui m'a permis de :

-   Clarifier exactement ce qui était attendu (endianness, tailles, formats)
-   Détecter immédiatement les erreurs de parsing
-   Valider chaque cas limite (données vides, tronquées, malformées)

**Résultat** : 90% de couverture sur ce module avec une implémentation robuste du premier coup.

### 2.3 Tests d'intégration avec mocks

L'utilisation de `unittest.mock` et `requests-mock` pour simuler le PointSetManager a été très efficace. Cela m'a permis de :

-   Tester le Triangulator de manière isolée sans dépendre d'un service externe
-   Simuler tous les cas d'erreur (404, 503, timeout) facilement
-   Accélérer considérablement l'exécution des tests

Les mocks ont également facilité le debugging en me permettant de contrôler précisément les réponses du service externe.

### 2.4 Couverture de code comme indicateur

L'utilisation de `coverage` a été très instructive. Le rapport de couverture m'a permis d'identifier rapidement les branches non testées, notamment dans `app.py` où certaines gestions d'erreur n'étaient pas couvertes initialement.

**Résultat final** : 90% de couverture globale, avec 97% sur la logique métier (`core.py`).

---

## 3. Les difficultés rencontrées

### 3.1 Implémentation de l'algorithme de triangulation

C'était le défi technique majeur du projet. Initialement, j'avais sous-estimé la complexité d'implémenter une triangulation de Delaunay "from scratch" sans bibliothèques externes.

**Problèmes rencontrés** :

-   Compréhension de l'algorithme de Bowyer-Watson
-   Gestion du super-triangle pour l'initialisation
-   Calcul du circumcircle et test d'appartenance
-   Gestion des cas dégénérés (points colinéaires, triangles plats)

**Solution adoptée** :

-   Recherche approfondie sur l'algorithme (documentation, articles académiques)
-   Implémentation incrémentale avec tests unitaires à chaque étape
-   Utilisation de cas simples (triangle, carré) pour valider la logique

**Leçon** : Pour un algorithme complexe, avoir des tests bien définis est crucial. Ils m'ont permis de progresser par petits pas validés plutôt que de tout implémenter d'un coup.

### 3.2 Gestion des cas limites

Le test `test_triangulation_duplicates` a révélé une différence entre mes attentes initiales et la réalité de l'implémentation.

**Problème** : Le test initial attendait une exception en cas de points dupliqués, mais mon implémentation les gérait automatiquement en les filtrant.

**Réflexion** : Fallait-il lever une exception (approche stricte) ou gérer le cas gracieusement (approche tolérante) ?

**Décision finale** : J'ai opté pour la suppression automatique des doublons car :

-   C'est plus robuste en production (le service ne crash pas)
-   C'est plus user-friendly pour les clients de l'API
-   C'est cohérent avec le comportement pour les points colinéaires (retour d'une liste vide)

J'ai donc **adapté le test** pour refléter ce comportement, ce qui illustre bien que les tests peuvent évoluer en phase d'implémentation.

### 3.3 Configuration de l'environnement Python

Problème initial avec le PYTHONPATH qui empêchait pytest de trouver le module `src`.

**Solution** : Ajout de `PYTHONPATH=.` dans le Makefile pour toutes les commandes pytest et coverage.

**Leçon** : La configuration de l'environnement de test est aussi importante que les tests eux-mêmes. Un problème de configuration peut bloquer tout le workflow.

---

## 4. Analyse du plan initial vs réalité

### 4.1 Ce qui était bien prévu

**Structure des tests** : La séparation en 4 catégories (unit, integration, api, performance) était parfaite et n'a pas nécessité de modification.

**Cas de tests unitaires** : Les tests sur le parsing binaire et la triangulation étaient bien identifiés dès le départ.

**Tests d'erreurs** : La liste des codes HTTP à tester (400, 404, 500, 503) était exhaustive et pertinente.

### 4.2 Ce qui a évolué

**Gestion des doublons** : Le plan prévoyait de lever une exception, mais l'implémentation finale gère le cas automatiquement. C'est un exemple typique où la réflexion lors de l'implémentation a conduit à un meilleur design.

**Tests de performance** : Le plan mentionnait l'utilisation de `pytest-benchmark`, mais finalement j'ai utilisé une approche plus simple avec `time.time()` et des assertions sur la durée. Cela s'est révélé suffisant pour les besoins du projet.

**Profondeur de la couverture** : Le plan visait 100%, nous avons obtenu 90%. Les 10% manquants correspondent principalement à des branches d'erreur très spécifiques dans `app.py` (timeouts, erreurs réseau rares). Avec plus de temps, j'aurais pu ajouter des tests pour ces cas, mais le ratio effort/bénéfice n'était pas optimal.

### 4.3 Ce qui manquait dans le plan

**Tests de validation du format binaire** : Le plan aurait pu être plus précis sur la validation de l'endianness et des types (float vs double). J'ai dû vérifier cela manuellement avec `struct.calcsize()`.

**Tests de régression** : Aucun test ne vérifie que les résultats sont **déterministes** (même entrée = même sortie). Avec plus de recul, j'aurais ajouté des tests avec des valeurs attendues "en dur" pour détecter toute régression.

---

## 5. Apprentissages et réflexions

### 5.1 Sur le TDD

**Avantages constatés** :

-   **Clarification des exigences** : Écrire les tests force à réfléchir précisément à ce qu'on attend du code
-   **Confiance dans les modifications** : Avec une bonne suite de tests, refactorer devient beaucoup moins risqué
-   **Documentation vivante** : Les tests servent de documentation sur le comportement attendu
-   **Détection précoce des bugs** : Beaucoup d'erreurs ont été détectées immédiatement lors de l'exécution des tests

**Limites observées** :

-   **Temps initial** : Écrire les tests prend du temps, surtout au début
-   **Évolution des tests** : Certains tests ont dû être réécrits/adaptés pendant l'implémentation
-   **Sur-spécification** : Parfois, les tests étaient trop rigides et imposaient des contraintes inutiles

**Bilan** : Le TDD est particulièrement adapté à ce type de projet avec des spécifications claires (formats binaires, API). Pour des projets plus exploratoires, une approche mixte serait peut-être plus appropriée.

### 5.2 Sur la triangulation de Delaunay

J'ai découvert que :

-   L'algorithme de Bowyer-Watson est élégant mais non trivial à implémenter
-   Les cas dégénérés (colinéarité, précision flottante) sont omniprésents en géométrie computationnelle
-   Un bon algorithme doit être à la fois **correct** (propriété de Delaunay) et **robuste** (gestion des edge cases)

**Réflexion** : Si j'avais eu accès à NumPy/SciPy, l'implémentation aurait été bien plus simple (`scipy.spatial.Delaunay`). Cette contrainte m'a forcé à vraiment comprendre l'algorithme, ce qui était l'objectif pédagogique.

### 5.3 Sur la qualité logicielle

**Outils découverts/approfondis** :

-   `pytest` : Fixtures, markers, parametrize
-   `coverage` : Analyse de couverture et identification des branches non testées
-   `ruff` : Linter moderne et rapide, bon équilibre entre strictesse et pragmatisme
-   `pdoc3` : Génération automatique de documentation

**Pratiques adoptées** :

-   Docstrings systématiques (format Google)
-   Gestion explicite des erreurs avec messages clairs
-   Validation des entrées (UUID, formats binaires)
-   Séparation des responsabilités (parsing, logique métier, API)

---

## 6. Ce que je ferais différemment

### 6.1 Avec plus de temps

**Tests additionnels** :

-   Tests de charge avec `locust` pour simuler des requêtes concurrentes
-   Tests de régression avec snapshots (valeurs de triangulation attendues)
-   Tests de validation des propriétés de Delaunay (angles > 60°)
-   Tests de fuzzing pour trouver des cas limites non prévus

**Améliorations de l'implémentation** :

-   Cache des triangulations calculées (avec Redis par exemple)
-   Logging structuré pour faciliter le debugging en production
-   Métriques Prometheus pour monitorer les performances
-   Support des formats JSON en alternative au binaire (pour faciliter le debugging)

**Optimisations** :

-   Utilisation de structures de données plus efficaces (KD-tree pour la recherche de points)
-   Parallélisation de la triangulation pour de très grands datasets
-   Streaming pour traiter des PointSets trop grands pour la mémoire

### 6.2 Approche différente

**Plan de tests** :

-   J'aurais commencé par des tests end-to-end simples avant les tests unitaires détaillés
-   Cela permet de valider le workflow complet rapidement, puis d'ajouter les détails

**Implémentation incrémentale** :

-   Version 1 : Algorithme simple (ear clipping) pour avoir quelque chose qui fonctionne rapidement
-   Version 2 : Passage à Delaunay une fois les tests en place
-   Cette approche "quick win" aurait permis de débloquer les tests d'intégration plus tôt

**Documentation** :

-   J'aurais documenté les choix d'architecture au fur et à mesure dans un ADR (Architecture Decision Record)
-   Cela aurait facilité la rédaction de ce RETEX

---

## 7. Conclusion

Ce projet m'a permis de mettre en pratique le TDD dans un contexte réaliste avec :

-   Des contraintes techniques (pas de bibliothèques externes)
-   Des spécifications précises (formats binaires, API)
-   Des exigences de qualité (couverture, linting, documentation)

**Principaux apprentissages** :

1. Le TDD fonctionne très bien quand les spécifications sont claires
2. Les tests sont un investissement rentable (ils m'ont fait gagner beaucoup de temps en debugging)
3. La couverture de code est un bon indicateur mais pas une fin en soi
4. Les outils modernes (pytest, coverage, ruff) rendent le TDD beaucoup plus accessible
5. L'implémentation d'algorithmes complexes sans bibliothèques est instructif mais chronophage

**Ce que je retiens pour mes futurs projets** :

-   Toujours commencer par les tests pour les fonctions critiques
-   Investir dans l'infrastructure de test dès le début
-   Ne pas hésiter à faire évoluer les tests pendant l'implémentation
-   Automatiser au maximum (CI/CD)
-   Documenter les décisions importantes

**Note finale** : Le TDD n'est pas une baguette magique, mais c'est un outil puissant quand il est bien utilisé. Ce projet m'a convaincu de son intérêt, et je compte l'appliquer dans mes futurs développements, au moins pour les parties critiques du code.
