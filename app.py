import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import ast

st.set_page_config(page_title="Movie Recommendation System", layout="wide")

# -------------------------------
# Helper functions
# -------------------------------

def convert(obj):
    """Extract names from list of dicts"""
    return [i['name'] for i in ast.literal_eval(obj)]

def convert_cast(obj):
    """Extract top 3 cast members"""
    return [i['name'] for i in ast.literal_eval(obj)[:3]]

def fetch_director(obj):
    """Extract director name"""
    for i in ast.literal_eval(obj):
        if i['job'] == 'Director':
            return i['name']
    return ""

# -------------------------------
# Load & preprocess data (cached)
# -------------------------------

@st.cache_data
def load_data():
    movies = pd.read_csv("tmdb_5000_movies.csv")
    credits = pd.read_csv("tmdb_5000_credits.csv")

    movies = movies.merge(credits, on="title")

    movies = movies[
        ["movie_id", "title", "overview", "genres", "keywords", "cast", "crew"]
    ]

    movies.dropna(inplace=True)

    movies["genres"] = movies["genres"].apply(convert)
    movies["keywords"] = movies["keywords"].apply(convert)
    movies["cast"] = movies["cast"].apply(convert_cast)
    movies["crew"] = movies["crew"].apply(fetch_director)

    movies["overview"] = movies["overview"].apply(lambda x: x.split())

    for col in ["genres", "keywords", "cast", "overview"]:
        movies[col] = movies[col].apply(lambda x: [i.replace(" ", "") for i in x])

    movies["crew"] = movies["crew"].apply(lambda x: x.replace(" ", ""))

    movies["tags"] = (
        movies["overview"]
        + movies["genres"]
        + movies["keywords"]
        + movies["cast"]
        + movies["crew"].apply(lambda x: [x])
    )

    new_df = movies[["movie_id", "title", "tags"]]
    new_df["tags"] = new_df["tags"].apply(lambda x: " ".join(x).lower())

    return new_df

@st.cache_data
def build_similarity(df):
    cv = CountVectorizer(max_features=5000, stop_words="english")
    vectors = cv.fit_transform(df["tags"]).toarray()
    similarity = cosine_similarity(vectors)
    return similarity

# -------------------------------
# Recommendation logic
# -------------------------------

def recommend(movie):
    idx = movies_df[movies_df["title"] == movie].index[0]
    distances = similarity[idx]
    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    return [movies_df.iloc[i[0]].title for i in movies_list]

# -------------------------------
# App UI
# -------------------------------

st.title("🎬 Movie Recommendation System")

with st.spinner("Loading data and building model..."):
    movies_df = load_data()
    similarity = build_similarity(movies_df)

selected_movie = st.selectbox(
    "Select a movie you like:",
    movies_df["title"].values
)

if st.button("Recommend"):
    recommendations = recommend(selected_movie)
    st.subheader("Recommended Movies:")
    for movie in recommendations:
        st.write("👉", movie)
