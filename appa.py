import asyncio
import streamlit as st
import pandas as pd
import google.generativeai as genai
from telegram import Bot
import telegram
from PIL import Image  # Import for image handling

# Set up Streamlit page configuration - this must come first
st.set_page_config(
    page_title="ArticleFatafat - Article Summarizer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load and display the logo
logo_path = "asset/logo_image.png"  # Replace with your image filename
logo = Image.open(logo_path)
st.image(logo, width=100)  # Adjust width as needed

# Telegram Bot Constants
TOKEN = "7702024552:AAHmnl2JO0MQ08tbPv53pa97jrnMQIBb2gg"
CHAT_ID = "1215055486"

# Configure the Gemini API
genai.configure(api_key="AIzaSyCgsv4OA_ZlV-73_HN_Z1Jfhdtn5mibWq0")  # Replace with your API key
model = genai.GenerativeModel("gemini-1.5-flash")

st.title("Get bite sized articles")
st.write("Upload a CSV file, generate summaries, and send them to Telegram.")

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file...", type=["csv"])

# Function to summarize article content using Gemini API
def summarize_article(article_content):
    """
    Summarizes the given article content using Gemini API.
    Args:
        article_content (str): The full content of the article.
    Returns:
        str: Generated summary from the API.
    """
    prompt = f"You are an expert in writing and have to summarize this content: {article_content}"
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Summary generation failed: {e}"

async def send_summary_to_telegram_async(summary):
    """
    Sends the given summary to Telegram asynchronously.
    Args:
        summary (str): The summary text to send.
    """
    try:
        bot = Bot(token=TOKEN)
        await bot.send_message(chat_id=CHAT_ID, text=summary)
        st.success("Summary sent successfully!")
    except telegram.error.TelegramError as e:
        st.error(f"Telegram Error: {e}")
    except Exception as e:
        st.error(f"Failed to send summary: {e}")

def send_summary_to_telegram(summary):
    """
    Wrapper function to handle asynchronous sending of Telegram messages.
    Args:
        summary (str): The summary text to send.
    """
    asyncio.run(send_summary_to_telegram_async(summary))

if uploaded_file is not None:
    # Load and display data
    df = pd.read_csv(uploaded_file)
    st.write("Preview of uploaded data:")
    st.dataframe(df.head())

    # Check if required columns are present
    if "Article Name" in df.columns and "Article Content" in df.columns:
        st.write("Generate summaries for the latest 2 articles:")

        summaries = []

        if st.button("Generate"):
            # Process the first 2 rows (index 0 and 1)
            for index in [0, 1]:
                if index < len(df):
                    article_name = df.loc[index, "Article Name"]
                    article_content = df.loc[index, "Article Content"]
                    summary = summarize_article(article_content)
                    summaries.append({"Article Name": article_name, "Summary": summary})

            # Store summaries in session state
            st.session_state['summaries'] = summaries

        if 'summaries' in st.session_state:
            st.text_area("Generated Summaries", value="\n\n".join(
                [f"Article: {item['Article Name']}\nSummary: {item['Summary']}" for item in st.session_state['summaries']]
            ), height=300)

            if st.button("Send Summaries to Telegram", key="send"):
                summary_text = "\n\n".join(
                    [f"Article: {item['Article Name']}\nSummary: {item['Summary']}" for item in st.session_state['summaries']]
                )
                send_summary_to_telegram(summary_text)
        else:
            st.error("The uploaded file must contain 'Article Name' and 'Article Content' columns.")
