# Guide d'utilisation : Système de Recherche de Corpus (V3)

## Description
Ce projet est un outil de gestion et d'analyse de corpus, conçu pour collecter des documents depuis Reddit et Arxiv, puis les analyser à l'aide de techniques telles que :

- Recherche par contexte (context search)
- Analyse de similarité cosinus
- Visualisation des fréquences des mots
- Gestion des documents via une interface graphique simple et intuitive dans Jupyter Notebook.

## Fonctionnalités principales
1. Collecte de documents depuis Reddit et Arxiv.
2. Recherche de mots-clés dans le contexte des documents.
3. Analyse des similarités cosinus entre une requête et les documents.
4. Visualisation des statistiques du corpus (fréquences des mots et types de documents).
5. Export des résultats dans un fichier CSV.

---

## Prérequis
1. **Python** : Version 3.8 ou supérieure.
2. **Modules requis** :
   - praw
   - urllib
   - xmltodict
   - pandas
   - numpy
   - scikit-learn
   - matplotlib
   - ipywidgets

   Installez-les avec la commande :
   ```bash
   pip install -r requirements.txt
   ```

3. **Jupyter Notebook** : Assurez-vous que Jupyter est installé sur votre machine. Si ce n'est pas le cas, installez-le via :
   ```bash
   pip install notebook
   ```

---

## Étapes pour exécuter la version V3

1. **Lancer Jupyter Notebook :**
   Ouvrez un terminal dans le dossier du projet et exécutez la commande suivante :
   ```bash
   jupyter notebook
   ```

2. **Ouvrir le fichier `notebook.ipynb` :**
   Une fois l'interface Jupyter Notebook ouverte dans votre navigateur, cliquez sur `notebook.ipynb`.

3. **Exécuter le fichier V3 :**
   Dans le notebook, exécutez la commande suivante dans une cellule :
   ```python
   %run V3.py
   ```

4. **Interaction avec l'interface graphique :**
   - Remplissez les champs d'entrée (Subreddit, Requête Arxiv, etc.).
   - Cliquez sur les boutons pour effectuer des actions comme rechercher, afficher des statistiques, exporter les résultats, etc.

5. **Gestion des erreurs :**
   Si un message d'erreur s'affiche lors de l'exécution initiale, cliquez sur le bouton de lecture (visible en haut de l'écran) pour réexécuter correctement les cellules.

---

## Fonctionnalités des boutons

- **Rechercher :** Collecte les documents depuis Reddit et Arxiv en fonction des entrées fournies.
- **Afficher Stats :** Affiche les statistiques du corpus (nombre de documents, mots, etc.).
- **Recherche Cosine :** Analyse la similarité cosinus entre une requête et les documents du corpus.
- **Recherche Contexte :** Recherche un mot-clé spécifique et affiche son contexte dans les documents.
- **Réinitialiser :** Vide le corpus actuel pour recommencer une nouvelle recherche.
- **Exporter Résultats :** Enregistre les documents collectés dans un fichier CSV.
- **Visualiser Stats :** Affiche des graphiques sur les fréquences des mots et la répartition des types de documents.

---

## Structure des fichiers

- `V1.py` : Version initiale avec fonctionnalités basiques.
- `V2.py` : Amélioration avec ajout d'analyse contextuelle et de similarité.
- `V3.py` : Version finale avec interface graphique et extensions comme l'export CSV et la visualisation des données.
- `notebook.ipynb` : Notebook permettant d'exécuter et d'interagir avec l'application via Jupyter Notebook.
- `requirements.txt` : Liste des dépendances nécessaires pour exécuter le projet.

---

## Notes supplémentaires

- **Performances :** La collecte des données depuis Reddit et Arxiv dépend de votre connexion internet et des limitations des API.
- **API Reddit :** Assurez-vous que vos identifiants (client_id, client_secret, user_agent) sont valides pour accéder aux données.
- **Support :** Si vous rencontrez des problèmes, vérifiez les logs dans Jupyter Notebook ou contactez le développeur du projet.
-  **Support :** Si vous rencontrez des problèmes pour lancer Jupyter crée un env dedié de préference venv ou conda.
---

**Amusez-vous à explorer et analyser vos corpus avec cet outil puissant !**