import streamlit as st
import pandas as pd
import PyPDF2
import docx
import os
import requests
import json

# Initialize variables
user_input = ""
chat_history = []
file_updated = False
extracted_content = []  # List to store extracted content from files

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
        st.write(message["content"])

# Handle file uploads
uploaded_files = st.file_uploader("Upload multiple documents", type=["txt", "pdf", "docx", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        file_updated = True  # Mark that a file has been updated
        if uploaded_file.type == "text/plain":
            content = uploaded_file.read().decode("utf-8")
            extracted_content.append(f"Content from {uploaded_file.name}:\n{content}\n")
        elif uploaded_file.type == "application/pdf":
            # Process PDF file
            reader = PyPDF2.PdfReader(uploaded_file)
            pdf_content = ""
            for page in reader.pages:
                pdf_content += page.extract_text() + "\n"
            extracted_content.append(f"Content from {uploaded_file.name}:\n{pdf_content}\n")
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            # Process DOCX file
            doc = docx.Document(uploaded_file)
            doc_content = "\n".join([para.text for para in doc.paragraphs])
            extracted_content.append(f"Content from {uploaded_file.name}:\n{doc_content}\n")
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            excel_data = pd.read_excel(uploaded_file, sheet_name=None)
            excel_text = ""
            for sheet_name, sheet_data in excel_data.items():
                excel_text += f"Sheet: {sheet_name}\n"
                excel_text += sheet_data.to_string(index=False) + "\n"
            extracted_content.append(f"Content from {uploaded_file.name}:\n{excel_text}\n")

# Show the links after a file upload is completed
website_url_2 = 'https://ottodev-bolt.myaibuilt.app/'
website_url_1 = 'https://www.freeconferencecall.com/'
st.sidebar.markdown(f"[App Building Tool]({website_url_2})", unsafe_allow_html=True)
st.sidebar.markdown(f"[FreeConference Call Tool]({website_url_1})", unsafe_allow_html=True)

# Function for generating LLM response
def generate_response(prompt_input, email, passwd):
    try:
        # Placeholder for actual LLM response generation
        # This is where you would integrate with the LLM API
        response = f"Response to: {prompt_input}"
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

    # Combine user input with extracted content for the LLM
    combined_input = prompt + "\n" + "\n".join(extracted_content)

    # Generate response
    response = generate_response(combined_input, hf_email, hf_pass)
    if response:
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)

# Function to insert line breaks into long strings
def insert_line_breaks(text, max_line_length=75):
    """Insert line breaks into long strings."""
    if isinstance(text, str):
        lines = []
        for i in range(0, len(text), max_line_length):
            lines.append(text[i:i + max_line_length])
        return '\n'.join(lines)
    else:
        return str(text)  # Convert to string if the type is not recognized

# Handle URL input
url_input = st.text_input("Enter a URL:", key="url_input")
if url_input:
    combined_input += f"URL: {url_input}\n"
    with st.spinner("Fetching information from the URL..."):
        try:
            url_response = generate_response(f"Provide information about the following URL: {url_input}", hf_email, hf_pass)
            if url_response:
                url_response = insert_line_breaks(url_response)  # Insert line breaks into response
                st.write(url_response)
                st.session_state.messages.append({"role": "assistant", "content": url_response})
            else:
                st.write("No response generated for the URL.")
        except Exception as e:
            st.error(f"Error fetching information from the URL: {e}")

# Link for ottodev-bolt.myaibuilt App Building tool
st.sidebar.markdown(f"[App Building Tool]({website_url_2})", unsafe_allow_html=True)

# Link for FreeConference Call Tool
st.sidebar.markdown(f"[FreeConference Call Tool]({website_url_1})", unsafe_allow_html=True)
