# IMDb Movie Scraper

## Description

IMDb Movie Scraper is a Python-based project designed to scrape movie data from the IMDb website. This project fetches details such as the film title, IMDb rating, release year, genre, director, movie image, and stars for the top-rated movies listed on IMDb. The scraped data is then stored in a CSV file, making it easy to analyze and utilize for various purposes, such as data analysis, machine learning projects, or movie recommendation systems.

## Features

- **Scrapes top-rated movies from IMDb**: Fetches movie details from the IMDb top-rated movies list.
- **Stores data in a CSV file**: All the scraped data is stored in a well-structured CSV file for easy access and analysis.
- **Detailed movie information**: Collects comprehensive details about each movie, including title, rating, release year, genre, director, and cast.

## Data Scraped

The following data is scraped for each movie:

- **Film Title**: The title of the movie.
- **IMDb Rating**: The IMDb rating of the movie.
- **Release Year**: The year the movie was released.
- **Genre**: The genre(s) of the movie.
- **Director**: The director(s) of the movie.
- **Movie Image**: URL of the movie's poster image.
- **Stars**: The main cast of the movie.

## How to Use

### Prerequisites

- Python 3.x
- Required Python libraries: `os`, `time`, `requests`, `pandas`, `bs4`

You can install the required libraries using pip:
```bash
pip install requests pandas beautifulsoup4
