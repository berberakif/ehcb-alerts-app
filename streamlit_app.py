import streamlit as st
import pandas as pd
from GoogleNews import GoogleNews
from urllib.parse import quote
from newsapi import NewsApiClient
import json

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

LANGUAGE_TO_NEWSAPI = {
    'Albanian': 'sq',
    'Arabic': 'ar',
    'Chinese': 'zh',
    'French': 'fr',
    'German': 'de',
    'Greek': 'el',
    'Hebrew': 'he',
    'Italian': 'it',
    'Japanese': 'ja',
    'Persian': 'fa',
    'Polish': 'pl',
    'Portuguese': 'pt',
    'Romanian': 'ro',
    'Russian': 'ru',
    'Serbian (Latin)': 'sr',
    'Serbian (Cyrillic)': 'sr',  # Note: NewsAPI uses 'sr' for Serbian
    'Spanish': 'es',
    'Turkish': 'tr',
    'English': 'en'  # Correct code for English
}
# Function to fetch news using NewsAPI

# Updated function to use correct language codes
# Load the JSON data from the file
with open('data/dictionary.json', 'r') as f:
    translations = json.load(f)


def fetch_news_with_newsapi(query, language='en'):
    # Retrieve the API key from the environment variable
    api_key = ''
    if not api_key:
        st.error(
            "API key not found. Please set the NEWSAPI_KEY environment variable.")
        return []

    newsapi = NewsApiClient(api_key=api_key)

    # Check if the language is valid for NewsAPI
    if language not in LANGUAGE_TO_NEWSAPI.values():
        st.error(f"Invalid language code: {language}")
        return []

    response = newsapi.get_everything(q=query, language=language)
    if response['status'] != 'ok':
        st.error("Failed to fetch news from NewsAPI.")
        return []

    return response['articles']


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
    "Select a Page", ["Google Alerts Generator", "GoogleNews Page", "NewsAPI Page", "Dictionary Search", "Custom Search"])

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

# Page 3: NewsAPI Page using the newsapi-python client
elif page == "NewsAPI Page":
    st.header("NewsAPI Page")

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

        if st.button("Fetch News with NewsAPI"):
            st.subheader("Fetched News Articles:")

            # Fetch and display news using NewsAPI client
            for language in languages:
                if language == "English":
                    name_in_language = df.loc[df['Name']
                                              == coach, 'Name'].values[0]
                else:
                    name_in_language = df.loc[df['Name']
                                              == coach, language].values[0]

                lang_code = LANGUAGE_TO_REGION.get(language, 'en')

                # Fetch news using the NewsAPI client
                articles = fetch_news_with_newsapi(
                    name_in_language, language='en')

                for article in articles:
                    st.write(f"**{article['title']}**")
                    st.write(f"{article['description']}")
                    st.write(f"[Read more]({article['url']})")

# Page 4: Dictionary Search
elif page == "Dictionary Search":
    st.header("Dictionary Search Page")

    # Step 1: Select coach-related terms
    coach_related_terms = ['Euroleague Head Coaches', 'Euroleague Coaches']
    selected_coach_terms = st.multiselect(
        "Select Coach-Related Terms",
        coach_related_terms,
        default=['Euroleague Coaches']  # Default selection
    )

    # Step 2: Select the related words (excluding 'Euroleague Head Coaches' and 'Euroleague Coaches')
    available_words = [word for word in translations.keys()
                       if word not in coach_related_terms]
    selected_words = st.multiselect(
        "Select Related Words",
        available_words,
    )

    # Step 3: Select language(s)
    # Assuming "Association" contains all language keys
    languages = list(translations['Association'].keys())
    english_key = "English" if "English" in languages else None

    # Adding "English" explicitly to the selection options
    if english_key:
        languages.insert(0, english_key)

    selected_languages = st.multiselect(
        "Select Languages",
        languages,
        # Use "English" if available, otherwise default to the first language
        default=[english_key] if english_key else [languages[0]]
    )

    if st.button("Fetch News with GoogleNews"):
        st.subheader("Fetched News Articles:")

        # Generate combinations of coach definitions and related words
        queries = []
        news_data = {}
        for coach_term in selected_coach_terms:
            for word in selected_words:
                for language in selected_languages:
                    if language in translations[coach_term] and language in translations[word]:
                        query = f"{translations[coach_term][language]} {translations[word][language]}"
                        queries.append((query, language))

        # Fetch and display news
        for query, language in queries:
            lang_code = LANGUAGE_TO_REGION.get(language, 'en')
            articles = fetch_news_with_google_news(query, lang=lang_code)

            st.write(f"**Search Query:** {query} (Language: {language})")
            if language not in news_data:
                news_data[language] = []
            news_data[language].extend(articles)

            for article in articles:
                st.write(f"**{article['title']}**")
                st.write(f"{article['desc']}")
                st.write(
                    f"**Published Date:** {article.get('date', 'N/A')}")
                st.write(f"[Read more]({article['link']})")
            st.write("---")

        # Generate HTML report
        if st.button("Generate HTML Report"):
            html_content = """
            <html>
            <head>
                <title>News Report</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    h1 { text-align: center; }
                    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    th { background-color: #f2f2f2; }
                    a { color: #3498db; text-decoration: none; }
                    a:hover { text-decoration: underline; }
                </style>
            </head>
            <body>
                <h1>News Report</h1>
                <table>
                    <tr>
                        <th>Language</th>
                        <th>Title</th>
                        <th>Date</th>
                        <th>Description</th>
                        <th>Link</th>
                    </tr>
            """

            for lang, articles in news_data.items():
                for article in articles:
                    title = article.get('title', 'N/A')
                    date = article.get('date', 'N/A')
                    desc = article.get('desc', 'N/A')
                    link = article.get('link', '#')
                    html_content += f"""
                    <tr>
                        <td>{lang}</td>
                        <td>{title}</td>
                        <td>{date}</td>
                        <td>{desc}</td>
                        <td><a href="{link}" target="_blank">Read more</a></td>
                    </tr>
                    """

            html_content += """
                </table>
            </body>
            </html>
            """

            output_path = "news_report.html"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            st.success("HTML report generated successfully!")
            with open(output_path, "rb") as f:
                st.download_button(
                    label="Download HTML Report",
                    data=f,
                    file_name="news_report.html",
                    mime="text/html"
                )


# Page 5: Custom Search
elif page == "Custom Search":
    st.header("Custom Search Page")

    # Custom search input
    custom_query = st.text_input("Enter your custom search query")

    # Step 2: Select language(s)
    # Directly use the languages from the Excel file as before
    df = pd.read_excel("data/names.xlsx")

    languages = list(df.columns[1:])
    languages_options = ['English'] + languages

    selected_languages = st.multiselect(
        "Select Languages",
        languages_options,
        default=['English']  # Set "English" as the default selection
    )

    if st.button("Fetch News with GoogleNews"):
        st.subheader("Fetched News Articles:")

        # Fetch and display news
        for language in selected_languages:
            lang_code = LANGUAGE_TO_REGION.get(language, 'en')
            articles = fetch_news_with_google_news(
                custom_query, lang=lang_code)

            st.write(
                f"**Search Query:** {custom_query} (Language: {language})")
            for article in articles:
                st.write(f"**{article['title']}**")
                st.write(f"{article['desc']}")
                st.write(f"**Published Date:** {article.get('date', 'N/A')}")
                st.write(f"[Read more]({article['link']})")
            st.write("---")
