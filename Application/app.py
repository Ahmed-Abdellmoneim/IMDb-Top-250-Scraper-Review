import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import joblib

# Load the data
stars_df = pd.read_csv("../Normalized Sheets/Stars.csv")
films_df = pd.read_csv("../Normalized Sheets/Films.csv")
genres_df = pd.read_csv("../Normalized Sheets/Genres.csv")
film_star_df = pd.read_csv("../Normalized Sheets/FilmStar.csv")
directors_df = pd.read_csv("../Normalized Sheets/Directors.csv")
film_genre_df = pd.read_csv("../Normalized Sheets/FilmGenre.csv")
film_director_df = pd.read_csv("../Normalized Sheets/FilmDirector.csv")

# Custom CSS
st.markdown(
    """
    <style>
    .main {
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
        color: white;
        text-align: left;
    }
    tr:hover {
        background-color: #f1f1f1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.title("Main Navigation")

main_page = st.sidebar.selectbox(
    "Select a Page", ["Home", "Review Rank Prediction", "IMDb Analysis"]
)

if main_page == "Home":
    st.title("IMDb Top 250 Movie")
    st.subheader("Discover, Analyze, and Predict Movie's Review Ratings")
    st.write(
        """
        This dashboard allows you to explore various aspects of the IMDb top 250 movies. 
        Whether you're a movie enthusiast, data analyst, or someone looking to delve into the intricacies of film data, 
        this tool offers something for everyone. 

        ### Features:

        - **Review Rank Prediction**: Predict the ranking of your review based on your input. 
        Curious how your review might fare among other IMDb users? Use our prediction model to find out!
        
        - **IMDb Analysis**: Dive deep into the IMDb top 250 movies with various analyses on genres, 
        directors, stars, and more. Understand trends, uncover patterns, and gain insights into the world of cinema.

        ### Instructions:

        - Navigate through the sidebar to access different sections.
        - Use the Review Rank Prediction to use our AI model which can be used to predict the rank of any review.
        - Explore the IMDb Analysis page for detailed insights and visualizations of the information about IMDb's top 250 movies.

        We hope you find this dashboard both informative and engaging. Happy exploring!
        """
    )

elif main_page == "Review Rank Prediction":
    st.title("Predict The Review Rate")
    st.subheader("Use AI Model to predict the rank of any given review")
    # Add text input fields
    headline = st.text_input("Write a headline for your review here:")
    user_text = st.text_area("Write your review here:")

    # Display character count
    st.markdown(
        f'<p class="char-counter">Required characters: 600</p>', unsafe_allow_html=True
    )
    st.write(f"Character count: {len(user_text)}")

    # Predict button
    if st.button("Predict"):
        if headline.strip() == "" or user_text.strip() == "":
            st.error("Please fill out both headline and review fields.")
        elif len(user_text) >= 600:
            # Preprocess the input text
            full_text = f"{headline} {user_text}"
            # sequences = tokenizer.texts_to_sequences([full_text])
            # padded_sequences = pad_sequences(sequences, maxlen=100)  # Ensure the maxlen is the same as during training

            # Predict the rating
            # predicted_rating = model.predict(padded_sequences)[0][0]

            # Display the rating
            st.write(f"The predicted rating for your review is: {0:.2f} out of 10")
            st.success("Review submitted successfully!")
        else:
            st.write(
                "Please enter a review text with at least 600 characters to get a prediction."
            )

elif main_page == "IMDb Analysis":
    st.sidebar.title("Analysis Navigation")
    analysis_option = st.sidebar.selectbox(
        "Select a view",
        [
            "Overview",
            "Directors",
            "Stars",
            "Star Film Ratings",
            "Director Film Ratings",
            "Genres",
            "Genre Popularity Over Time",
            "Top Stars by Genre",
            "Film Release Trends",
            "IMDb Rating Distribution",
        ],
    )

    if analysis_option == "Overview":
        st.header("Overview of IMDb Top 250 Movies")
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Films", films_df.shape[0])
        col2.metric("Total Genres", genres_df.shape[0])
        col3.metric("Total Directors", directors_df.shape[0])
        col4.metric("Total Stars", stars_df.shape[0])

        st.subheader("Top Rated Films")

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
            unsafe_allow_html=True,
        )

        # Apply CSS class to make the table larger
        top_rated_films = films_df.nlargest(10, "IMDb Rating")
        st.markdown('<div class="big-table">', unsafe_allow_html=True)
        st.dataframe(top_rated_films[["Film Title", "IMDb Rating", "Release Year"]])
        st.markdown("</div>", unsafe_allow_html=True)

    if analysis_option == "Genres":
        st.header("Genre Analysis")

        genre_count = (
            film_genre_df["GenreID"]
            .value_counts()
            .rename_axis("GenreID")
            .reset_index(name="Count")
        )
        genre_count = genre_count.merge(genres_df, on="GenreID")

        st.subheader("Number of Films per Genre")
        st.bar_chart(genre_count.set_index("Genre")["Count"])

        st.subheader("Genre Distribution")
        fig = px.pie(
            genre_count, values="Count", names="Genre", title="Genre Distribution"
        )
        st.plotly_chart(fig)

        st.subheader("Genre Co-occurrence")

        film_genres = (
            film_genre_df.groupby("FilmID")["GenreID"].apply(list).reset_index()
        )

        from itertools import combinations

        genre_pairs = []

        for genres in film_genres["GenreID"]:
            if len(genres) > 1:
                genre_pairs.extend(combinations(genres, 2))

        genre_pair_count = pd.DataFrame(genre_pairs, columns=["Genre1", "Genre2"])

        genre_pair_count = genre_pair_count.merge(
            genres_df, left_on="Genre1", right_on="GenreID"
        ).drop(columns=["GenreID"])
        genre_pair_count = genre_pair_count.merge(
            genres_df, left_on="Genre2", right_on="GenreID"
        ).drop(columns=["GenreID"])
        genre_pair_count.columns = ["Genre1", "Genre2", "Genre1Name", "Genre2Name"]
        genre_pair_count = (
            genre_pair_count.groupby(["Genre1Name", "Genre2Name"])
            .size()
            .reset_index(name="Count")
        )

        if not genre_pair_count.empty:
            fig = px.treemap(
                genre_pair_count,
                path=[px.Constant("all"), "Genre1Name", "Genre2Name"],
                values="Count",
                title="Genre Co-occurrence",
            )
            st.plotly_chart(fig)
        else:
            st.write("No genre co-occurrence data available.")

    if analysis_option == "Directors":
        st.header("Director Analysis")

        director_count = (
            film_director_df["DirectorID"]
            .value_counts()
            .rename_axis("DirectorID")
            .reset_index(name="Count")
        )
        director_count = director_count.merge(directors_df, on="DirectorID")

        st.subheader("Number of Films per Director")
        st.bar_chart(director_count.set_index("Director")["Count"])

        st.subheader("Films by Selected Director")
        director = st.selectbox("Select a director", directors_df["Director"])
        director_id = directors_df[directors_df["Director"] == director][
            "DirectorID"
        ].values[0]
        films_by_director = film_director_df[
            film_director_df["DirectorID"] == director_id
        ].merge(films_df, on="FilmID")
        st.table(films_by_director[["Film Title", "IMDb Rating", "Release Year"]])

    if analysis_option == "Stars":
        st.header("Star Analysis")

        star_count = (
            film_star_df["StarID"]
            .value_counts()
            .rename_axis("StarID")
            .reset_index(name="Count")
        )
        star_count = star_count.merge(stars_df, on="StarID")

        st.subheader("Number of Films per Star")
        st.bar_chart(star_count.set_index("Star")["Count"])

        st.subheader("Films by Selected Star")
        star = st.selectbox("Select a star", stars_df["Star"])
        star_id = stars_df[stars_df["Star"] == star]["StarID"].values[0]
        films_by_star = film_star_df[film_star_df["StarID"] == star_id].merge(
            films_df, on="FilmID"
        )
        st.table(films_by_star[["Film Title", "IMDb Rating", "Release Year"]])

    if analysis_option == "Star Film Ratings":
        st.header("Star Film Ratings")
        star_avg_ratings = (
            film_star_df.merge(films_df, on="FilmID")
            .groupby("StarID")["IMDb Rating"]
            .mean()
            .reset_index(name="Avg Rating")
        )
        star_avg_ratings = star_avg_ratings.merge(stars_df, on="StarID")

        st.subheader("Average IMDb Rating by Star")
        st.bar_chart(star_avg_ratings.set_index("Star")["Avg Rating"])

    if analysis_option == "Director Film Ratings":
        st.header("Director Film Ratings")
        director_avg_ratings = (
            film_director_df.merge(films_df, on="FilmID")
            .groupby("DirectorID")["IMDb Rating"]
            .mean()
            .reset_index(name="Avg Rating")
        )
        director_avg_ratings = director_avg_ratings.merge(directors_df, on="DirectorID")

        st.subheader("Average IMDb Rating by Director")
        st.bar_chart(director_avg_ratings.set_index("Director")["Avg Rating"])

    if analysis_option == "Genre Popularity Over Time":
        st.header("Genre Popularity Over Time")

        film_genre_df["Decade"] = (
            films_df["Release Year"] // 10 * 10
        ).values  # Extract decades

        genre_popularity = (
            film_genre_df.groupby(["Decade", "GenreID"])
            .size()
            .reset_index(name="Count")
        )
        genre_popularity = genre_popularity.merge(genres_df, on="GenreID")

        fig = px.line(
            genre_popularity,
            x="Decade",
            y="Count",
            color="Genre",
            title="Genre Popularity Over Time",
        )
        st.plotly_chart(fig)

    if analysis_option == "Top Stars by Genre":
        st.header("Top Stars by Genre")

        genre = st.selectbox("Select a genre", genres_df["Genre"])
        genre_id = genres_df[genres_df["Genre"] == genre]["GenreID"].values[0]

        top_stars_by_genre = (
            film_genre_df[film_genre_df["GenreID"] == genre_id]
            .merge(film_star_df, on="FilmID")
            .groupby("StarID")
            .size()
            .reset_index(name="Count")
            .merge(stars_df, on="StarID")
            .nlargest(10, "Count")
        )

        st.subheader(f"Top Stars in {genre}")
        st.bar_chart(top_stars_by_genre.set_index("Star")["Count"])

    if analysis_option == "Film Release Trends":
        st.header("Film Release Trends")

        films_df["Decade"] = films_df["Release Year"] // 10 * 10  # Extract decades
        release_trends = films_df["Decade"].value_counts().sort_index()

        st.subheader("Number of Films Released per Decade")
        st.line_chart(release_trends)

    if analysis_option == "IMDb Rating Distribution":
        st.header("IMDb Rating Distribution")

        st.subheader("IMDb Rating Histogram")
        st.hist(data=films_df, x="IMDb Rating", bins=20, color="skyblue")

        st.subheader("IMDb Rating KDE Plot")
        fig, ax = plt.subplots()
        films_df["IMDb Rating"].plot(kind="kde", ax=ax)
        ax.set_title("IMDb Rating Density")
        st.pyplot(fig)
