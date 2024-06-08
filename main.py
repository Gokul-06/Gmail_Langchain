import streamlit as st
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
import email
import openai

# Set your OpenAI API key here
os.environ['OPENAI_API_KEY'] = 'your-openai-api-key'

# Define OAuth scopes and client secret file
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.compose']
CLIENT_SECRET_FILE = 'client_secret_137685561772-f71sepcpmv01e4jkiqh2ageh941cc97c.apps.googleusercontent.com.json'  # Adjust the path to your client_secret.json
TOKEN_FILE = 'token.json'

# Function to load credentials
def load_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return creds

# Initialize the Gmail API
def get_gmail_service():
    creds = load_credentials()
    service = build('gmail', 'v1', credentials=creds)
    return service

# Function to search emails
def search_emails(service, query):
    result = service.users().messages().list(userId='me', q=query).execute()
    messages = result.get('messages', [])
    return messages

# Function to generate intelligent responses using OpenAI
def generate_response(email_text):
    response = openai.Completion.create(
        engine="davinci",
        prompt="Summarize this email and suggest a polite response:\n\n" + email_text,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Streamlit UI
st.title('Gmail AI Agent with Streamlit and OpenAI')

def main():
    st.sidebar.title("Gmail Actions")
    action = st.sidebar.selectbox("Choose an action", ["None", "Search Emails", "Generate Response"])

    service = get_gmail_service()

    if action == "Search Emails":
        query = st.text_input("Enter search query", "invoice")
        if st.button("Search"):
            messages = search_emails(service, query)
            for msg in messages:
                st.write(msg)

    elif action == "Generate Response":
        email_id = st.text_input("Enter email ID")
        if st.button("Generate"):
            # Fetch the email text using a helper function (not shown here)
            email_text = "Simulated email content for testing"  # Placeholder text
            response = generate_response(email_text)
            st.write("Suggested Response:")
            st.write(response)

if __name__ == "__main__":
    main()
