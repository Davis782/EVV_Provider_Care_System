import streamlit as st
from hugchat import hugchat
from hugchat.login import Login
from hugchat.message import ChatError
import pandas as pd
import docx
from PyPDF2 import PdfReader
import sqlite3
import os
import requests
import json

# Initialize variables
user_input = ""  # Initialize user_input as an empty string
chat_history = []  # Initialize chat history list
file_updated = False  # Flag to track if a file or .db has been updated
messages = []  # Initialize chat history list

# App title
st.set_page_config(page_title="Care System")

# Streamlit UI components
st.title("EVV Provider Care System")

# Hugging Face Credentials
with st.sidebar:
    st.title('Care System')
    if ('EMAIL' in st.secrets) and ('PASS' in st.secrets):
        st.success('You are All System Go and Ready for Analysis!', icon='✅')
        hf_email = st.secrets['EMAIL']
        hf_pass = st.secrets['PASS']
    else:
        hf_email = st.text_input('Enter E-mail:', type='password')
        hf_pass = st.text_input('Enter password:', type='password')
        if not (hf_email and hf_pass):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your prompt message!', icon='  ')
    st.markdown('The Exact Solution of Pi and What it Means website [blog](https://exact-solution-of-pi.onrender.com/)')

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I help you?"}]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "content" in message:
            st.write(message["content"])
        else:
            st.write("No content available.")

# Function for generating LLM response
def generate_response(prompt_input, email, passwd):
    try:
        # Hugging Face Login
        sign = Login(email, passwd)
        cookies = sign.login()
        # Create ChatBot
        chatbot = hugchat.ChatBot(cookies=cookies.get_dict())

        # Get the response
        response = chatbot.chat(prompt_input)

        # Check if the response is valid JSON
        if isinstance(response, str):
            try:
                json_response = json.loads(response)
                return json_response
            except json.JSONDecodeError as json_error:
                st.error(f"JSON decode error: {json_error}")
                st.error(f"Raw response: {response}")
        else:
            return response
    except requests.exceptions.RequestException as e:
        st.error(f"Request error: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# User input: Upload multiple documents
uploaded_files = st.sidebar.file_uploader("Upload multiple documents", accept_multiple_files=True)

# Process uploaded documents
if uploaded_files:
    file_updated = True
    for idx, uploaded_file in enumerate(uploaded_files):
        file_type = uploaded_file.type
        if file_type == 'text/plain':
            document_text = uploaded_file.getvalue().decode("utf-8", errors='replace')
            user_input += document_text + "\n"
        elif file_type == 'application/pdf':
            pdf_reader = PdfReader(uploaded_file)
            num_pages = len(pdf_reader.pages)
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                document_text = page.extract_text()
                user_input += document_text + "\n"
        elif file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            doc = docx.Document(uploaded_file)
            document_text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            user_input += document_text + "\n"
        elif file_type == 'text/csv':
            df = pd.read_csv(uploaded_file)
            document_text = df.to_string(index=False)
            user_input += document_text + "\n"
        elif file_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            df = pd.read_excel(uploaded_file)
            document_text = df.to_string(index=False)
            user_input += document_text + "\n"

# User-provided prompt
if prompt := st.chat_input(disabled=not (hf_email and hf_pass)):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Combine user input with extracted content for the LLM
    combined_input = f"{prompt}\n\nExtracted Content:\n{user_input}"

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = generate_response(combined_input, hf_email, hf_pass)
                response = response if response else "Sorry, I couldn't generate a response."
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except ChatError as e:
                st.error(f"ChatError: {e}")
                st.error("An error occurred while processing the chat response.")

# Handle URL input
url_input = st.text_input("Enter a URL:", key="url_input")
if url_input:
    combined_input = f"URL: {url_input}\n"
    with st.spinner("Fetching information from the URL..."):
        try:
            url_response = generate_response(f"Provide information about the following URL: {url_input}", hf_email, hf_pass)
            if url_response:
                url_response = url_response if url_response else "No response generated for the URL."
                st.write(url_response)
                st.session_state.messages.append({"role": "assistant", "content": url_response})
            else:
                st.write("No response generated for the URL.")
        except Exception as e:
            st.error(f"Error fetching information from the URL: {e}")

# Link for Trickle App Building Tool
website_url_3 = 'https://app.trickle.so/project?id=proj_T5ErIh2arF'
st.sidebar.markdown(f"[App Building Tool]({website_url_3})", unsafe_allow_html=True)

# Link for ottodev-bolt.myaibuilt App Building Tool
website_url_2 = 'https://ottodev-bolt.myaibuilt.app/'
st.sidebar.markdown(f"[App Building Tool]({website_url_2})", unsafe_allow_html=True)

# Link for FreeConference Call Tool
website_url_1 = 'https://www.freeconferencecall.com/'
st.sidebar.markdown(f"[FreeConference Call Tool]({website_url_1})", unsafe_allow_html=True)

# Display YouTube video input field
youtube_video_input = st.text_input("Enter a YouTube video URL:", key="youtube_video_input")
if youtube_video_input:
    st.write(f"YouTube Video URL: {youtube_video_input}")
    st.write("Transcript: This is a placeholder transcript for the YouTube video.")

# Show a warning if no file or user input has been updated
if not file_updated and not user_input:
    st.warning("Please upload a document or enter text below to generate a response.")
