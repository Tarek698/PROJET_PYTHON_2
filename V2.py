import praw
import urllib.request
import xmltodict
import datetime
from collections import Counter
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from urllib.parse import quote
import re

# Classe de base pour les documents
class Document:
    """
        Initialise un objet Document avec un titre, un auteur, une date et un texte.
    """
    def __init__(self, title, author, date, text=""):
        self.title = title
        self.author = author
        self.date = date
        self.text = text
        self.type = self.getType()

    def getType(self):
        """
        Retourne le type du document. Ici, c'est "Document" pour la classe de base.
        Les classes dérivées peuvent redéfinir cette méthode.
        """
        return "Document"

    def __str__(self):
        """
        Méthode de conversion en chaîne de caractères pour afficher les informations du document.
        """
        return f"{self.title} by {self.author} on {self.date} ({self.type})"

# Classe pour représenter les documents provenant de Reddit
class RedditDocument(Document):
    def __init__(self, title, author, date, num_comments, text=""):
        """
        Initialise un objet RedditDocument, dérivé de Document, avec des informations spécifiques à Reddit.
        
        """
        super().__init__(title, author, date, text)
        self.num_comments = num_comments

    def getType(self):
        """
        Méthode de conversion en chaîne de caractères pour afficher les informations du document Reddit.
        Ajoute les informations spécifiques comme le nombre de commentaires.
        """
        return "Reddit"

    def __str__(self):
        return super().__str__() + f", Comments: {self.num_comments}"

# Classe pour les documents Arxiv
class ArxivDocument(Document):
    def __init__(self, title, authors, date, text=""):
        """
        Initialise un objet ArxivDocument, dérivé de Document, avec des informations spécifiques à Arxiv.
        
        """
        super().__init__(title, authors, date, text)
        self.authors = authors

    def getType(self):
        """
        Retourne le type du document : "Arxiv".
        """
        return "Arxiv"

    def __str__(self):
        """
        Méthode de conversion en chaîne de caractères pour afficher les informations du document Arxiv.
        Ajoute la liste des auteurs.
        """
        authors_str = ", ".join(self.authors)
        return super().__str__() + f", Authors: {authors_str}"

# Classe pour gérer un corpus de documents
class Corpus:
    def __init__(self):
        """
        Initialise un corpus avec une liste vide de documents
        et un vocabulaire vide.
        """
        self.documents = []
        self.vocab = {}

    def add_document(self, document):
        """
        Ajoute un document au corpus.
        """
        self.documents.append(document)

    def display_documents(self):
        """
        Affiche tous les documents du corpus avec leurs détails.
        """
        print("Corpus Content:")
        for i, doc in enumerate(self.documents):
            print(f"{i + 1}. {doc}")

    def clean_text(self, text):
        """
        Nettoie un texte en le mettant en minuscules et en supprimant la ponctuation.
        """
        text = text.lower()
        text = re.sub(r'\W+', ' ', text)
        return text

    def build_tfidf_matrix(self):
        """
        Construit une matrice TF-IDF pour représenter les textes des documents.
        """
        cleaned_texts = [self.clean_text(doc.text) for doc in self.documents]
        vectorizer = TfidfVectorizer(stop_words='english', min_df=2)
        tfidf_matrix = vectorizer.fit_transform(cleaned_texts)
        self.vocab = vectorizer.vocabulary_
        return tfidf_matrix

    def cosine_similarity_search(self, query, top_n=5):
        """
        Recherche les documents les plus similaires à une requête donnée
        en utilisant la similarité cosinus.
        """
        query = self.clean_text(query)
        tfidf_matrix = self.build_tfidf_matrix()
        query_vector = TfidfVectorizer(stop_words='english', vocabulary=self.vocab).fit_transform([query])
        similarities = cosine_similarity(tfidf_matrix, query_vector).flatten()

        ranked_docs = sorted(enumerate(similarities), key=lambda x: x[1], reverse=True)
        results = [(self.documents[idx], float(score)) for idx, score in ranked_docs if score > 0]
        return results[:top_n]

    def display_cosine_results(self, results):
        """Affiche les résultats de la recherche par similarité cosinus."""
        print("\nCosine Recherche similaire:")
        if not results:
            print("Rien trouvé.")
        else:
            for rank, (doc, score) in enumerate(results, start=1):
                print(f"{rank}. {doc.title} ({doc.type}) - Similarity Score: {score:.4f}")

    def search_with_context(self, keyword, context_size=5):
        """
        Recherche un mot-clé et retourne son contexte (texte autour) dans chaque document.
        """
        results = []
        for doc in self.documents:
            matches = re.finditer(rf'\b{re.escape(keyword)}\b', doc.text, re.IGNORECASE)
            for match in matches:
                start, end = match.span()
                left_context = doc.text[max(0, start - context_size):start].strip()
                right_context = doc.text[end:end + context_size].strip()
                results.append({
                    "Document": doc.title,
                    "Left Context": left_context,
                    "Keyword": match.group(),
                    "Right Context": right_context,
                })
        return pd.DataFrame(results)

    def get_word_frequency(self):
        """
        Calcule la fréquence des mots dans tous les documents du corpus.
        
        """
        word_counter = Counter()
        for doc in self.documents:
            words = re.findall(r'\w+', doc.text.lower())
            word_counter.update(words)

        return pd.DataFrame(word_counter.items(), columns=['Word', 'Frequency']).sort_values(by='Frequency', ascending=False)

# Fonction pour collecter les données Reddit
def fetch_reddit_data(subreddit='einstein', limit=5):
    """
    Collecte les données d'un subreddit Reddit.
    Retourne une liste d'objets RedditDocument.
    """
    reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent='WebScrapping'
)
    subreddit = reddit.subreddit(subreddit)
    documents = []
    for post in subreddit.hot(limit=limit):
        title = post.title
        author = str(post.author) if post.author else "Unknown"
        date = datetime.datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d')
        num_comments = post.num_comments
        text = post.selftext.replace('\n', ' ')
        documents.append(RedditDocument(title, author, date, num_comments, text))
    return documents

# Fonction pour collecter les données Arxiv
def fetch_arxiv_data(query='physician', max_results=5):
    """
    Collecte les données depuis Arxiv en utilisant une requête API.
    Retourne une liste d'objets ArxivDocument.
    """
    query = quote(query)
    url = f'http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}'
    with urllib.request.urlopen(url) as response:
        data = response.read()
    parsed = xmltodict.parse(data)
    documents = []
    for entry in parsed['feed']['entry']:
        title = entry['title']
        authors = [author['name'] for author in entry['author']] if isinstance(entry['author'], list) else [entry['author']['name']]
        date = entry['published']
        summary = entry['summary'].replace('\n', ' ')
        documents.append(ArxivDocument(title, authors, date, summary))
    return documents

# Main
if __name__ == "__main__":
    corpus = Corpus()

    # Collecter les documents depuis Reddit et Arxiv
    reddit_docs = fetch_reddit_data()
    arxiv_docs = fetch_arxiv_data()

    # Ajouter les documents au corpus
    for doc in reddit_docs + arxiv_docs:
        corpus.add_document(doc)

    # Afficher le contenu du corpus
    corpus.display_documents()

    # Recherche avec contexte
    keyword = "einstein"
    print(f"\nrecherche de context pour Keyword: '{keyword}'")
    context_results = corpus.search_with_context(keyword)
    print(context_results)

    # Fréquence des mots
    print("\nWord Frequencies:")
    print(corpus.get_word_frequency().head(10))

    # Recherche par similarité cosinus
    query = "machine learning"
    print(f"\nRecherche de similarité cosinus pour : '{query}'")
    results = corpus.cosine_similarity_search(query)
    corpus.display_cosine_results(results)
