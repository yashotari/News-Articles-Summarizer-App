import pandas as pd
from nltk.corpus import stopwords 


# Preprocessing function
def preprocess_text(text):
    # Tokenize the text
    tokens = text.lower().split()

    # Remove punctuation and stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word.isalnum() and word not in stop_words]

    return tokens



# Function to calculate similarity score between text and bag of words
def similarity_score(text, bow):
    # Tokenize the input text
    tokens = preprocess_text(text)

    # Calculate similarity score based on common words with bag of words
    common_words = set(tokens) & set(bow['Word'])
    score = sum(bow[bow['Word'] == word]['Frequency'].values[0] for word in common_words)

    return score




# Function to classify text domain using bag of words
def classify_text_domain(text):
    # Load bags of words from CSV files
    india_bow = pd.read_csv("india_bow.csv")
    world_bow = pd.read_csv("world_bow.csv")
    business_bow = pd.read_csv("business_bow.csv")
    tech_bow = pd.read_csv("tech_bow.csv")
    sports_bow = pd.read_csv("sports_bow.csv")

    # Calculate similarity scores between input text and bags of words
    india_score = similarity_score(text, india_bow)
    world_score = similarity_score(text, world_bow)
    business_score = similarity_score(text, business_bow)
    tech_score = similarity_score(text, tech_bow)
    sports_score = similarity_score(text, sports_bow)

    # Determine the domain with the highest similarity score
    scores = {
        'India': india_score,
        'World': world_score,
        'Business': business_score,
        'Technology': tech_score,
        'Sports': sports_score
    }
    domain = max(scores, key=scores.get)

    return domain



