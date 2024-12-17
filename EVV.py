import streamlit as st
from hugchat import hugchat
from hugchat.login import Login
from hugchat.message import ChatError  # Import ChatError class
import pandas as pd
import docx
from PyPDF2 import PdfReader
import sqlite3
import os
import requests  # Import requests libra

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

# # Display chat messages
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.write(message["content"])

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



# User-provided prompt
if prompt := st.chat_input(disabled=not (hf_email and hf_pass)):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Define a simple Message class for demonstration purposes
class Message:
    def __init__(self, content):
        self.content = content

# Function to insert line breaks into long strings
def insert_line_breaks(text, max_line_length=75):
    """Insert line breaks into long strings."""
    if isinstance(text, str):
        lines = []
        for i in range(0, len(text), max_line_length):
            lines.append(text[i:i+max_line_length])
        return '\n'.join(lines)
    elif isinstance(text, Message):  # Assuming Message is the type of the response object
        return text  # Return the Message object as it is
    else:
        return str(text)  # Convert to string if the type is not recognized

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = generate_response(prompt, hf_email, hf_pass)
                response = insert_line_breaks(response)  # Insert line breaks into response
                st.write(response)
            except ChatError as e:
                st.error(f"ChatError: {e}")
                st.error("An error occurred while processing the chat response.")
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)

# # Generate a new response if last message is not from assistant
# if st.session_state.messages[-1]["role"] != "assistant":
#     with st.chat_message("assistant"):
#         with st.spinner("Thinking..."):
#             try:
#                 response = generate_response(prompt, hf_email, hf_pass)
#                 if response:
#                     response = insert_line_breaks(response)  # Insert line breaks into response
#                     message = {"role": "assistant", "content": response}
#                 else:
#                     message = {"role": "assistant", "content": "Sorry, I couldn't generate a response."}
#             except Exception as e:
#                 st.error(f"An error occurred: {e}")
#                 message = {"role": "assistant", "content": "An error occurred while generating the response."}
#     message = {"role": "assistant", "content": response}
#     st.session_state.messages.append(message)


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

# Handle URL input
url_input = st.text_input("Enter a URL:", key="url_input")
if url_input:
    user_input += f"URL: {url_input}\n"
    # Generate a response based on the URL
    with st.spinner("Fetching information from the URL..."):
        try:
            # You can customize the prompt to ask for information about the URL
            url_response = generate_response(f"Provide information about the following URL: {url_input}", hf_email, hf_pass)
            if url_response:
                url_response = insert_line_breaks(url_response)  # Insert line breaks into response
                st.write(url_response)
                st.session_state.messages.append({"role": "assistant", "content": url_response})
            else:
                st.write("No response generated for the URL.")
        except Exception as e:
            st.error(f"Error fetching information from the URL: {e}")



# Link for ottodev-bolt.myaibuilt App Building Tool
# Define the website URL for App Building Tool
website_url_2 = 'https://ottodev-bolt.myaibuilt.app/'

# Create a clickable link to the website
st.sidebar.markdown(f"[App Building Tool]({website_url_2})", unsafe_allow_html=True)


# Link for FreeConference Call Tool
# Define the website URL for video transcript
website_url_1 = 'https://www.freeconferencecall.com/'

# Create a clickable link to the website
st.sidebar.markdown(f"[FreeConference Call Tool]({website_url_1})", unsafe_allow_html=True)

# Define the website URL for video transcript
website_url = 'https://transcriptal.com/'

# Create an iframe and embed it in the Streamlit app
iframe_html = f'<iframe src="{website_url}" width="700" height="450"></iframe>'

# Display the YouTube video URL input field
youtube_video_input = st.text_input(
    "Enter a YouTube video URL:", key="youtube_video_input")

# Check if the user has entered a YouTube video URL
if youtube_video_input:
    # Embed the website with the YouTube video
    st.markdown(iframe_html, unsafe_allow_html=True)
    # Display the YouTube video URL
    st.write(f"YouTube Video URL: {youtube_video_input}")

    # Add functionality to execute transcript for the YouTube video here
    # This can include calling an API or service to generate the transcript

    # For demonstration purposes, you can display a placeholder transcript
    # YouTube video input
    st.write("Transcript: This is a placeholder transcript for the YouTube video.")



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
                st.text_area(f"{sender}: {message}")

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
        "Please click on '>' in the upper left hand corner to 1. upload a document or 2. enter a text below or 3. Enter a YouTube video, provide a URL above to generate a response.")
