# AdvancedPythonProject1

# Movie Recommender System

## Overview
This project is a Python-based movie recommender system that allows users to:
- Search for movies by title  
- Rate movies by ID or name  
- Get personalized movie recommendations based on:
  - Genre (top-rated movies in a specific genre)  
  - User similarity (movies liked by users with similar taste)  

It uses the MovieLens dataset (`movies.csv` and `ratings.csv`) and supports interaction through a simple text-based menu.

---

## Features
### 1. Search Movies
- Search any movie by title.
- Displays matching results with their average rating.

### 2. Rate Movies
- Enter a movie ID or part of a movie title to find and rate it.
- If multiple matches exist, the program lists them so you can pick the correct one.
- Your rating updates the movie’s average rating.

### 3. Get Recommendations
Choose between:
- `genre` → Lists all available genres and recommends the top-rated movies in that genre.
- `user` → Finds the most similar user and recommends movies they liked that you haven’t rated yet.  
Each recommendation includes the movie title and average rating.

### 4. Exit
- Cleanly exits the program.

---

## How It Works
### Data Loading
- `MovieDatabase` loads data from `movies.csv` and `ratings.csv`.
- Builds dictionaries for:
  - `movies` → `{movieId: Movie object}`
  - `users` → `{userId: set of movieIds rated}`
  - `genres` → `{genre_name: set of movieIds}`

### Movie Representation
Each movie is stored as a `Movie` object with:
- `id`, `title`, `genres`, and a list of `ratings`
- Method `average_rating()` to calculate its mean rating.

### Recommenders
- **GenreRecommender:**  
  Suggests top 5 movies in a given genre based on average ratings.  
- **UserSimilarityRecommender:**  
  Finds the most similar user (based on overlapping rated movies) and recommends the top 5 new movies they’ve rated highly.

---

## How to Run
### Requirements
- Python 3.8 or later  
- Pandas library

### Installation
```bash
pip install pandas
