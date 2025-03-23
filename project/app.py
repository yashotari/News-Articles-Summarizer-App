import streamlit as st
import pandas as pd
from gtts import gTTS
from googletrans import Translator
from googlesearch import search
from io import BytesIO
from PIL import Image
import os
from pathlib import Path
import requests

def remove_repeated_words(text):
    words = text.split()
    cleaned_text = []
    seen = set()

    for word in words:
        if word not in seen:
            cleaned_text.append(word)
            seen.add(word)

    return ' '.join(cleaned_text)


vidno=0
st.set_page_config(layout="wide")
st.write(f"# News Articles")

# Define CSV file paths for each category
csv_folder = Path(__file__).resolve().parent  # Get the directory of the script
category_csv_files = {
    'India': csv_folder / 'india.csv',
    'World': csv_folder / 'world.csv',
    'Business': csv_folder / 'business.csv',
    'Technology': csv_folder / 'tech.csv',
    'Sports': csv_folder / 'sports.csv'
}

translate=Translator()

# Dropdown menu for category selection
selected_category = st.selectbox('Select Category', ['Enter Company Name', 'India', 'World', 'Business', 'Technology', 'Sports'])
if selected_category == 'Enter Company Name':
    company_name = st.text_input("Enter Company Name:")
    
    if company_name or st.button("click on search",disabled=True):
        response = requests.post("http://localhost:8000/get_news/", json={"company": company_name})
        
        if response.status_code == 200:
            news_articles = response.json()["articles"]
            st.session_state = False  # Reset error flag

            if news_articles:
                col1, col2 = st.columns([1, 3])
                for article in news_articles:
                    with col1:
                        st.write("")
                        st.write("") 
                        
                        if article["image"] and article["image"] != "No Image":
                            st.image(article["image"], caption=article["title"],use_container_width=False)
                        st.write(f"**Sentiment:** {article['sentiment']}")
                        st.write(f"[Read More]({article['url']})")

                    with col2:
                        article["title"] = remove_repeated_words(article["title"])
                        st.subheader(article["title"])
                        st.write(f"**Topics:** {article['topics']}")  # Assuming topics is a list
                        article["summary"] = remove_repeated_words(article["summary"])
                        st.write(article["summary"])
                

                        # Convert summary to audio
                        audio_response = requests.post("http://localhost:8000/convert_audio/", json={"text": article["summary"]})
                        if audio_response.status_code == 200:
                            st.audio(audio_response.json()["audio_url"], format="audio/mp3")

                        st.write("")
                        st.write("") 
            else:
                st.warning("No articles found for this company.")
        else:
            st.error("Failed to fetch news. Please try again.")

    else:
        st.warning("Please enter a company name.")

else:

    st.write(f"## {selected_category}") 
    # Read the CSV file based on the selected category
    csv_file = category_csv_files[selected_category]
    df = pd.read_csv(csv_file)

    # Display containers for each news article
    for i in range(min(50, len(df))):
        article_title = df.iloc[i]['Article Title']
        article_summary = df.iloc[i]['Article Summary']
        article_link = df.iloc[i]['Article Link']
        article_image = df.iloc[i]['Article Image']
    
    # Check if all required fields are not empty and valid
    if all(isinstance(field, str) and field.strip() for field in [article_title, article_summary, article_link, article_image]):
        # Display article container
        col1, col2 = st.columns([1, 3])
        article_title = translate.translate(article_title, src='en', dest='hi').text
        article_summary = translate.translate(article_summary, src='en', dest='hi').text
        
        with col1:
            st.write("")
            st.write("")
            st.image(article_image, width=250)  # Display article image on the left side with specified height and width
            # Display "Read Full Article" button
            st.write(f"[Read Full Article]({article_link})")
        
        with col2:
            # Replace dollar signs with escape character before writing to Streamlit
            clean_title = article_title.replace('$', '\$')
            st.write(f"### {clean_title}")
            clean_summary = article_summary.replace('$', '\$')
            st.write(clean_summary)


            # Display "Convert to Audio" button
            convert_button_key = f"convert_button_{i}"
            if st.button("Convert to Audio", key=convert_button_key):
                # Convert summarized text to audio
                audio_filename = f"{vidno}_summary_audio.mp3"
                vidno=vidno+1
                tts = gTTS(article_summary, lang='hi')
                tts.save(audio_filename)
                st.audio(audio_filename, format='audio/mp3')

                # Remove audio file after playing
                if os.path.exists(audio_filename):
                    os.remove(audio_filename)
                    print(article_title, "- Audio file deleted")

            st.write("")
            st.write("")       
    else:
        print("One or more required fields are empty or invalid. Skipping article display.")

st.markdown("<p style='font-size: small; color: grey; text-align: center;'>A NLP project. <a href='https://github.com/akanksha1131/News-Articles-Summarizer-App'>GitHub Link</a> . Disclaimer: This project is intended for educational purposes only. Web scraping without proper authorization is not encouraged or endorsed.</p>", unsafe_allow_html=True)    
