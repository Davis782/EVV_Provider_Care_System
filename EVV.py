import streamlit as st
from hugchat import hugchat
from hugchat.login import Login
from hugchat.message import ChatError  # Import ChatError class
import docx
from PyPDF2 import PdfReader
import sqlite3
import os
import requests  # Import requests library
import json  # Ensure you have this import for JSON handling

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
    st.markdown(
        'The Exact Solution of Pi and What it Means website [blog](https://exact-solution-of-pi.onrender.com/)')

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant", "content": "How may I help you?"}]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "content" in message:
            st.write(message["content"])
        else:
            st.write("No content available.")

# Handle file uploads
uploaded_files = st.file_uploader("Upload multiple documents", type=["txt", "pdf", "docx", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        file_updated = True  # Mark that a file has been updated
        if uploaded_file.type == "text/plain":
            content = uploaded_file.read().decode("utf-8")
            user_input += f"Content from {uploaded_file.name}:\n{content}\n"
        elif uploaded_file.type == "application/pdf":
            pdf_reader = PdfReader(uploaded_file)
            pdf_text = ""
            for page in pdf_reader.pages:
                pdf_text += page.extract_text() + "\n"
            user_input += f"Content from {uploaded_file.name}:\n{pdf_text}\n"
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(uploaded_file)
            doc_text = "\n".join([para.text for para in doc.paragraphs])
            user_input += f"Content from {uploaded_file.name}:\n{doc_text}\n"
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            # Read Excel file using built-in methods
            excel_text = ""
            for sheet in pd.read_excel(uploaded_file, sheet_name=None):
                for index, row in sheet.iterrows():
                    excel_text += f"{row.to String()}\n"
            user_input += f"Content from {uploaded_file.name}:\n{excel_text}\n"

# Function for generating LLM response
def generate_response(prompt_input, email, passwd):
    try:
        # Hugging Face Login
        sign = Login(email, passwd)
        cookies = sign.Login()
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
            st.error(f"RequestError: {e}")
        except Exception as e:
            st.error(f"AnErrorOccurred: {e}")

# User-provided prompt
if prompt := st.chat_input(disabled=not (hf_email and hf_pass):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Function to insert line breaks into long strings
def insert_line_breaks(text, max_line_length=75):
    """Insert line breaks into long strings."""
    if isinstance(text, str):
        lines = []
        for i in range(0, len(text), max_line_length):
            lines.append(text[i:i + max_lineLength])
        return '\n'.join(lines)
    else:
        return str(text)  # Convert to string if the type is not recognized

# Handle URL input
url_input = st.text_input("Enter a URL:", key="url_input")
if url_input:
    user_input += f"URL: {url_input}\n"
    # Generate a response based on the URL
    with st.spinner("Fetching information from the URL:"):
        try:
            # You can customize the prompt to ask for information about the URL
            url_response = generate_response(f"Provide information about the following URL: {url_input}", hf_email, hf_pass)
            if url_response:
                url_response = insert_lineBreaks(url_response)  # Insert line breaks into response
                st.write(url_response)
                st.session_state.messages.append({"role": "assistant", "content": url_response})
            else:
                st.write("No response generated for the URL.")
        except Exception as e:
            st.error(f"Error fetching information from the URL: {e}")

# Link for ottodev-bolt.myaibuilt App Building tool
# Define the website URL for app building tool
website_url_2 = 'https://ottodev-bolt.myaibuilt.app/'

# Create a clickable link to the website
st.sidebar.markdown(f"[App Building Tool]({website_url_2})", unsafe_allow_html=True)

# Link for FreeConference Call Tool
# Define the website URL for video transcript
website_url_1 = 'https://www.freeconferencecall.com/'

# Create a clickable link to the website
st.sidebar.markdown(f"[FreeConference Call Tool]({website_url_1})", unsafe Allow Html=True)

# Define the website URL for video transcript
website_url = 'https://transcriptal.com
