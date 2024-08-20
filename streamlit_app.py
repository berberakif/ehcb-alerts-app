import streamlit as st
import pandas as pd
from urllib.parse import quote

# Dictionary mapping languages to Google region codes
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
}

# Function to generate Google Alerts URL


def generate_alert_url(search_term, region_code=""):
    base_url = "https://www.google.com/alerts?hl=en&q="
    return f"{base_url}{quote(search_term)}&gl={region_code}"


# Streamlit interface
st.title("Google Alerts URL Generator")

# File upload
uploaded_file = "data/names.xlsx"

if uploaded_file:
    # Load the Excel file
    df = pd.read_excel(uploaded_file)

    # Coach selection
    coach = st.selectbox("Select a Coach", df['Name'].unique())

    # Language selection
    languages = st.multiselect("Select Languages", df.columns[1:])

    if st.button("Generate URLs"):
        st.subheader("Generated Google Alerts URLs:")

        # Generate URLs
        urls = []
        for language in languages:
            search_term = df.loc[df['Name'] == coach, language].values[0]
            region_code = LANGUAGE_TO_REGION.get(language, "")
            url = generate_alert_url(search_term, region_code)
            urls.append((language, url))

        # Display URLs
        for language, url in urls:
            st.markdown(f"[{language} Alert]({url})")

        # Option to download the URLs as a CSV file
        download_df = pd.DataFrame(urls, columns=['Language', 'URL'])
        csv = download_df.to_csv(index=False)
        st.download_button(label="Download URLs as CSV",
                           data=csv, mime="text/csv")
