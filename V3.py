import praw
import urllib.request
import xmltodict
import pandas as pd
import re
from IPython.display import display, clear_output
import ipywidgets as widgets
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import matplotlib.pyplot as plt

# Classe de base pour représenter les documents
class Document:
    def __init__(self, title, author, date, text=""):
        """
        Initialise un objet Document avec un titre, un auteur, une date et un texte.
        """
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
        Retourne le type du document : "Reddit".
        """
        return "Reddit"

    def __str__(self):
        """
        Méthode de conversion en chaîne de caractères pour afficher les informations du document Reddit.
        Ajoute les informations spécifiques comme le nombre de commentaires.
        """
        return super().__str__() + f", Comments: {self.num_comments}"

# Classe pour représenter les documents provenant d'Arxiv
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

# Classe pour gérer un corpus de documents (collection de documents)
class Corpus:
    def __init__(self):
        """
        Initialise un corpus avec une liste vide de documents
        et un vocabulaire vide.
        """
        self.documents = []  # Stocke les documents ajoutés
        self.vocab = {}      # Contient le vocabulaire généré à partir des documents

    def add_document(self, document):
        """
        Ajoute un document au corpus.
        """
        self.documents.append(document)

    def reset(self):
        """
        Vide la liste des documents pour réinitialiser le corpus.
        """
        self.documents = []

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
        Recherche les documents les plus similaires à une requête
        en utilisant la similarité cosinus.
        """
        query = self.clean_text(query)
        tfidf_matrix = self.build_tfidf_matrix()
        query_vector = TfidfVectorizer(stop_words='english', vocabulary=self.vocab).fit_transform([query])
        similarities = cosine_similarity(tfidf_matrix, query_vector).flatten()

        ranked_docs = sorted(enumerate(similarities), key=lambda x: x[1], reverse=True)
        results = [(self.documents[idx], float(score)) for idx, score in ranked_docs if score > 0]
        return results[:top_n]

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

    def stats(self):
        """
        Affiche des statistiques générales sur le corpus, 
        comme le nombre de documents et de mots.
        """
        num_docs = len(self.documents)
        total_words = sum(len(re.findall(r'\w+', doc.text)) for doc in self.documents)
        print(f"Nombre de documents : {num_docs}")
        print(f"Nombre total de mots : {total_words}")
        print(f"Nombre moyen de mots par document : {total_words / num_docs if num_docs else 0:.2f}")

    def get_document_types(self):
        """
        Calcule le nombre de documents par type.
        """
        type_counter = Counter(doc.getType() for doc in self.documents)
        return pd.DataFrame(type_counter.items(), columns=['Type', 'Count'])

    def export_results_to_csv(self, filename="results.csv"):
        """
        Exporte les résultats du corpus dans un fichier CSV.
        """
        if not self.documents:
            print("Le corpus est vide. Rien à exporter.")
            return
        data = [{"Title": doc.title, "Author": doc.author, "Date": doc.date, "Text": doc.text[:100]} for doc in self.documents]
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"Résultats exportés avec succès dans {filename}.")

    def plot_word_frequencies(self, top_n=10):
        """
        Génère un graphique des mots les plus fréquents dans le corpus.
        """
        freq_df = self.get_word_frequency()
        if freq_df.empty:
            print("Pas de fréquences à afficher.")
            return
        freq_df.head(top_n).plot(kind='bar', x='Word', y='Frequency', legend=False, color='skyblue')
        plt.title(f"Top {top_n} Fréquences des mots")
        plt.xlabel("Mot")
        plt.ylabel("Fréquence")
        plt.show()

    def plot_document_types(self):
        """
        Génère un graphique en camembert montrant la répartition des types de documents.
        """
        type_stats = self.get_document_types()
        if type_stats.empty:
            print("Pas de types de documents à afficher.")
            return
        type_stats.set_index('Type').plot(kind='pie', y='Count', autopct='%1.1f%%', legend=False)
        plt.title("Répartition des types de documents")
        plt.ylabel("")
        plt.show()


# Widgets pour l'interface graphique
subreddit_input = widgets.Text(description="Subreddit:", placeholder="Entrez le nom du subreddit")
query_input = widgets.Text(description="Requête Arxiv:", placeholder="Entrez la requête Arxiv")
keyword_input = widgets.Text(description="Contexte:", placeholder="Entrez un mot pour le contexte")
cosine_query_input = widgets.Text(description="Similarité :", placeholder="similarité")
limit_input = widgets.IntSlider(value=5, min=1, max=100, description="Limite:")

# Création des boutons stylisés
search_button = widgets.Button(
    description="Rechercher",
    button_style="info",
    layout=widgets.Layout(width="150px", height="30px", margin="5px")
)
stats_button = widgets.Button(
    description="Afficher Stats",
    button_style="info",
    layout=widgets.Layout(width="150px", height="30px", margin="5px")
)
cosine_button = widgets.Button(
    description="Recherche Cosine",
    button_style="info",
    layout=widgets.Layout(width="150px", height="30px", margin="5px")
)
context_button = widgets.Button(
    description="Recherche Contexte",
    button_style="info",
    layout=widgets.Layout(width="150px", height="30px", margin="5px")
)
reset_button = widgets.Button(
    description="Réinitialiser",
    button_style="info",
    layout=widgets.Layout(width="150px", height="30px", margin="5px")
)
export_button = widgets.Button(
    description="Exporter Résultats",
    button_style="info",
    layout=widgets.Layout(width="150px", height="30px", margin="5px")
)
visualize_button = widgets.Button(
    description="Visualiser Stats",
    button_style="info",
    layout=widgets.Layout(width="150px", height="30px", margin="5px")
)

# Disposition des boutons
button_column_1 = widgets.HBox([search_button, stats_button, cosine_button])
button_row_2 = widgets.HBox([context_button, reset_button, export_button])
button_row_3 = widgets.HBox([visualize_button])
buttons_container = widgets.VBox([button_column_1, button_row_2, button_row_3])

# Zone de sortie
output = widgets.Output()

# Gestion des événements
@output.capture(clear_output=True)
def on_search_button_clicked(b):
    subreddit = subreddit_input.value
    query = query_input.value
    limit = limit_input.value
    corpus.reset()  # Réinitialiser le corpus avant la recherche
    if not subreddit or not query:
        print("Veuillez remplir Subreddit et Requête.")
        return
    print(f"Recherche Reddit ({subreddit}):")
    reddit_docs = fetch_reddit_data(subreddit, limit)
    for doc in reddit_docs:
        corpus.add_document(doc)

    print(f"Recherche Arxiv ({query}):")
    arxiv_docs = fetch_arxiv_data(query, limit)
    for doc in arxiv_docs:
        corpus.add_document(doc)
    corpus.display_documents()

@output.capture(clear_output=True)
def on_stats_button_clicked(b):
    corpus.stats()

@output.capture(clear_output=True)
def on_cosine_button_clicked(b):
    query = cosine_query_input.value
    if not query:
        print("Veuillez entrer une requête pour la recherche par similarité.")
        return
    results = corpus.cosine_similarity_search(query)
    if not results:
        print(f"Aucun résultat trouvé pour la requête '{query}'.")
    else:
        for doc, score in results:
            print(f"{doc.title} ({doc.type}) - Similarité : {score:.4f}")

@output.capture(clear_output=True)
def on_context_button_clicked(b):
    keyword = keyword_input.value
    if not keyword:
        print("Veuillez entrer un mot-clé pour la recherche de contexte.")
        return
    context_results = corpus.search_with_context(keyword)
    if context_results.empty:
        print(f"Aucune occurrence trouvée pour le mot-clé '{keyword}'.")
    else:
        display(context_results)

@output.capture(clear_output=True)
def on_frequency_button_clicked(b):
    word_freq = corpus.get_word_frequency()
    display(word_freq)

@output.capture(clear_output=True)
def on_reset_button_clicked(b):
    corpus.reset()
    print("Corpus réinitialisé.")

@output.capture(clear_output=True)
def on_export_button_clicked(b):
    corpus.export_results_to_csv()
    print("Résultats exportés.")

@output.capture(clear_output=True)
def on_visualize_button_clicked(b):
    corpus.plot_word_frequencies()
    corpus.plot_document_types()

# Associer les événements aux boutons
search_button.on_click(on_search_button_clicked)
stats_button.on_click(on_stats_button_clicked)
cosine_button.on_click(on_cosine_button_clicked)
context_button.on_click(on_context_button_clicked)
reset_button.on_click(on_reset_button_clicked)
export_button.on_click(on_export_button_clicked)
visualize_button.on_click(on_visualize_button_clicked)


# Affichage des widgets
# Affichage final
display(
    subreddit_input, query_input, keyword_input, cosine_query_input, limit_input,
    buttons_container, output
)

# Fonctions pour récupérer les données
def fetch_reddit_data(subreddit, limit):
    reddit = praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent='WebScrapping')
    documents = []
    for post in reddit.subreddit(subreddit).hot(limit=limit):
        doc = RedditDocument(post.title, str(post.author), datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%d'), post.num_comments, post.selftext)
        documents.append(doc)
    return documents

def fetch_arxiv_data(query, limit):
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={limit}"
    documents = []
    with urllib.request.urlopen(url) as response:
        data = response.read()
        parsed = xmltodict.parse(data)
        for entry in parsed['feed']['entry']:
            authors = [author['name'] for author in entry['author']] if isinstance(entry['author'], list) else [entry['author']['name']]
            doc = ArxivDocument(entry['title'], authors, entry['published'], entry['summary'])
            documents.append(doc)
    return documents

# Initialisation du corpus
corpus = Corpus()

if __name__ == "__main__":
    print("Utilisez l'interface graphique pour interagir avec le corpus.")
