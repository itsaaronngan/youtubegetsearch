from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import isodate
from datetime import datetime, timedelta
import os

# Function to set up YouTube client with OAuth2
def get_authenticated_service():
    SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
    CLIENT_SECRETS_FILE = 'client_secrets.json'  # Path to your client_secrets.json file

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('youtube', 'v3', credentials=creds)

# Function to search YouTube videos
def youtube_search(youtube, search_term, max_results, time_filter):
    published_after = datetime.now() - timedelta(weeks=1) if time_filter == 'W' \
        else datetime.now() - timedelta(days=30) if time_filter == 'M' \
        else datetime.now() - timedelta(days=365) if time_filter == 'Y' \
        else None

    if published_after:
        published_after_str = published_after.isoformat("T") + "Z"
    else:
        raise ValueError("Time filter must be 'W', 'M', or 'Y'")

    response = youtube.search().list(
        q=search_term,
        part='id,snippet',
        maxResults=max_results,
        type='video',
        publishedAfter=published_after_str,
        relevanceLanguage='en'
    ).execute()

    for item in response['items']:
        video_id = item['id']['videoId']
        print(f'Video ID: {video_id}')

# Main function
if __name__ == '__main__':
    # Setting up OAuth2 authenticated YouTube client
    youtube = get_authenticated_service()

    # Example usage of the YouTube search function
    search_term = "example search term"  # Replace with your search term
    max_results = 10  # Set the number of results
    time_filter = 'W'  # Set the time filter (W, M, Y)

    youtube_search(youtube, search_term, max_results, time_filter)
