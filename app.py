import pickle
from http.client import responses
import streamlit as st
import requests

def fetch_poster(movie_id):
    response = requests.get(
        f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=749627bb5d47066b0de73d8f24ef6212')
    data = response.json()
    return "http://image.tmdb.org/t/p/w500/" + data['poster_path']

def recommend(movie):
    movie_index = movies_df[movies_df['title'] == movie].index[0]
    distances = similarity[movie_index]
    recommended_indices = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in recommended_indices:
        movie_id = movies_df.iloc[i[0]].movie_id
        recommended_movies.append(movies_df.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movies_posters

# Load data
movies_df = pickle.load(open('movies.pkl', 'rb'))
movies_list = movies_df['title'].values

# Add placeholder to the dropdown list
movies_with_placeholder = ['Select a movie...'] + list(movies_list)

similarity = pickle.load(open('similarity.pkl', 'rb'))

st.title('Movie Recommendation System')

# Dropdown with placeholder
selected_movie_name = st.selectbox("Choose a movie", movies_with_placeholder)

if st.button("Recommend") and selected_movie_name != "Select a movie...":
    names, posters = recommend(selected_movie_name)
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.text(names[0])
        st.image(posters[0])

    with col2:
        st.text(names[1])
        st.image(posters[1])

    with col3:
        st.text(names[2])
        st.image(posters[2])

    with col4:
        st.text(names[3])
        st.image(posters[3])

    with col5:
        st.text(names[4])
        st.image(posters[4])


