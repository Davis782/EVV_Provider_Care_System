import streamlit as st
from hugchat import hugchat
from hugchat.login import Login
import pandas as pd
import docx
from PyPDF2 import PdfReader
import sqlite3
import os

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
        'Learn how to build this app in this [blog]('The Exact Solution of Pi and What it Means website [blog](https://exact-solution-of-pi.onrender.com/)')
# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant", "content": "How may I help you?"}]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Function for generating LLM response


def generate_response(prompt_input, email, passwd):
    # Hugging Face Login
    sign = Login(email, passwd)
    cookies = sign.login()
    # Create ChatBot
    chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
    return chatbot.chat(prompt_input)


# User-provided prompt
if prompt := st.chat_input(disabled=not (hf_email and hf_pass)):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_response(prompt, hf_email, hf_pass)
            st.write(response)
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)
# User-provided prompt

# Handle language input
if "language" not in st.session_state:
    st.session_state.language = "en"  # Default language is English

# Upload .db file and Google Sheets ID
uploaded_db_file = st.sidebar.file_uploader(
    "Upload a .db file", type=["db"], key="db_file")
google_sheets_id = st.sidebar.text_input(
    "Enter Google Sheets ID:", key="google_sheets_id")

# User input: Upload multiple documents
uploaded_files = st.sidebar.file_uploader(
    "Upload multiple documents", accept_multiple_files=True)

# Process uploaded documents
if uploaded_files:
    file_updated = True
    for idx, uploaded_file in enumerate(uploaded_files):
        file_type = uploaded_file.type
        if file_type == 'text/plain':
            document_text = uploaded_file.getvalue().decode("utf-8", errors='replace')
            user_input += document_text
        elif file_type == 'application/pdf':
            pdf_reader = PdfReader(uploaded_file)
            num_pages = len(pdf_reader.pages)
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                document_text = page.extract_text()
                user_input += document_text
        elif file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            doc = docx.Document(uploaded_file)
            document_text = '\n'.join(
                [paragraph.text for paragraph in doc.paragraphs])
            user_input += document_text
        elif file_type == 'text/csv':
            df = pd.read_csv(uploaded_file)
            document_text = df.to_string(index=False)
            user_input += document_text
        elif file_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            df = pd.read_excel(uploaded_file)
            document_text = df.to_string(index=False)
            user_input += document_text

# URL input
url_input = st.text_input("Enter a URL:", key="url_input")
if url_input:
    user_input += f"URL: {url_input}\n"

# YouTube video input
youtube_video_input = st.text_input(
    "Enter a YouTube video URL:", key="youtube_video_input")
if youtube_video_input:
    user_input += f"YouTube Video: {youtube_video_input}\n"

# Initialize Hugchat
chatbot = None

# Generate Response button
if file_updated or user_input:
    if st.button("Generate Response", key="generate_response_button"):
        with st.spinner("Thinking..."):
            # Hugging Face Login
            sign = Login(hf_email, hf_pass)
            cookies = sign.login()
            # Initialize Hugchat with credentials
            chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
            response = chatbot.chat(
                user_input, language=st.session_state.language)

            # Add Hugchat response to chat history
            chat_history.append(("Hugchat", response))

            # Display chat history
            st.subheader("Chat History")
            for sender, message in chat_history:
                st.text(f"{sender}: {message}")

    # Get the email input from the user
    email = st.text_input("Enter your email address:", key="email_input")

    if email:
        # Check if the email address is in the correct format
        if "@" in email and "." in email.split("@")[1]:
            # Split the email address on "@" and "."
            parts = email.split('@')
            username = parts[0]
            domain = parts[1].split('.')[0]

            # Concatenate to create the SQLite file name
            sqlite_filename = f"{username}_{domain}.db"

            # Get the current working directory
            current_directory = os.getcwd()

            # Save the SQLite file in the current working directory
            sqlite_filepath = os.path.join(current_directory, sqlite_filename)

            try:
                # Check if the file already exists
                if os.path.exists(sqlite_filepath):
                    # Append to the existing database
                    conn = sqlite3.connect(sqlite_filepath)
                    cursor = conn.cursor()
                    # Perform append operation here
                    st.write(
                        "Data appended to existing SQLite file: " + sqlite_filepath)
                else:
                    # Create a new database
                    conn = sqlite3.connect(sqlite_filepath)
                    cursor = conn.cursor()
                    # Perform initial database setup here
                    st.write(
                        "New SQLite file created in the working directory: " + sqlite_filepath)

                conn.commit()
                conn.close()
            except Exception as e:
                st.error(f"Error accessing the SQLite file: {e}")
        else:
            st.error("Invalid email address format")

        # Send email to the user (you can implement this functionality using an email service)

# Show a warning if no file or user input has been updated
if not file_updated and not user_input:
    st.warning(
        "Please upload a document, enter a text, provide a URL, or a YouTube video to generate a response.")

