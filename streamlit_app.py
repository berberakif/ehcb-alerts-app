import streamlit as st
import pandas as pd
from GoogleNews import GoogleNews
from urllib.parse import quote

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
    'English': ''  # No specific region for English, hence empty string
}

# Google Alerts URL Generator


def generate_alert_url(search_term, region_code=""):
    base_url = "https://www.google.com/alerts?hl=en&q="
    return f"{base_url}{quote(search_term)}&gl={region_code}#1:0"

# Google News Fetcher using GoogleNews library


def fetch_news_with_google_news(name_in_language, lang):
    googlenews = GoogleNews(lang=lang)
    googlenews.search(name_in_language)
    return googlenews.results()


# Streamlit App
st.title("Coach Monitoring App")

# Navigation
page = st.sidebar.selectbox(
    "Select a Page", ["Google Alerts Generator", "GoogleNews Page"])

# Page 1: Google Alerts Generator
if page == "Google Alerts Generator":
    st.header("Google Alerts URL Generator")

    # File upload (this can be made dynamic, currently using fixed path for simplicity)
    uploaded_file = "data/names.xlsx"

    if uploaded_file:
        # Load the Excel file
        df = pd.read_excel(uploaded_file)

        # Coach selection
        coach = st.selectbox("Select a Coach", df['Name'].unique())

        # Language selection with English pre-selected
        languages = st.multiselect(
            "Select Languages",
            ['English'] + list(df.columns[1:]),
            default=['English']
        )

        if st.button("Generate URLs"):
            st.subheader("Generated Google Alerts URLs:")

            # Generate URLs
            urls = []
            for language in languages:
                if language == 'English':
                    search_term = df.loc[df['Name'] == coach, 'Name'].values[0]
                else:
                    search_term = df.loc[df['Name']
                                         == coach, language].values[0]

                region_code = LANGUAGE_TO_REGION.get(language, "")
                url = generate_alert_url(search_term, region_code)
                urls.append((language, url))

            # Display URLs
            for language, url in urls:
                st.markdown(f"[{language} Alert]({url})")

            st.write(
                "**Note:** After opening the link, manually adjust the 'Language' and 'Region' fields as needed.")

# Page 2: GoogleNews Page
elif page == "GoogleNews Page":
    st.header("GoogleNews Page")

    # Load the Excel file
    uploaded_file = "data/names.xlsx"
    if uploaded_file:
        # Load the Excel file
        df = pd.read_excel(uploaded_file)

        # Combine "English" with the other language columns
        languages_options = ['English'] + list(df.columns[1:])

        # Coach selection
        coach = st.selectbox("Select a Coach", df['Name'].unique())

        # Language selection with English pre-selected
        languages = st.multiselect(
            "Select Languages",
            languages_options,  # Now includes "English"
            default=['English']  # Set "English" as the default selection
        )

        if st.button("Fetch News with GoogleNews"):
            st.subheader("Fetched News Articles:")

            # Fetch and display news using GoogleNews library
            for language in languages:
                # Handle the case where "English" is selected
                if language == "English":
                    name_in_language = df.loc[df['Name']
                                              == coach, 'Name'].values[0]
                else:
                    name_in_language = df.loc[df['Name']
                                              == coach, language].values[0]

                # Get the language code, defaulting to 'en' (English) if not found
                lang_code = LANGUAGE_TO_REGION.get(language, 'en')

                # Fetch news using GoogleNews library
                articles = fetch_news_with_google_news(
                    name_in_language, lang=lang_code)

                # Display the fetched news articles
                for article in articles:
                    st.write(f"**{article['title']}**")
                    st.write(f"{article['desc']}")
                    st.write(f"[Read more]({article['link']})")
