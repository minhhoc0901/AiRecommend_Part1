
from flask import Flask, render_template, request
from googleapiclient.discovery import build
import os
import pandas as pd
from recommendation import recommend_videos, log_user_interaction

app = Flask(__name__)

API_KEY = 'AIzaSyCVUxi32JXtp082wuZI0m3lvwf857g1_os'

YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# Tạo thư mục user_data nếu chưa tồn tại
if not os.path.exists('user_data'):
    os.makedirs('user_data')

USER_DATA_FILE = 'user_data/user_interactions.csv'

# Trang chủ
@app.route('/', methods=['GET', 'POST'])
def index():
    videos = []
    if request.method == 'POST':
        query = request.form['query']
        videos = youtube_search(query)

        # Ghi lại hành vi xem của người dùng
        for video in videos:
            log_user_interaction(query, video['videoId'])

    # Đề xuất video khi load trang
    else:
        # Đọc dữ liệu hành vi người dùng
        if os.path.isfile(USER_DATA_FILE):
            interactions = pd.read_csv(USER_DATA_FILE)
            interactions = interactions[interactions['query'].notna()]
            if not interactions.empty:
                last_query = interactions['query'].mode()[0]  # Lấy truy vấn phổ biến nhất
                videos = youtube_search(last_query)

                # Ghi lại hành vi xem
                for video in videos:
                    log_user_interaction(last_query, video['videoId'])

    return render_template('index.html', videos=videos)

# Trang video chi tiết
@app.route('/video/<video_id>')
def video_detail(video_id):
    recommended_videos = recommend_videos(video_id)
    video_data = youtube_get_video_data(video_id)

    return render_template('video_detail.html', video=video_data, recommended_videos=recommended_videos)

# Hàm tìm kiếm video trên YouTube
def youtube_search(query, max_results=10):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)
    
    search_response = youtube.search().list(
        q=query,
        part='snippet',
        maxResults=max_results
    ).execute()

    videos = []
    for search_result in search_response.get('items', []):
        if search_result['id']['kind'] == 'youtube#video':
            video_data = {
                'videoId': search_result['id']['videoId'],
                'title': search_result['snippet']['title'],
                'description': search_result['snippet']['description'],
                'thumbnail': search_result['snippet']['thumbnails']['high']['url']
            }
            videos.append(video_data)
    
    return videos

def youtube_get_video_data(video_id):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)
    video_response = youtube.videos().list(part='snippet', id=video_id).execute()
    
    if video_response['items']:
        video_data = video_response['items'][0]
        return {
            'videoId': video_data['id'],
            'title': video_data['snippet']['title'],
            'description': video_data['snippet']['description'],
            'thumbnail': video_data['snippet']['thumbnails']['high']['url']
        }
    return None

if __name__ == '__main__':
    app.run(debug=True)

