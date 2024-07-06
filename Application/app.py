import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import joblib

import numpy as np

from keras.models import load_model
from sentence_transformers import SentenceTransformer
from gensim.models.doc2vec import Doc2Vec



import os
print("Current working directory:", os.getcwd())
models_dir = os.path.join(os.getcwd(), 'Models')
print("Contents of Models directory:", os.listdir(models_dir))



# Define the save path for the models
save_path = 'Models'

# Load pre-trained model
model_path = os.path.join(save_path, 'deep_learning_classifier_model_complex.h5')
model = load_model(model_path)

# Load SentenceTransformer model
sentence_model_path = os.path.join(save_path, 'sentence_transformer_model')
sentence_model = SentenceTransformer(sentence_model_path)

# Load Doc2Vec model
doc2vec_model_path = os.path.join(save_path, 'doc2vec_model')
doc2vec_model = Doc2Vec.load(doc2vec_model_path)


films_df = pd.read_csv('Normalized Sheets/Films.csv')
genres_df = pd.read_csv('Normalized Sheets/Genres.csv')
directors_df = pd.read_csv('Normalized Sheets/Directors.csv')
stars_df = pd.read_csv('Normalized Sheets/Stars.csv')
film_genre_df = pd.read_csv('Normalized Sheets/FilmGenre.csv')
film_director_df = pd.read_csv('Normalized Sheets/FilmDirector.csv')
film_star_df = pd.read_csv('Normalized Sheets/FilmStar.csv')

# Function to encode sentences using the SentenceTransformer model
def Sent2Vec(sentence):
    return sentence_model.encode(sentence)

# Function to encode documents using the Doc2Vec model
def Doc2VecEncode(doc):
    return doc2vec_model.infer_vector(doc.split())


# Custom CSS
st.markdown(
    """
    <style>
    .main {
        # background-color: babyblue;
        font-family: Arial, sans-serif;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        transition-duration: 0.4s;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: white;
        color: black;
        border: 2px solid #4CAF50;
    }
    table {
        width: 100%;
        border-collapse: collapse;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 8px;
    }
    th {
        # background-color: #4CAF50;
        color: white;
        text-align: left;
    }
    tr:hover {
        background-color: blue;
    }
    </style>
    """,
    unsafe_allow_html=True
)



st.sidebar.title('Main Navigation')

main_page = st.sidebar.selectbox('Select a Page', ['Home', 'Review Rank Prediction', 'Analysis Page'])

if main_page == 'Home':
    st.title('Home')
    st.write('Welcome to the Film Database Dashboard!')

elif main_page == 'Review Rank Prediction':
    st.title('Review Rank Prediction')

    # Add text input fields
    headline = st.text_input("Write a headline for your review here:")
    user_text = st.text_area("Write your review here:")

    # Display character count
    st.markdown(f'<p class="char-counter">Required characters: 600</p>', unsafe_allow_html=True)
    st.write(f'Character count: {len(user_text)}')

    # Predict button
    if st.button("Predict"):
        if headline.strip() == "" or user_text.strip() == "":
            st.error("Please fill out both headline and review fields.")
        elif len(user_text) >= 600:
            # Preprocess the input text
            encoded_title = Sent2Vec(headline)
            encoded_review = Doc2VecEncode(user_text)
            combined_features = np.concatenate((encoded_title, encoded_review)).reshape(1, -1)

            # Predict the rating
            predicted_rating = model.predict(combined_features)
            predicted_class = np.argmax(predicted_rating, axis=1)[0]

            # Display the rating
            st.write(f"The predicted rating for your review is: {predicted_class} out of 10")
            st.success("Review submitted successfully!")
        else:
            st.write("Please enter a review text with at least 600 characters to get a prediction.")


elif main_page == 'Analysis Page':
    st.sidebar.title('Analysis Navigation')
    analysis_option = st.sidebar.selectbox('Select a view', [
        'Overview',
        'Directors', 
        'Stars', 
        'Star Film Ratings', 
        'Director Film Ratings',
        'Genres',
        'Genre Popularity Over Time',
        'Top Stars by Genre', 
        'Film Release Trends',
        'IMDb Rating Distribution'
    ])


    if analysis_option == 'Overview':
        st.header('Overview')
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Total Films", films_df.shape[0])
        col2.metric("Total Genres", genres_df.shape[0])
        col3.metric("Total Directors", directors_df.shape[0])
        col4.metric("Total Stars", stars_df.shape[0])
        
        st.subheader('Top Rated Films')

        # Custom CSS for the table
        st.markdown(
            """
            <style>
            .big-table .dataframe {
                font-size: 18px !important;
                height: auto !important;
            }
            .big-table table {
                width: 100% !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Apply CSS class to make the table larger
        top_rated_films = films_df.nlargest(10, 'IMDb Rating')
        st.markdown('<div class="big-table">', unsafe_allow_html=True)
        st.dataframe(top_rated_films[['Film Title', 'IMDb Rating', 'Release Year']])
        st.markdown('</div>', unsafe_allow_html=True)


    if analysis_option == 'Genres':
        st.header('Genres')
        
        genre_count = film_genre_df['GenreID'].value_counts().rename_axis('GenreID').reset_index(name='Count')
        genre_count = genre_count.merge(genres_df, on='GenreID')
        
        st.subheader('Number of Films per Genre')
        st.bar_chart(genre_count.set_index('Genre')['Count'])
        
        st.subheader('Genre Distribution')
        fig = px.pie(genre_count, values='Count', names='Genre', title='Genre Distribution')
        st.plotly_chart(fig)
        
        st.subheader('Genre Co-occurrence')
        
        film_genres = film_genre_df.groupby('FilmID')['GenreID'].apply(list).reset_index()

        from itertools import combinations
        genre_pairs = []
        
        for genres in film_genres['GenreID']:
            if len(genres) > 1:
                genre_pairs.extend(combinations(genres, 2))
        
        genre_pair_count = pd.DataFrame(genre_pairs, columns=['Genre1', 'Genre2'])
        
        genre_pair_count = genre_pair_count.merge(genres_df, left_on='Genre1', right_on='GenreID').drop(columns=['GenreID'])
        genre_pair_count = genre_pair_count.merge(genres_df, left_on='Genre2', right_on='GenreID').drop(columns=['GenreID'])
        genre_pair_count.columns = ['Genre1', 'Genre2', 'Genre1Name', 'Genre2Name']
        genre_pair_count = genre_pair_count.groupby(['Genre1Name', 'Genre2Name']).size().reset_index(name='Count')
        
        if not genre_pair_count.empty:
            fig = px.treemap(genre_pair_count, path=[px.Constant('all'), 'Genre1Name', 'Genre2Name'], values='Count', title='Genre Co-occurrence')
            st.plotly_chart(fig)
        else:
            st.write("No genre co-occurrence data available.")


    if analysis_option == 'Directors':
        st.header('Directors')
        
        director_count = film_director_df['DirectorID'].value_counts().rename_axis('DirectorID').reset_index(name='Count')
        director_count = director_count.merge(directors_df, on='DirectorID')
        
        st.subheader('Number of Films per Director')
        st.bar_chart(director_count.set_index('Director')['Count'])
        
        st.subheader('Films by Selected Director')
        director = st.selectbox('Select a director', directors_df['Director'])
        director_id = directors_df[directors_df['Director'] == director]['DirectorID'].values[0]
        films_by_director = film_director_df[film_director_df['DirectorID'] == director_id].merge(films_df, on='FilmID')
        st.table(films_by_director[['Film Title', 'IMDb Rating', 'Release Year']])


    if analysis_option == 'Stars':
        st.header('Stars')
        
        star_count = film_star_df['StarID'].value_counts().rename_axis('StarID').reset_index(name='Count')
        star_count = star_count.merge(stars_df, on='StarID')
        
        st.subheader('Number of Films per Star')
        st.bar_chart(star_count.set_index('Star')['Count'])
        
        st.subheader('Films by Selected Star')
        star = st.selectbox('Select a star', stars_df['Star'])
        star_id = stars_df[stars_df['Star'] == star]['StarID'].values[0]
        films_by_star = film_star_df[film_star_df['StarID'] == star_id].merge(films_df, on='FilmID')
        st.table(films_by_star[['Film Title', 'IMDb Rating', 'Release Year']])

    if analysis_option == 'Genre Popularity Over Time':
        st.header('Genre Popularity Over Time')
        film_genre_merged = film_genre_df.merge(films_df[['FilmID', 'Release Year']], on='FilmID')
        film_genre_merged = film_genre_merged.merge(genres_df, on='GenreID')
        genre_popularity = film_genre_merged.groupby(['Release Year', 'Genre']).size().reset_index(name='Count')
        fig = px.line(genre_popularity, x='Release Year', y='Count', color='Genre', title='Genre Popularity Over Time')
        st.plotly_chart(fig)
        
    if analysis_option == 'Top Stars by Genre':
        st.header('Top Stars by Genre')
        genre = st.selectbox('Select a genre', genres_df['Genre'])
        genre_id = genres_df[genres_df['Genre'] == genre]['GenreID'].values[0]
        films_in_genre = film_genre_df[film_genre_df['GenreID'] == genre_id]['FilmID'].unique()
        stars_in_genre = film_star_df[film_star_df['FilmID'].isin(films_in_genre)]
        star_count_genre = stars_in_genre['StarID'].value_counts().rename_axis('StarID').reset_index(name='Count')
        star_count_genre = star_count_genre.merge(stars_df, on='StarID')
        fig = px.bar(star_count_genre.head(10), x='Star', y='Count', title=f'Top Stars in {genre}')
        st.plotly_chart(fig)

    if analysis_option == 'Director Film Ratings':
        st.header("Director's Film Ratings")
        film_director_merged = film_director_df.merge(films_df[['FilmID', 'IMDb Rating']], on='FilmID')
        film_director_merged = film_director_merged.merge(directors_df, on='DirectorID')
        director_ratings = film_director_merged.groupby('Director').mean()['IMDb Rating'].reset_index()
        fig = px.bar(director_ratings, x='Director', y='IMDb Rating', title="Average IMDb Rating per Director")
        st.plotly_chart(fig)


    if analysis_option == 'Star Film Ratings':
        st.header("Star's Film Ratings")
        film_star_merged = film_star_df.merge(films_df[['FilmID', 'IMDb Rating']], on='FilmID')
        film_star_merged = film_star_merged.merge(stars_df, on='StarID')
        star_ratings = film_star_merged.groupby('Star').mean()['IMDb Rating'].reset_index()
        fig = px.bar(star_ratings, x='Star', y='IMDb Rating', title="Average IMDb Rating per Star")
        st.plotly_chart(fig)


    if analysis_option == 'Film Release Trends':
        st.header('Film Release Trends')
        
        films_df['Release Year'] = pd.to_numeric(films_df['Release Year'], errors='coerce')
        films_df = films_df.dropna(subset=['Release Year'])
        films_df['Release Year'] = films_df['Release Year'].astype(int)
        
        release_trends = films_df['Release Year'].value_counts().reset_index()
        release_trends.columns = ['Release Year', 'Count']  # Correctly rename columns
        release_trends = release_trends.sort_values('Release Year')
        
        # Ensure column names are correctly set
        # st.write(release_trends)  # Print the DataFrame to inspect its structure
        fig = px.line(release_trends, x='Release Year', y='Count', title='Film Release Trends Over Years')
        st.plotly_chart(fig)


    if analysis_option == 'IMDb Rating Distribution':
        st.header('IMDb Rating Distribution')
        fig = px.histogram(films_df, x='IMDb Rating', nbins=20, title='Distribution of IMDb Ratings')
        st.plotly_chart(fig)