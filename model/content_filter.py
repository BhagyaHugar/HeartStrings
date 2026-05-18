import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import os

class ContentFilter:
    def __init__(self, dataset_path='dataset/spotify_tracks.csv'):
        self.dataset_path = dataset_path
        self.df = None
        self.feature_matrix = None
        self.load_and_preprocess()

    def load_and_preprocess(self):
        if not os.path.exists(self.dataset_path):
            print("Dataset not found!")
            return
            
        self.df = pd.read_csv(self.dataset_path)
        
        # Features to use for content-based similarity
        features = ['energy', 'danceability', 'tempo', 'popularity', 'acousticness', 'valence']
        
        # Normalize features
        scaler = MinMaxScaler()
        self.feature_matrix = scaler.fit_transform(self.df[features])

    def get_similar_tracks(self, track_id, top_n=10):
        if self.df is None or track_id not in self.df['track_id'].values:
            return pd.DataFrame(columns=['track_id'])

        # Get index of the track
        idx = self.df.index[self.df['track_id'] == track_id].tolist()[0]
        
        # Compute cosine similarity between this track and all others
        similarities = cosine_similarity([self.feature_matrix[idx]], self.feature_matrix)[0]
        
        # Get top indices (excluding the track itself)
        top_indices = similarities.argsort()[-(top_n+1):][::-1][1:]
        
        similar_tracks = self.df.iloc[top_indices].copy()
        similar_tracks['similarity_score'] = similarities[top_indices]
        
        return similar_tracks

if __name__ == '__main__':
    cf = ContentFilter('../dataset/spotify_tracks.csv')
    print("Content Filter loaded.")
