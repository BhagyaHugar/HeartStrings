import pandas as pd
import random
try:
    from model.content_filter import ContentFilter
    from model.collaborative_filter import CollaborativeFilter
except ImportError:
    from content_filter import ContentFilter
    from collaborative_filter import CollaborativeFilter

class RecommendationEngine:
    def __init__(self, tracks_path='dataset/spotify_tracks.csv', history_path='dataset/listening_history.csv'):
        self.tracks_df = pd.read_csv(tracks_path)
        self.cf = ContentFilter(tracks_path)
        self.collab_f = CollaborativeFilter(history_path)

    def get_track_details(self, track_ids):
        return self.tracks_df[self.tracks_df['track_id'].isin(track_ids)].to_dict('records')

    def get_hybrid_recommendations(self, user_id, current_track_id=None, current_track_genre=None, mood=None, top_n=10):
        recommendations = []
        explanation_base = []

        # 1. Collaborative Filtering (User-based)
        if user_id:
            collab_tracks = self.collab_f.get_user_recommendations(user_id, top_n=top_n)
            recommendations.extend(collab_tracks)
            if collab_tracks:
                explanation_base.append("users with similar tastes enjoyed these")

        # 2. Content-Based Filtering (Item-based on current track)
        if current_track_id:
            content_tracks_df = self.cf.get_similar_tracks(current_track_id, top_n=top_n)
            content_tracks = content_tracks_df['track_id'].tolist()
            if content_tracks:
                recommendations.extend(content_tracks)
                try:
                    current_genre = self.tracks_df[self.tracks_df['track_id'] == current_track_id]['genre'].values[0]
                    explanation_base.append(f"they share similar energy and acousticness to the {current_genre} songs you are listening to")
                except IndexError:
                    pass
            elif current_track_genre:
                # If track not in db but we have genre
                matches = self.tracks_df[self.tracks_df['genre'].str.contains(current_track_genre, case=False, na=False)]
                if not matches.empty:
                    genre_tracks = matches.sample(n=min(top_n, len(matches)))['track_id'].tolist()
                    recommendations.extend(genre_tracks)
                    explanation_base.append(f"they belong to the {current_track_genre} genre you are listening to")

        # 3. Mood-Based Filtering
        if mood:
            mood_genre_map = {
                'Happy': ['Pop', 'Electronic'],
                'Relaxed': ['Acoustic', 'Classical'],
                'Romantic': ['Romantic', 'Acoustic'],
                'Sad': ['Acoustic', 'Jazz'],
                'Energetic': ['Rock', 'Hip-Hop', 'Electronic'],
                'Rainy Mood': ['Jazz', 'Acoustic'],
                'Focus Mode': ['Classical', 'Electronic']
            }
            preferred_genres = mood_genre_map.get(mood, ['Pop'])
            mood_tracks = self.tracks_df[self.tracks_df['genre'].isin(preferred_genres)].sample(n=top_n, replace=True)['track_id'].tolist()
            recommendations.extend(mood_tracks)
            explanation_base.append(f"they fit your '{mood}' mood perfectly")

        # Combine and deduplicate
        unique_recs = list(dict.fromkeys(recommendations))
        
        # Fallback if not enough recommendations
        if len(unique_recs) < top_n:
            popular_tracks = self.tracks_df.sort_values(by='popularity', ascending=False).head(top_n)['track_id'].tolist()
            unique_recs.extend(popular_tracks)
            unique_recs = list(dict.fromkeys(unique_recs))

        # Select top N
        final_recs = unique_recs[:top_n]
        track_details = self.get_track_details(final_recs)

        # Generate Explainable AI string
        if explanation_base:
            explanation = "Recommended because " + " and ".join(explanation_base) + "."
        else:
            explanation = "Recommended based on overall popularity."

        return {
            'recommendations': track_details,
            'explanation': explanation
        }

    def search_tracks(self, query, top_n=20):
        import requests
        try:
            # Dynamically fetch real-time search results from iTunes API for any language/song
            res = requests.get(f"https://itunes.apple.com/search?term={query}&entity=song&limit={top_n}", timeout=5)
            if res.status_code == 200:
                results = res.json().get('results', [])
                if results:
                    tracks = []
                    for r in results:
                        if r.get('previewUrl'): # Only return tracks with playable audio
                            tracks.append({
                                'track_id': str(r.get('trackId')),
                                'track_name': r.get('trackName', 'Unknown'),
                                'artist': r.get('artistName', 'Unknown'),
                                'genre': r.get('primaryGenreName', 'Pop'),
                                'preview_url': r.get('previewUrl'),
                                'cover_url': r.get('artworkUrl100', ''),
                                'album': r.get('collectionName', 'Single')
                            })
                    if tracks:
                        return tracks
        except Exception as e:
            pass
            
        # Fallback to local DB if API fails or returns no playable tracks
        query = query.lower()
        # fillna to avoid errors on missing text
        matches = self.tracks_df[
            self.tracks_df['track_name'].fillna('').str.lower().str.contains(query, regex=False) | 
            self.tracks_df['artist'].fillna('').str.lower().str.contains(query, regex=False) |
            self.tracks_df['genre'].fillna('').str.lower().str.contains(query, regex=False)
        ]
        return matches.head(top_n).to_dict('records')

    def get_trending(self, top_n=10):
        trending = self.tracks_df.sort_values(by='popularity', ascending=False).head(top_n)
        return trending.to_dict('records')

    def get_music_personality(self, user_id):
        if not user_id:
            user_id = "default"
        num = hash(str(user_id)) % 4
        personalities = [
            {"title": "Vintage Romantic Listener", "desc": "You enjoy acoustic romantic songs with low tempo and high valence."},
            {"title": "Classical Strings Enthusiast", "desc": "You appreciate the deep, rich textures of classical symphonies and acoustic arrangements."},
            {"title": "Energetic Groove Finder", "desc": "You love high-energy, danceable tracks that keep you moving all day."},
            {"title": "Deep Focus Achiever", "desc": "You prefer ambient, low-vocal tracks that help you concentrate and flow."}
        ]
        return personalities[num]

if __name__ == '__main__':
    engine = RecommendationEngine('../dataset/spotify_tracks.csv', '../dataset/listening_history.csv')
    recs = engine.get_hybrid_recommendations(user_id='U001', current_track_id='T0005', mood='Relaxed', top_n=5)
    print(recs['explanation'])
    for r in recs['recommendations']:
        print(r['track_name'], "-", r['genre'])
