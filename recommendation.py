
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

USER_DATA_FILE = 'user_data/user_interactions.csv'

# Hàm ghi dữ liệu hành vi người dùng
def log_user_interaction(query, video_id):
    df = pd.DataFrame({'query': [query], 'video_id': [video_id]})
    if not os.path.isfile(USER_DATA_FILE):
        df.to_csv(USER_DATA_FILE, index=False, mode='w', header=True)
    else:
        df.to_csv(USER_DATA_FILE, index=False, mode='a', header=False)

def build_recommendation_model():
    # Đọc dữ liệu hành vi người dùng
    interactions = pd.read_csv(USER_DATA_FILE)

    # Loại bỏ các giá trị NaN trong cột 'query'
    interactions = interactions[interactions['query'].notna()]

    # Tạo ma trận tần suất
    count_vectorizer = CountVectorizer()
    count_matrix = count_vectorizer.fit_transform(interactions['query'])

    # Tính toán độ tương đồng cosine
    cosine_sim = cosine_similarity(count_matrix)

    return cosine_sim, interactions

def recommend_videos(video_id):
    cosine_sim, interactions = build_recommendation_model()

    # Tìm chỉ số của video trong danh sách
    idx = interactions[interactions['video_id'] == video_id].index[0]

    # Lấy độ tương đồng cho video này
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sắp xếp các video tương tự
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Lấy danh sách video tương tự
    video_indices = [i[0] for i in sim_scores[1:6]]  # Lấy 5 video tương tự
    recommended_videos = interactions.iloc[video_indices]

    return recommended_videos['video_id'].tolist()

