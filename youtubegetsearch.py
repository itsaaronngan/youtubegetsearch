from googleapiclient.discovery import build
import sys
import isodate
from datetime import datetime, timedelta

def youtube_search(search_term, max_results, time_filter):
    api_key = 'YO PUT YOUR API KEY HERE'
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Determine the time range for filtering
    if time_filter == 'W':
        published_after = datetime.now() - timedelta(weeks=1)
    elif time_filter == 'M':
        published_after = datetime.now() - timedelta(days=30)  # Approximate month
    elif time_filter == 'Y':
        published_after = datetime.now() - timedelta(days=365)  # Approximate year
    else:
        raise ValueError("Time filter must be 'W', 'M', or 'Y'")

    published_after_str = published_after.isoformat("T") + "Z"  # Format for YouTube API

    videos = []
    page_token = None
    while len(videos) < max_results:
        search_response = youtube.search().list(
            q=search_term,
            part='id,snippet',
            maxResults=50,  # Fetch up to 50 results at a time
            type='video',
            publishedAfter=published_after_str,
            relevanceLanguage='en',  # Filter for English language videos
            pageToken=page_token
        ).execute()

        for search_result in search_response.get('items', []):
            if search_result['id']['kind'] == 'youtube#video':
                video_id = search_result['id']['videoId']
                video_details = youtube.videos().list(
                    id=video_id,
                    part='contentDetails'
                ).execute()

                iso_duration = video_details['items'][0]['contentDetails']['duration']
                duration = isodate.parse_duration(iso_duration)
                if duration.total_seconds() >= 60:  # Exclude Shorts
                    videos.append(f"https://www.youtube.com/watch?v={video_id}")

                if len(videos) == max_results:
                    break

        if 'nextPageToken' in search_response:
            page_token = search_response['nextPageToken']
        else:
            break  # Exit if there are no more results

    return videos

if __name__ == "__main__":
    search_term = ' '.join(sys.argv[1:-2]).strip('<>')
    max_results = int(sys.argv[-2])
    time_filter = sys.argv[-1]
    results = youtube_search(search_term, max_results, time_filter)
    for url in results:
        print(url)
