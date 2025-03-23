from fastapi import FastAPI
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from gtts import gTTS
from googlesearch import search
import tempfile
from googletrans import Translator
from textblob import TextBlob
import nltk
nltk.download('brown')
nltk.download('punkt')
nltk.download('punkt_tab')

translate=Translator()
app = FastAPI()

class NewsRequest(BaseModel):
    company: str

# Function to analyze sentiment
def get_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity  # Polarity score (-1 to 1)
    
    if polarity > 0:
        return "Positive"
    elif polarity < 0:
        return "Negative"
    else:
        return "Neutral"

# Function to extract key topics
def extract_topics(text):
    blob = TextBlob(text)
    topics = blob.noun_phrases[:3]  # Extract top 3 noun phrases as topics
    return ", ".join(topics) if topics else "No Key Topics"

# Function to fetch image from meta tags
def get_image(soup):
    image_tag = soup.find("meta", property="og:image")  # Try OpenGraph image
    if image_tag and image_tag.get("content"):
        return image_tag["content"]

# Function to fetch image from meta tags
def get_image(soup):
    image_tag = soup.find("meta", property="og:image")  # Try OpenGraph image
    if image_tag and image_tag.get("content"):
        return image_tag["content"]
    
    # Alternative approach: Find the first image in the article
    img_tag = soup.find("img")
    if img_tag and img_tag.get("src"):
        return img_tag["src"]

    return "No Image"


@app.post("/get_news/")
def get_news(data: NewsRequest):
    company = data.company
    query = f"{company} latest news"
    
    # Fetch top 10 search results
    search_urls = list(search(query, num=10, stop=10, pause=2))

    headers = {"User-Agent": "Mozilla/5.0"}
    news_articles = []

    for url in search_urls:
        try:
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()  # Ensure successful request

            soup = BeautifulSoup(response.content, "html.parser")

            # Extract title
            title = soup.find("h1")
            if not title:
                title = soup.find("title")
            title_text = title.text.strip() if title else "No Title"

            # Extract summary from first 5 paragraphs
            paragraphs = soup.find_all("p")
            summary = " ".join([p.text.strip() for p in paragraphs[:5]]) if paragraphs else "No Summary"

            title_text = translate.translate(title_text, src='en', dest='hi').text
            summary = translate.translate(summary, src='en', dest='hi').text

            # Get image URL
            image = get_image(soup)

            sentiment = get_sentiment(summary)
            topics = extract_topics(summary)

            news_articles.append({"image": image if image else "No Image","title": title_text, "summary": summary,"sentiment": sentiment,"topics": topics, "url": url})

        except requests.RequestException as e:
            print(f"Failed to fetch {url}: {e}")
            continue

    return {"articles": news_articles}


class AudioRequest(BaseModel):
    text: str  # Ensure text is expected as a string

@app.post("/convert_audio/")
def convert_audio(data: AudioRequest):
    try:
        tts = gTTS(data.text, lang="hi")  # Convert text to Hindi audio
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            tts.save(temp_audio.name)
            audio_path = temp_audio.name  # Path to generated audio

        return {"audio_url": audio_path}  # Send back the file path

    except Exception as e:
        return {"error": str(e)}