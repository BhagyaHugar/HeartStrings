import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os

class CollaborativeFilter:
    def __init__(self, history_path='dataset/listening_history.csv'):
        self.history_path = history_path
        self.user_item_matrix = None
        self.user_similarity_df = None
        self.load_and_train()

    def load_and_train(self):
        if not os.path.exists(self.history_path):
            print("Listening history dataset not found!")
            return
            
        df = pd.read_csv(self.history_path)
        
        # Create User-Item Matrix
        # Using 'rating' as the value
        self.user_item_matrix = df.pivot_table(
            index='user_id', 
            columns='track_id', 
            values='rating'
        ).fillna(0)
        
        # Calculate User-User Cosine Similarity
        user_similarity = cosine_similarity(self.user_item_matrix)
        self.user_similarity_df = pd.DataFrame(
            user_similarity, 
            index=self.user_item_matrix.index, 
            columns=self.user_item_matrix.index
        )

    def get_user_recommendations(self, user_id, top_n=10):
        if self.user_item_matrix is None or user_id not in self.user_item_matrix.index:
            return []

        # Get top similar users
        similar_users = self.user_similarity_df[user_id].sort_values(ascending=False)[1:6] # Top 5 similar users
        
        recommended_tracks = {}
        user_listened_tracks = set(self.user_item_matrix.columns[self.user_item_matrix.loc[user_id] > 0])

        for sim_user, sim_score in similar_users.items():
            sim_user_tracks = self.user_item_matrix.loc[sim_user]
            # Tracks liked by similar user (> 3 rating)
            good_tracks = sim_user_tracks[sim_user_tracks > 3].index
            
            for track in good_tracks:
                if track not in user_listened_tracks:
                    if track not in recommended_tracks:
                        recommended_tracks[track] = 0
                    recommended_tracks[track] += sim_score * sim_user_tracks[track]
                    
        # Sort by weighted score
        sorted_recommendations = sorted(recommended_tracks.items(), key=lambda x: x[1], reverse=True)
        
        # Return top N track IDs
        return [track for track, score in sorted_recommendations[:top_n]]

if __name__ == '__main__':
    clf = CollaborativeFilter('../dataset/listening_history.csv')
    print("Collaborative Filter loaded.")
