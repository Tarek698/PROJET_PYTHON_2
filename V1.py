import os
import praw
import urllib.request
import xmltodict
import datetime
import pickle
import time

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
        self.type = self.getType()  # Déterminé dynamiquement par les classes filles

    def getType(self):
        """
        Retourne le type du document. Ici, c'est "Document" pour la classe de base.
        Les classes dérivées peuvent redéfinir cette méthode.
        """
        return "Document"  # Type générique par défaut

    def __str__(self):
        """
        Méthode de conversion en chaîne de caractères pour afficher les informations du document.
        """
        return f"{self.title} by {self.author} on {self.date} ({self.type})"

# Classe pour les documents Reddit
class RedditDocument(Document):
    def __init__(self, title, author, date, num_comments, text=""):
        """
        Initialise un objet RedditDocument, dérivé de Document, avec des informations spécifiques à Reddit.
        
        """
        super().__init__(title, author, date, text)  # Hérite des attributs communs de Document
        self.num_comments = num_comments  # Nombre de commentaires sur le post

    def getType(self):
        """
        Méthode de conversion en chaîne de caractères pour afficher les informations du document Reddit.
        Ajoute les informations spécifiques comme le nombre de commentaires.
        """
        return "Reddit"  # Spécifique aux documents Reddit

    def __str__(self):
        return super().__str__() + f", Comments: {self.num_comments}"

# Classe pour les documents Arxiv
class ArxivDocument(Document):
    def __init__(self, title, authors, date, text=""):
        """
        Initialise un objet ArxivDocument, dérivé de Document, avec des informations spécifiques à Arxiv.
        
        """
        super().__init__(title, authors, date, text)  # Hérite des attributs communs de Document
        self.authors = authors  # Liste des auteurs

    def getType(self):
        """
        Retourne le type du document : "Arxiv".
        """
        return "Arxiv"  # Spécifique aux documents Arxiv

    def __str__(self):
        """
        Méthode de conversion en chaîne de caractères pour afficher les informations du document Arxiv.
        Ajoute la liste des auteurs.
        """
        authors_str = ", ".join(self.authors)  
        return super().__str__() + f", Authors: {authors_str}"

# Classe pour gérer un corpus de documents
class Corpus:
    _instance = None 

    def __new__(cls):
        """
        Assure qu'une seule instance de la classe Corpus est créée (Singleton).
        Initialise la liste des documents lors de la première instanciation.
        """
        if cls._instance is None:
            cls._instance = super(Corpus, cls).__new__(cls)
            cls._instance.documents = [] 
        return cls._instance  

    def add_document(self, document):
        """
        Ajoute un document au corpus.
        """
        self.documents.append(document)

    def display_documents(self):
        """
        Affiche tous les documents contenus dans le corpus.
        """
        for doc in self.documents:
            print(doc)


# collecte des données de Reddit
def collect_reddit_data():
    """
    Collecte des données du subreddit 'manga' via l'API Reddit.
    Combine le titre et le contenu des posts pour créer des objets RedditDocument.

    """
    reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent='WebScrapping'
)
    hot_posts = reddit.subreddit('manga')  
    documents = []
    for post in hot_posts.hot(limit=15):
        combined_text = f"{post.title}. {post.selftext}".replace("\n", " ") 
        doc = RedditDocument(
            title=post.title,
            author=str(post.author) if post.author else "Inconnu",  
            date=str(datetime.datetime.fromtimestamp(post.created_utc)),  
            num_comments=post.num_comments,
            text=combined_text
        )
        documents.append(doc)
    return documents


# collecte des données d'Arxiv
def collect_arxiv_data():
    """
    Collecte des données depuis l'API Arxiv en utilisant un terme de recherche.
    Crée des objets ArxivDocument pour chaque entrée récupérée.
    """
    query = "anime"  
    url = f'http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=15'
    time.sleep(1)  

    with urllib.request.urlopen(url) as response:
        data = response.read()  

    parsed_data = xmltodict.parse(data)  
    documents = []
    for entry in parsed_data['feed']['entry']:
        auteur = entry['author'][0].get('name', "Inconnu") if 'author' in entry and isinstance(entry['author'], list) else "Inconnu"
        doc = ArxivDocument(
            title=entry['title'],
            authors=[auteur],
            date=entry['published'], 
            text=entry['summary'].replace("\n", " ")  
        )
        documents.append(doc)
    return documents


# Exemple d'utilisation
if __name__ == "__main__":
    """
    Exemple d'utilisation de la classe Corpus et des fonctions de collecte.
    Combine des données de Reddit et Arxiv, les ajoute au corpus, les affiche,
    et sauvegarde/charge le corpus avec pickle.
    """
    corpus = Corpus()  

    # Collecte des données depuis Reddit et Arxiv
    reddit_documents = collect_reddit_data()
    arxiv_documents = collect_arxiv_data()

   
    for doc in reddit_documents + arxiv_documents:
        corpus.add_document(doc)

   
    corpus.display_documents()


    with open("corpus.pkl", "wb") as f:
        pickle.dump(corpus, f) 

   
    with open("corpus.pkl", "rb") as f:
        loaded_corpus = pickle.load(f)  
        loaded_corpus.display_documents() 