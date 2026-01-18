#
# Standard library
import os
import json
import re
import html

# Third-party libraries
import pandas as pd
import numpy as np

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Optional imports (enable if needed)
# from thefuzz import fuzz
# from selenium_scraper import get_top_comments

# Example usage for optional import:
# name = "Kurtis Pykes"
# full_name = "Kurtis K D Pykes"
# print(f"Similarity score: {fuzz.ratio(name, full_name)}")

INPUT_CSV = ""

YOUTUBE_API_KEY = ""

START_INDEX_IN_SPOTIFY_DATA = 0
TOTAL_SONGS = 0

MAX_COMMENTS_PER_VIDEO = 0

# Load JSON data from a file
with open("parameters_file.json", "r", encoding="utf-8") as file:

    parameters_json = json.load(file) # Parses JSON into a Python dictionary
    
    INPUT_CSV = parameters_json["input_csv"]
    # YOUTUBE_API_KEY = parameters_json["youtube_api_key"]
    YOUTUBE_API_KEY = parameters_json["youtube_api_key_2"]
    START_INDEX_IN_SPOTIFY_DATA = parameters_json["start_index_in_spotify_data"]
    TOTAL_SONGS = parameters_json["total_songs"]
    MAX_COMMENTS_PER_VIDEO = parameters_json["max_comments_per_video"]
    
# Initialize YouTube client and read input CSV
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
df_spotify = pd.read_csv(INPUT_CSV)

def extract_and_return_top_50_comments_if_enabled(video_id, youtube):

    global MAX_COMMENTS_PER_VIDEO
    comments = []

    comments = list()
    top_comments = list()
    sorted_comments = list()        
    error_message = "" 
    try:
        next_page_token = None
        while len(comments) < MAX_COMMENTS_PER_VIDEO:
            comment_response = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=50,
                pageToken=next_page_token,
                order='relevance'
            ).execute()

            for comment in comment_response.get('items', []):
                snippet = comment['snippet']['topLevelComment']['snippet']
                comments.append({
                    "comment": html.unescape(snippet['textOriginal']),
                    "likes": snippet['likeCount']
                })

                # print({
                #     "comment": html.unescape(snippet['textOriginal']),
                #     "likes": snippet['likeCount']
                #     }
                # )

            next_page_token = comment_response.get('nextPageToken')
            if not next_page_token:
                break

        # Sort comments by likes (descending) and limit to top 50
        sorted_comments = sorted(comments, key=lambda x: x['likes'], reverse=True)[:MAX_COMMENTS_PER_VIDEO]
        top_comments = [(c['comment'], c['likes']) for c in sorted_comments]

    except HttpError as e:
        # raise e
        if e.resp.status == 403 and 'commentsDisabled' in str(e):
            print(f"Comments are disabled for video ID {video_id}.")
            error_message = str(e)
        error_message = str(e)            

    return comments, top_comments, sorted_comments, error_message 


def clean_text(text):
    # Remove special characters and convert to lowercase
    return re.sub(r'[^a-zA-Z0-9\s]', '', text).lower()

# Read merged Spotify/YouTube mapping CSV and inspect

df_spotify_youtube = pd.read_csv( "Spotify_Youtube.csv" , index_col = False, usecols=lambda column: column not in ["Unnamed: 0"])  


print(df_spotify_youtube.head())

# (Re)initialize YouTube client if needed

youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Tracking structures
skipped_indices = list()

# Quick size check
print(len(df_spotify_youtube), len(df_spotify_youtube)*10)

# Initialize collections

collection_of_disabled_videos = list()

collection_of_curated_data = list()

counter = 0
total_videos_processed = 0

max_results = 5
for index, row in df_spotify_youtube.iterrows():

    if counter < START_INDEX_IN_SPOTIFY_DATA:
        counter+=1
        continue

    if (total_videos_processed > TOTAL_SONGS):
        break
        
    try:
        spotify_id = row['Uri'].split(":")[2]    
        youtube_video_id = row['Url_youtube'].split("=")[1]
    except Exception as e:
        skipped_indices.append( (index, str(e) ) )
        continue

    # print(spotify_id, youtube_video_id)
    comments, top_comments, sorted_comments, error_message = extract_and_return_top_50_comments_if_enabled(youtube_video_id, youtube)

    # print(top_comments)
    
    if error_message:
        collection_of_disabled_videos.append(
            {
                'spotify_id': row.get('id'),
                # 'song_name': song_name,
                # 'artist_name': artist_name,
                'video_id' : youtube_video_id,
                # 'video_title' : video_title,
                'error_message' : error_message
            }
        )
        
        continue

    for comment in top_comments:
        collection_of_curated_data.append(
    
                {
                    'spotify_id': spotify_id,
                    # 'song_name': song_name,
                    # 'artist_name': artist_name,
                    'video_id' : youtube_video_id,
                    # 'video_title' : video_title,
                    'comment' : comment[0],
                    'likes' : comment[1]
                }
             
        )    
    if not counter%1000:
        print(counter)
        
    total_videos_processed += 1

# Create DataFrame from curated comments

df = pd.DataFrame(collection_of_curated_data)

print(df.head())

print(len(df))

# Save the DataFrame to a CSV file

df.to_csv("C:/Users/shubh/programming_work/git_repos/NU/courses_and_academics/data_mining/proj/spotify_youtube_comment_88247.csv", index=False)  # index=False ensures the index is not stored

# Save failed/disabled collection

df_failed = pd.DataFrame(collection_of_curated_data)
df_failed.to_csv("C:/Users/shubh/programming_work/git_repos/NU/courses_and_academics/data_mining/proj/spotify_youtube_comment_f.csv", index=False)  # index=False ensures the index is not stored
