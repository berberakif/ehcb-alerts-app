import streamlit as st
import pandas as pd
from GoogleNews import GoogleNews
from urllib.parse import quote
import json
from datetime import datetime, timedelta

# Existing mappings and functions
LANGUAGE_TO_REGION = {
    'Albanian': 'al',
    'Arabic': 'ar',
    'Chinese': 'cn',
    'French': 'fr',
    'German': 'de',
    'Greek': 'gr',
    'Hebrew': 'il',
    'Italian': 'it',
    'Japanese': 'jp',
    'Persian': 'ir',
    'Polish': 'pl',
    'Portuguese': 'pt',
    'Romanian': 'ro',
    'Russian': 'ru',
    'Serbian (Latin)': 'rs',
    'Serbian (Cyrillic)': 'rs',
    'Spanish': 'es',
    'Turkish': 'tr',
    'English': ''  # No specific region for English
}

# Load the JSON data from the file
with open('data/dictionary.json', 'r') as f:
    translations = json.load(f)

# Fetch news with GoogleNews with date range
def fetch_news_with_google_news(query, lang, start_date):
    googlenews = GoogleNews(lang=lang)
    googlenews.set_time_range(
        start_date.strftime('%m/%d/%Y'),
        datetime.now().strftime('%m/%d/%Y')
    )
    googlenews.search(query)
    return googlenews.results()

# Streamlit App
st.title("Coach Monitoring App")

# Navigation
page = st.sidebar.selectbox(
    "Select a Page", ["Google Alerts Generator", "GoogleNews Page", "NewsAPI Page", "Dictionary Search", "Custom Search"]
)

# Page 1: Google Alerts Generator
if page == "Google Alerts Generator":
    st.header("Google Alerts URL Generator")

    uploaded_file = "data/names.xlsx"
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        coach = st.selectbox("Select a Coach", df['Name'].unique())
        languages = st.multiselect(
            "Select Languages", ['English'] + list(df.columns[1:]), default=['English']
        )

        if st.button("Generate URLs"):
            st.subheader("Generated Google Alerts URLs:")
            urls = []
            for language in languages:
                if language == 'English':
                    search_term = df.loc[df['Name'] == coach, 'Name'].values[0]
                else:
                    search_term = df.loc[df['Name'] == coach, language].values[0]
                region_code = LANGUAGE_TO_REGION.get(language, "")
                url = generate_alert_url(search_term, region_code)
                urls.append((language, url))
            for language, url in urls:
                st.markdown(f"[{language} Alert]({url})")

# Page 2: GoogleNews Page
elif page == "GoogleNews Page":
    st.header("GoogleNews Page")

    uploaded_file = "data/names.xlsx"
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        languages_options = ['English'] + list(df.columns[1:])
        coach = st.selectbox("Select a Coach", df['Name'].unique())
        languages = st.multiselect(
            "Select Languages", languages_options, default=['English']
        )

        date_range = st.date_input("Start Date for Search", datetime.now() - timedelta(days=4))

        if st.button("Fetch News with GoogleNews"):
            st.subheader("Fetched News Articles:")
            for language in languages:
                if language == "English":
                    name_in_language = df.loc[df['Name'] == coach, 'Name'].values[0]
                else:
                    name_in_language = df.loc[df['Name'] == coach, language].values[0]
                lang_code = LANGUAGE_TO_REGION.get(language, 'en')
                articles = fetch_news_with_google_news(name_in_language, lang_code, date_range)

                st.write(f"**Language: {language}**")
                for article in articles:
                    st.write(f"**{article['title']}**")
                    st.write(f"{article['desc']}")
                    st.write(f"[Read more]({article['link']})")
                    st.write("---")

# Page 3: Dictionary Search
elif page == "Dictionary Search":
    st.header("Dictionary Search Page")
    coach_related_terms = ['Euroleague Head Coaches', 'Euroleague Coaches', 'Kyle Hines']
    selected_coach_terms = st.multiselect(
        "Select Coach-Related Terms", coach_related_terms, default=['Euroleague Coaches']
    )

    additional_words = ['EHCB Coaches Academy']
    available_words = list(translations.keys())
    selected_words = st.multiselect(
        "Select Related Words", available_words + additional_words
    )

    languages = list(translations['Kyle Hines'].keys())
    selected_languages = st.multiselect("Select Languages", languages, default=["English"])

    date_range = st.date_input("Start Date for Search", datetime.now() - timedelta(days=4))

    if st.button("Fetch News"):
        st.subheader("Fetched News Articles:")
        queries = []
        news_data = {}
        for coach_term in selected_coach_terms:
            for word in selected_words:
                for language in selected_languages:
                    if coach_term in translations and word in translations and language in translations[coach_term]:
                        query = f"{translations[coach_term][language]} {translations[word][language]}"
                        queries.append((query, language))

        for query, language in queries:
            lang_code = LANGUAGE_TO_REGION.get(language, 'en')
            articles = fetch_news_with_google_news(query, lang_code, date_range)

            st.write(f"**Search Query:** {query} (Language: {language})")
            if language not in news_data:
                news_data[language] = []
            news_data[language].extend(articles)

            for article in articles:
                st.write(f"**{article['title']}**")
                st.write(f"{article['desc']}")
                st.write(f"[Read more]({article['link']})")
                st.write("---")

# Page 4: Custom Search
elif page == "Custom Search":
    st.header("Custom Search Page")

    custom_query = st.text_input("Enter your custom search query")
    df = pd.read_excel("data/names.xlsx")
    languages = list(df.columns[1:])
    selected_languages = st.multiselect(
        "Select Languages", ['English'] + languages, default=['English']
    )

    date_range = st.date_input("Start Date for Search", datetime.now() - timedelta(days=4))

    if st.button("Fetch News with GoogleNews"):
        st.subheader("Fetched News Articles:")
        for language in selected_languages:
            lang_code = LANGUAGE_TO_REGION.get(language, 'en')
            articles = fetch_news_with_google_news(custom_query, lang_code, date_range)

            st.write(f"**Search Query:** {custom_query} (Language: {language})")
            for article in articles:
                st.write(f"**{article['title']}**")
                st.write(f"{article['desc']}")
                st.write(f"[Read more]({article['link']})")
                st.write("---")
