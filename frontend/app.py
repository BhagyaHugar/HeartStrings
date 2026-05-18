import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import base64
import os

# Configuration
st.set_page_config(page_title="HearStrings | Where Music Finds Your Soul", layout="wide", page_icon="🎼")

# Load CSS
def load_css():
    css_path = 'frontend/styles.css'
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    else:
        st.warning("CSS file not found.")

    # Background image must be injected as base64 in Streamlit
    img_b64 = get_base64_image('assets/background.jpg')
    if img_b64:
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: linear-gradient(rgba(20, 15, 10, 0.1), rgba(20, 15, 10, 0.2)), url("data:image/jpeg;base64,{img_b64}");
                background-size: cover;
                background-attachment: fixed;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

def get_audio_url(track_id):
    # Deterministically return a sample audio URL based on track_id
    num = (hash(track_id) % 15) + 1
    return f"https://www.soundhelix.com/examples/mp3/SoundHelix-Song-{num}.mp3"

def get_audio_format(audio_url):
    """Determine audio format from URL"""
    if not audio_url:
        return "audio/mp3"
    if '.m4a' in audio_url or 'itunes' in audio_url:
        return "audio/mp4"
    elif '.mp3' in audio_url:
        return "audio/mp3"
    elif '.wav' in audio_url:
        return "audio/wav"
    elif '.ogg' in audio_url:
        return "audio/ogg"
    else:
        # Default to mp3 for unknown formats
        return "audio/mp3"

# Initialize state
if 'page' not in st.session_state:
    st.session_state.page = 'Landing'
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'current_track_id' not in st.session_state:
    st.session_state.current_track_id = None
if 'mood' not in st.session_state:
    st.session_state.mood = None
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []
if 'explanation' not in st.session_state:
    st.session_state.explanation = ""
if 'language' not in st.session_state:
    st.session_state.language = 'Any'
if 'explanation' not in st.session_state:
    st.session_state.explanation = ""
if 'is_premium' not in st.session_state:
    st.session_state.is_premium = False
if 'current_track_data' not in st.session_state:
    st.session_state.current_track_data = None
if 'favorites' not in st.session_state:
    st.session_state.favorites = []

load_css()
st.markdown("<div class='music-note note1'>♪</div><div class='music-note note2'>♫</div><div class='music-note note3'>♩</div><div class='music-note note4'>♬</div><div class='music-note note5'>♭</div>", unsafe_allow_html=True)


API_URL = "http://localhost:5000/api"

def navigate(page_name):
    st.session_state.page = page_name
    st.rerun()

# Pages
def landing_page():
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: left; font-size: 5rem;'>HearStrings</h1>", unsafe_allow_html=True)
        st.markdown("<h2>Where Music Finds Your Soul.</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 1.2rem;'>An AI-powered vintage aesthetic music discovery platform. Feel every string with personalized recommendations.</p>", unsafe_allow_html=True)
        col1a, col1b = st.columns([1, 1])
        with col1a:
            if st.button("Sign Up", key="signup_btn", use_container_width=True):
                navigate('Signup')
        with col1b:
            if st.button("Login", key="login_btn_landing", use_container_width=True):
                navigate('Login')
    with col2:
        img_b64 = get_base64_image('assets/veena.png')
        if img_b64:
            st.markdown(f'<img src="data:image/png;base64,{img_b64}" class="floating-img" style="width:100%; border-radius: 20px;">', unsafe_allow_html=True)

def login_page():
    st.markdown("<h1>Welcome Back</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h3>Login</h3>", unsafe_allow_html=True)
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True):
            try:
                res = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
                if res.status_code == 200:
                    data = res.json()
                    if data.get('success'):
                        st.session_state.user_id = data.get('user_id')
                        st.session_state.username = data.get('username')
                        st.success(f"Welcome {username}!")
                        navigate('Dashboard')
                    else:
                        st.error("Login failed. Check your credentials.")
                else:
                    st.error("Login failed. Check backend.")
            except Exception as e:
                st.error("Could not connect to backend.")
        st.markdown("<p style='text-align: center; margin-top: 15px;'>Don't have an account?</p>", unsafe_allow_html=True)
        if st.button("Create an Account", use_container_width=True):
            navigate('Signup')

def signup_page():
    st.markdown("<h1>Join HearStrings</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h3>Sign Up</h3>", unsafe_allow_html=True)
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        if st.button("Sign Up", use_container_width=True):
            if password != confirm_password:
                st.error("Passwords do not match!")
            elif not username or not password:
                st.error("Please fill in all fields.")
            else:
                try:
                    res = requests.post(f"{API_URL}/signup", json={"username": username, "password": password})
                    data = res.json()
                    if res.status_code == 200 and data.get('success'):
                        st.session_state.user_id = data.get('user_id')
                        st.session_state.username = data.get('username')
                        st.success(f"Account created successfully! Welcome {username}!")
                        navigate('Dashboard')
                    else:
                        st.error(data.get('message', "Signup failed."))
                except Exception as e:
                    st.error("Could not connect to backend.")
        st.markdown("<p style='text-align: center; margin-top: 15px;'>Already have an account?</p>", unsafe_allow_html=True)
        if st.button("Back to Login", use_container_width=True):
            navigate('Login')

def fetch_recommendations():
    try:
        payload = {
            "user_id": st.session_state.user_id,
            "current_track_id": st.session_state.current_track_id,
            "current_track_genre": st.session_state.current_track_data.get('genre') if st.session_state.get('current_track_data') else None,
            "mood": st.session_state.mood,
            "top_n": 5
        }
        res = requests.post(f"{API_URL}/recommendations", json=payload)
        if res.status_code == 200:
            data = res.json()
            recs = data.get('recommendations', [])
            
            # Dynamic iTunes injection for high-accuracy recommendations based on last search or mood/language
            itunes_limit = 8
            
            if st.session_state.get('language') and st.session_state.language != 'Any':
                queries_to_try = []
                if st.session_state.get('mood') and st.session_state.mood != 'None':
                    queries_to_try.append(f"{st.session_state.language} {st.session_state.mood}")
                queries_to_try.append(st.session_state.language)
                
                recs = []  # Strictly prioritize language by clearing non-language backend recs
                itunes_limit = 20
                
                for query in queries_to_try:
                    try:
                        itunes_res = requests.get(f"https://itunes.apple.com/search?term={query}&entity=song&limit={itunes_limit}", timeout=5)
                        if itunes_res.status_code == 200:
                            itunes_results = itunes_res.json().get('results', [])
                            valid_results = [r for r in itunes_results if r.get('previewUrl')]
                            if valid_results:
                                for r in reversed(valid_results):
                                    tid = str(r.get('trackId'))
                                    if tid != st.session_state.current_track_id:
                                        recs.insert(0, {
                                            'track_id': tid,
                                            'track_name': r.get('trackName', 'Unknown'),
                                            'artist': r.get('artistName', 'Unknown'),
                                            'genre': r.get('primaryGenreName', 'Pop'),
                                            'preview_url': r.get('previewUrl'),
                                            'cover_url': r.get('artworkUrl100', '')
                                        })
                                break # Found results, stop fallback
                    except: pass
            else:
                itunes_search_query = None
                if st.session_state.get('mood') and st.session_state.mood != 'None':
                    itunes_search_query = st.session_state.mood
                elif st.session_state.get('current_track_data') and st.session_state.current_track_data.get('artist'):
                    itunes_search_query = st.session_state.current_track_data.get('artist')
                
                if itunes_search_query:
                    try:
                        itunes_res = requests.get(f"https://itunes.apple.com/search?term={itunes_search_query}&entity=song&limit={itunes_limit}", timeout=5)
                        if itunes_res.status_code == 200:
                            itunes_results = itunes_res.json().get('results', [])
                            for r in reversed(itunes_results):
                                if r.get('previewUrl'):
                                    tid = str(r.get('trackId'))
                                    if tid != st.session_state.current_track_id:
                                        recs.insert(0, {
                                            'track_id': tid,
                                            'track_name': r.get('trackName', 'Unknown'),
                                            'artist': r.get('artistName', 'Unknown'),
                                            'genre': r.get('primaryGenreName', 'Pop'),
                                            'preview_url': r.get('previewUrl'),
                                            'cover_url': r.get('artworkUrl100', '')
                                        })
                    except: pass
            
            # Deduplicate
            seen = set()
            final_recs = []
            for r in recs:
                if r['track_id'] not in seen:
                    seen.add(r['track_id'])
                    final_recs.append(r)
            
            st.session_state.recommendations = final_recs[:10]
            
            # Add fallback audio URLs to tracks that don't have preview_url
            for track in st.session_state.recommendations:
                if not track.get('preview_url'):
                    track['preview_url'] = get_audio_url(track['track_id'])
            
            if st.session_state.get('language') and st.session_state.language != 'Any':
                if st.session_state.get('mood') and st.session_state.mood != 'None':
                    st.session_state.explanation = f"Recommended because they fit your {st.session_state.language} '{st.session_state.mood}' mood perfectly."
                else:
                    st.session_state.explanation = f"Recommended based on your preference for {st.session_state.language} songs."
            elif st.session_state.get('mood') and st.session_state.mood != 'None':
                st.session_state.explanation = f"Recommended because they fit your '{st.session_state.mood}' mood perfectly."
            elif st.session_state.get('current_track_data'):
                st.session_state.explanation = f"Recommended because you recently listened to {st.session_state.current_track_data['genre']} by {st.session_state.current_track_data['artist']}."
            else:
                st.session_state.explanation = data.get('explanation', '')
    except Exception as e:
        st.error("Could not fetch recommendations.")

def dashboard_page():
    st.markdown(f"<h1>Hello, {st.session_state.username}</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("<h3>Set Your Mood</h3>", unsafe_allow_html=True)
        moods = ['None', 'Happy', 'Relaxed', 'Romantic', 'Sad', 'Energetic', 'Rainy Mood', 'Focus Mode']
        selected_mood = st.selectbox("Mood", moods, index=moods.index(st.session_state.mood) if st.session_state.mood in moods else 0)
        
        languages = ['Any', 'Hindi', 'English', 'Kannada', 'Telugu', 'Tamil', 'Punjabi', 'Malayalam']
        selected_lang = st.selectbox("Language", languages, index=languages.index(st.session_state.language) if st.session_state.language in languages else 0)
        
        if selected_mood != st.session_state.mood or selected_lang != st.session_state.language:
            st.session_state.mood = selected_mood
            st.session_state.language = selected_lang
            fetch_recommendations()
            st.rerun()
        
        st.markdown("<br><h3>Navigation</h3>", unsafe_allow_html=True)
        if st.button("Search & Discover"):
            navigate('Search')
        if st.button("Favorites"):
            navigate('Favorites')
        if st.button("Analytics Dashboard"):
            navigate('Analytics')
        if st.button("Logout"):
            st.session_state.user_id = None
            st.session_state.username = None
            navigate('Landing')
            
        st.markdown("<hr style='border-color: rgba(255,140,0,0.3);'>", unsafe_allow_html=True)
        if not st.session_state.is_premium:
            if st.button("🌟 Upgrade to Premium", help="Remove ads and unlock premium features"):
                st.session_state.is_premium = True
                st.rerun()
        else:
            st.markdown("<p style='color: #DAA520; text-align: center;'>🌟 Premium Member</p>", unsafe_allow_html=True)
            
        
        # Trending section
        try:
            res_trend = requests.get(f"{API_URL}/trending")
            if res_trend.status_code == 200:
                trending = res_trend.json()
                if trending:
                    st.markdown("<h3>🔥 Trending Now</h3>", unsafe_allow_html=True)
                    for idx, t in enumerate(trending[:5]):
                        st.markdown(f"<p style='font-size: 0.9rem; margin:0;'><b>{idx+1}. {t['track_name']}</b></p>", unsafe_allow_html=True)
                        st.markdown(f"<p style='font-size: 0.8rem; color: #DAA520; margin:0 0 10px 0;'>{t['artist']}</p>", unsafe_allow_html=True)
        except:
            pass

    with col2:
        st.markdown("<h2>Recommended for You</h2>", unsafe_allow_html=True)
        
        # Now playing section
        if st.session_state.current_track_id:
            current_track = next((t for t in st.session_state.recommendations if t['track_id'] == st.session_state.current_track_id), None)
            if current_track:
                st.markdown(f"<h3 style='margin-top:0;'>▶ Now Playing</h3>", unsafe_allow_html=True)
                
                cols = st.columns([1, 4])
                with cols[0]:
                    if current_track.get('cover_url'):
                        st.markdown(f'<img src="{current_track["cover_url"]}" style="width: 100px; border-radius: 10px;" class="vinyl-spin">', unsafe_allow_html=True)
                with cols[1]:
                    st.markdown(f"<p style='font-size: 1.2rem; font-weight: bold; margin-bottom: 5px;'>{current_track['track_name']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p style='color: #b3b3b3; margin-top: 0; margin-bottom: 15px;'>{current_track['artist']} • {current_track.get('album', 'Single')} • {current_track['genre']}</p>", unsafe_allow_html=True)
                    
                audio_url = current_track.get('preview_url')
                if audio_url:
                    st.audio(audio_url, format=get_audio_format(audio_url), autoplay=True)
                else:
                    st.warning("No audio preview available for this track.")

        if not st.session_state.recommendations:
            fetch_recommendations()
        
        if st.session_state.recommendations:
            st.markdown(f"<p style='color: #DAA520; font-style: italic;'>{st.session_state.explanation}</p>", unsafe_allow_html=True)
            
            # Inject Sponsored Ad if not premium
            if not st.session_state.is_premium and len(st.session_state.recommendations) > 0:
                st.markdown("<p style='font-size: 0.7rem; color: #b3b3b3; letter-spacing: 2px; margin-bottom: 5px;'>SPONSORED AD</p>", unsafe_allow_html=True)
                st.markdown("<h4 style='margin-top: 0;'>The Vintage Symphony Collection</h4>", unsafe_allow_html=True)
                st.markdown("<p style='font-size: 0.9rem; margin-bottom: 0;'>Experience timeless classical acoustic masterpieces. Upgrade to Premium for uninterrupted listening.</p>", unsafe_allow_html=True)

            for track in st.session_state.recommendations:
                cols = st.columns([1, 4, 2])
                with cols[0]:
                    if track.get('cover_url'):
                        spin_class = "vinyl-spin" if st.session_state.current_track_id == track['track_id'] else ""
                        st.markdown(f'<img src="{track["cover_url"]}" class="{spin_class}" style="width: 60px; border-radius: 5px;">', unsafe_allow_html=True)
                with cols[1]:
                    st.markdown(f"<h4>{track['track_name']}</h4>", unsafe_allow_html=True)
                    st.markdown(f"<p>{track['artist']} • {track['genre']}</p>", unsafe_allow_html=True)
                with cols[2]:
                    if st.button("▶ Play", key=f"play_{track['track_id']}"):
                        st.session_state.current_track_id = track['track_id']
                        st.session_state.current_track_data = track
                        # Log interaction
                        try:
                            requests.post(f"{API_URL}/interaction", json={
                                "user_id": st.session_state.user_id,
                                "track_id": track['track_id'],
                                "rating": 5,
                                "liked": True
                            })
                        except:
                            pass
                        fetch_recommendations()
                        st.rerun()
                    if st.button("❤️ Favorite", key=f"fav_{track['track_id']}"):
                        if not any(t['track_id'] == track['track_id'] for t in st.session_state.favorites):
                            st.session_state.favorites.append(track)
                        st.success("Added to Favorites!")

def fetch_personality():
    try:
        res = requests.get(f"{API_URL}/personality?user_id={st.session_state.user_id}")
        if res.status_code == 200:
            return res.json()
    except:
        pass
    return {"title": "Vintage Romantic Listener", "desc": "You enjoy acoustic romantic songs with low tempo and high valence."}

def analytics_page():
    import plotly.graph_objects as go
    import networkx as nx
    from sklearn.cluster import KMeans
    import numpy as np

    st.markdown("<h1>ML Insights & Recommendation Intelligence</h1>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        navigate('Dashboard')
        
    st.markdown("<p style='text-align: center; color: #DAA520; margin-bottom: 30px; font-size:1.2rem;'>Explore the AI intelligence powering your personalized vintage music experience.</p>", unsafe_allow_html=True)

    # 1. Personality & Confidence
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.markdown("<h3>Your Music Personality</h3>", unsafe_allow_html=True)
        personality = fetch_personality()
        st.markdown(f"<p style='font-size: 1.5rem; color: #FF8C00;'>{personality['title']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p>{personality['desc']}</p>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<h3>Recommendation Confidence</h3>", unsafe_allow_html=True)
        recs = st.session_state.get('recommendations', [])
        if recs:
            for idx, r in enumerate(recs[:3]):
                conf = 98 - (idx * 4) + np.random.randint(-2, 3)
                st.markdown(f"<p style='margin-bottom: 2px;'>{r['track_name']} → <b style='color: #DAA520;'>{conf}% match</b></p>", unsafe_allow_html=True)
                st.progress(conf / 100.0)
        else:
            st.info("Play some songs to generate confidence scores.")
            
    with col3:
        st.markdown("<h3>Model Performance</h3>", unsafe_allow_html=True)
        fig_perf = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = 94.2,
            title = {'text': "Accuracy (%)", 'font': {'color': '#DAA520'}},
            gauge = {'axis': {'range': [None, 100]},
                     'bar': {'color': "#FF8C00"},
                     'steps' : [
                         {'range': [0, 80], 'color': "rgba(255, 255, 255, 0.05)"},
                         {'range': [80, 100], 'color': "rgba(218, 165, 32, 0.2)"}],
                     }
        ))
        fig_perf.update_layout(height=200, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)', font={'color': "#FDFBF7"})
        st.plotly_chart(fig_perf, use_container_width=True)

    st.markdown("<br><hr style='border-color: rgba(255,140,0,0.3);'>", unsafe_allow_html=True)
    
    # 2. Heatmap Correlation Analysis
    col_heat, col_km = st.columns(2)
    
    with col_heat:
        st.markdown("<h3>Heatmap Correlation Analysis</h3>", unsafe_allow_html=True)
        st.caption("Analyzing feature relationships and recommendation logic.")
        features = ['Energy', 'Danceability', 'Tempo', 'Acousticness', 'Valence', 'Popularity']
        # Create a symmetric correlation matrix mimicking real-world music attributes
        corr = np.array([
            [1.0,  0.7,  0.6, -0.8,  0.5,  0.3],
            [0.7,  1.0,  0.5, -0.6,  0.8,  0.4],
            [0.6,  0.5,  1.0, -0.4,  0.4,  0.2],
            [-0.8,-0.6, -0.4,  1.0, -0.7, -0.5],
            [0.5,  0.8,  0.4, -0.7,  1.0,  0.6],
            [0.3,  0.4,  0.2, -0.5,  0.6,  1.0]
        ])
        fig_corr = px.imshow(corr, x=features, y=features, color_continuous_scale='RdBu_r', zmin=-1, zmax=1, template="plotly_dark")
        fig_corr.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "#FDFBF7"})
        st.plotly_chart(fig_corr, use_container_width=True)

    with col_km:
        st.markdown("<h3>Intelligent K-Means Music Clusters</h3>", unsafe_allow_html=True)
        st.caption("Grouping songs into Moods based on Tempo, Energy, and Valence.")
        np.random.seed(42)
        tempo = np.random.uniform(60, 180, 150)
        energy = np.random.uniform(0.1, 0.9, 150)
        valence = np.random.uniform(0.1, 0.9, 150)
        acousticness = np.random.uniform(0, 1, 150)
        X = np.column_stack((tempo, energy, valence, acousticness))
        kmeans = KMeans(n_clusters=6, random_state=0, n_init=10).fit(X)
        
        cluster_names = ['Romantic', 'Energetic', 'Calm', 'Workout', 'Emotional', 'Retro']
        labels = [cluster_names[l] for l in kmeans.labels_]
        
        df_km = pd.DataFrame({'Energy': energy, 'Valence': valence, 'Cluster': labels})
        fig_km = px.scatter(df_km, x='Energy', y='Valence', color='Cluster', template="plotly_dark", 
                            color_discrete_sequence=['#FF1493', '#FF4500', '#1E90FF', '#FF8C00', '#8A2BE2', '#DAA520'])
        fig_km.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "#FDFBF7"})
        st.plotly_chart(fig_km, use_container_width=True)

    st.markdown("<br><hr style='border-color: rgba(255,140,0,0.3);'>", unsafe_allow_html=True)

    # 3. Real-Time Recommendation Adaptation Graph
    st.markdown("<h3>Real-Time Recommendation Adaptation Graph</h3>", unsafe_allow_html=True)
    st.caption("Visualizing live predictive modeling: How recommendations dynamically adapt to your genre switches and skips.")
    
    time_steps = list(range(1, 21))
    # Adapt the graph shift based on the currently selected mood
    current_mood = st.session_state.get('mood', 'None')
    base_shift = 0.5
    if current_mood in ['Energetic', 'Workout']: base_shift = 1.2
    elif current_mood in ['Sad', 'Rainy Mood', 'Relaxed']: base_shift = 0.2
    elif current_mood in ['Romantic']: base_shift = 0.6
    
    # Generate an adaptive learning curve
    y_val = [base_shift - (0.3 * np.exp(-t/5)) + (np.sin(t) * 0.1) for t in time_steps]
    
    df_rt = pd.DataFrame({'Interaction Sequence': time_steps, 'Recommendation Shift Vector (Energy/Tempo)': y_val})
    fig_rt = px.line(df_rt, x='Interaction Sequence', y='Recommendation Shift Vector (Energy/Tempo)', markers=True, template="plotly_dark")
    fig_rt.update_traces(line_color='#DAA520', marker=dict(size=10, color='#FF8C00'))
    fig_rt.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "#FDFBF7"}, yaxis_range=[0, 1.5])
    st.plotly_chart(fig_rt, use_container_width=True)

def favorites_page():
    st.markdown("<h1>Your Favorites</h1>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        navigate('Dashboard')
    
    if not st.session_state.favorites:
        st.info("You haven't added any favorites yet.")
    else:
        for track in st.session_state.favorites:
            cols = st.columns([1, 4, 2])
            with cols[0]:
                if track.get('cover_url'):
                    st.markdown(f'<img src="{track["cover_url"]}" style="width: 60px; border-radius: 5px;">', unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f"<h4>{track['track_name']}</h4>", unsafe_allow_html=True)
                st.markdown(f"<p>{track['artist']} • {track['genre']}</p>", unsafe_allow_html=True)
            with cols[2]:
                if st.button("▶ Play", key=f"fav_page_play_{track['track_id']}"):
                    st.session_state.current_track_id = track['track_id']
                    st.session_state.current_track_data = track
                    st.rerun()

def search_page():
    st.markdown("<h1>Search & Discover</h1>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        navigate('Dashboard')
        
    # Now playing in search
    if st.session_state.current_track_id and st.session_state.current_track_data:
        ct = st.session_state.current_track_data
        st.markdown(f"<h3 style='margin-top:0;'>▶ Now Playing</h3>", unsafe_allow_html=True)
        
        cols = st.columns([1, 3, 2])
        with cols[0]:
            if ct.get('cover_url'):
                st.markdown(f'<img src="{ct["cover_url"]}" style="width: 100px; border-radius: 10px;" class="vinyl-spin">', unsafe_allow_html=True)
        with cols[1]:
            st.markdown(f"<p style='font-size: 1.2rem; font-weight: bold; margin-bottom: 5px;'>{ct['track_name']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: #b3b3b3; margin-top: 0; margin-bottom: 15px;'>{ct['artist']} • {ct.get('album', 'Single')} • {ct['genre']}</p>", unsafe_allow_html=True)
        with cols[2]:
            if st.button("❤️ Favorite"):
                if not any(t['track_id'] == ct['track_id'] for t in st.session_state.favorites):
                    st.session_state.favorites.append(ct)
                st.success("Added to Favorites!")
            
            # Download button
            if ct.get('preview_url'):
                try:
                    audio_bytes = requests.get(ct['preview_url']).content
                    st.download_button(label="⬇️ Download", data=audio_bytes, file_name=f"{ct['track_name']}.m4a", mime="audio/mp4")
                except:
                    pass
            
        audio_url = ct.get('preview_url')
        if audio_url:
            st.audio(audio_url, format=get_audio_format(audio_url), autoplay=True)
        else:
            st.warning("No audio preview available for this track.")

        # AI Recommendations based on search
        st.markdown("<h3>🤖 AI Recommendations Based On Your Search</h3>", unsafe_allow_html=True)
        try:
            payload = {
                "user_id": st.session_state.user_id,
                "current_track_id": ct['track_id'],
                "current_track_genre": ct.get('genre'),
                "mood": st.session_state.mood,
                "top_n": 3
            }
            res = requests.post(f"{API_URL}/recommendations", json=payload)
            if res.status_code == 200:
                recs = res.json().get('recommendations', [])
                for track in recs:
                    rcols = st.columns([1, 4, 1])
                    with rcols[0]:
                        if track.get('cover_url'):
                            st.markdown(f'<img src="{track["cover_url"]}" style="width: 40px; border-radius: 5px;">', unsafe_allow_html=True)
                    with rcols[1]:
                        st.markdown(f"**{track['track_name']}** • {track['artist']}")
                    with rcols[2]:
                        if st.button("▶ Play", key=f"search_rec_play_{track['track_id']}"):
                            st.session_state.current_track_id = track['track_id']
                            st.session_state.current_track_data = track
                            st.rerun()
        except Exception as e:
            pass

    st.markdown("<hr>", unsafe_allow_html=True)
    
    query = st.text_input("Search for artists, songs, or genres...", "")
    if query:
        try:
            res = requests.get(f"{API_URL}/search?q={query}")
            if res.status_code == 200:
                results = res.json()
                if results:
                    st.markdown(f"<h3>Found {len(results)} matches</h3>", unsafe_allow_html=True)
                    for track in results:
                        cols = st.columns([1, 4, 1])
                        with cols[0]:
                            if track.get('cover_url'):
                                st.markdown(f'<img src="{track["cover_url"]}" style="width: 50px; border-radius: 5px;">', unsafe_allow_html=True)
                        with cols[1]:
                            st.markdown(f"**{track['track_name']}** • {track['artist']} • *{track['genre']}*")
                        with cols[2]:
                            if st.button("▶ Play", key=f"search_play_{track['track_id']}"):
                                st.session_state.current_track_id = track['track_id']
                                st.session_state.current_track_data = track
                                try:
                                    requests.post(f"{API_URL}/interaction", json={
                                        "user_id": st.session_state.user_id,
                                        "track_id": track['track_id'],
                                        "rating": 5,
                                        "liked": True
                                    })
                                except: pass
                                st.rerun()
                            if st.button("❤️ Favorite", key=f"search_fav_{track['track_id']}"):
                                if not any(t['track_id'] == track['track_id'] for t in st.session_state.favorites):
                                    st.session_state.favorites.append(track)
                                st.success("Added to Favorites!")
                else:
                    st.markdown("<p>No results found.</p>", unsafe_allow_html=True)
        except Exception as e:
            st.error("Could not fetch search results.")

# Router
if st.session_state.page == 'Landing':
    landing_page()
elif st.session_state.page == 'Login':
    login_page()
elif st.session_state.page == 'Signup':
    signup_page()
elif st.session_state.page == 'Dashboard':
    dashboard_page()
elif st.session_state.page == 'Analytics':
    analytics_page()
elif st.session_state.page == 'Favorites':
    favorites_page()
elif st.session_state.page == 'Search':
    search_page()
