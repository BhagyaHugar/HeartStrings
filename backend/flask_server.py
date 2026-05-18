from flask import Flask, request, jsonify
import mysql.connector
import os
import sys

# Add parent directory to path to import model
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from model.recommendation_engine import RecommendationEngine
except ImportError:
    from HeartStrings.model.recommendation_engine import RecommendationEngine

app = Flask(__name__)

# Initialize Recommendation Engine
engine = RecommendationEngine(
    tracks_path='dataset/spotify_tracks.csv', 
    history_path='dataset/listening_history.csv'
)

# MySQL DB Config
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '', # User can change this or set ENV var
    'database': 'music_db'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password') # In prod, hash this
    preferred_mood = data.get('preferred_mood', None)
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        # Check if user exists
        cursor.execute("SELECT * FROM Users WHERE username=%s", (username,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
        
        # Insert new user
        cursor.execute("INSERT INTO Users (username, password_hash, preferred_mood) VALUES (%s, %s, %s)", 
                       (username, password, preferred_mood))
        conn.commit()
        
        # Get the inserted user ID
        cursor.execute("SELECT id FROM Users WHERE username=%s", (username,))
        user = cursor.fetchone()
        conn.close()
        
        return jsonify({'success': True, 'user_id': f"U{user['id']:03d}", 'username': username})
        
    return jsonify({'success': False, 'message': 'Database not connected'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password') # In prod, verify hash
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users WHERE username=%s AND password_hash=%s", (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            # Map DB user_id to mock dataset user ID for demo purposes
            return jsonify({'success': True, 'user_id': f"U{user['id']:03d}", 'username': user['username']})
    
    # Fallback to mock login for demo if DB is not setup
    return jsonify({'success': True, 'user_id': 'U001', 'username': username, 'warning': 'DB not connected, using mock data'})

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    data = request.json
    user_id = data.get('user_id')
    current_track_id = data.get('current_track_id')
    current_track_genre = data.get('current_track_genre')
    mood = data.get('mood')
    top_n = data.get('top_n', 10)
    
    recs = engine.get_hybrid_recommendations(user_id=user_id, current_track_id=current_track_id, current_track_genre=current_track_genre, mood=mood, top_n=top_n)
    return jsonify(recs)

@app.route('/api/interaction', methods=['POST'])
def log_interaction():
    data = request.json
    user_id = data.get('user_id')
    track_id = data.get('track_id')
    rating = data.get('rating')
    liked = data.get('liked')
    
    # Log to DB if connected
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        # Convert 'U001' to integer 1
        u_id = int(user_id.replace('U', '')) if isinstance(user_id, str) and user_id.startswith('U') else 1
        cursor.execute("INSERT INTO ListeningHistory (user_id, track_id, rating, liked) VALUES (%s, %s, %s, %s)", 
                       (u_id, track_id, rating, liked))
        conn.commit()
        conn.close()
        
    return jsonify({'success': True})

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    results = engine.search_tracks(query)
    return jsonify(results)

@app.route('/api/trending', methods=['GET'])
def trending():
    results = engine.get_trending()
    return jsonify(results)

@app.route('/api/personality', methods=['GET'])
def personality():
    user_id = request.args.get('user_id', '')
    result = engine.get_music_personality(user_id)
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
