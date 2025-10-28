import pandas as pd

class Movie:
    def __init__(self, movie_id, title, genres):
        self.id = movie_id
        self.title = title
        self.genres = genres
        self.ratings = []
    def add_rating(self, rating):
        self.ratings.append(rating)
    def average_rating(self):
        return sum(self.ratings) / len(self.ratings) if self.ratings else 0.0

class MovieDatabase:
    def __init__(self, movies_file, ratings_file):
        try:
            self.movies_df = pd.read_csv(movies_file)
            self.ratings_df = pd.read_csv(ratings_file)
        except FileNotFoundError:
            raise FileNotFoundError("Dataset files not found!")

        self.movies = {}
        self.users = {}
        self.genres = {}

        self._load_data()

    def _load_data(self):
        for _, row in self.movies_df.iterrows():
            movie = Movie(row['movieId'], row['title'], row['genres'])
            self.movies[row['movieId']] = movie

        for _, row in self.ratings_df.iterrows():
            movie_id, user_id, rating = row['movieId'], row['userId'], row['rating']
            if movie_id in self.movies:
                self.movies[movie_id].add_rating(rating)
                self.users.setdefault(user_id, set()).add(movie_id)

        for m in self.movies.values():
            for g in m.genres.split('|'):
                genre = g.strip().lower()
                self.genres.setdefault(genre, set()).add(m.id)

class Recommender:
    def __init__(self, db):
        self.db = db

    def recommend(self, user_id):
        raise NotImplementedError

class GenreRecommender(Recommender):
    def recommend(self, user_id):
        if user_id not in self.db.users:
            raise ValueError("User not found!")

        liked_genres = set()
        for m_id in self.db.users[user_id]:
            movie = self.db.movies[m_id]
            liked_genres.update(movie.genres.split('|'))

        recs = set()
        for g in liked_genres:
            recs.update(self.db.genres.get(g.lower(), []))
        recs -= self.db.users[user_id]

        sorted_recs = sorted(
            recs,
            key=lambda m_id: self.db.movies[m_id].average_rating(),
            reverse=True
        )
        top_5 = sorted_recs[:5]
        return [self.db.movies[m].title for m in top_5] or ["No recommendations available."]
    def recommend_by_genre(self, genre):
        genre = genre.lower()
        if genre not in self.db.genres:
            return []

        movie_ids = self.db.genres[genre]
        sorted_movies = sorted(
            [self.db.movies[m_id] for m_id in movie_ids],
            key=lambda m: m.average_rating(),
            reverse=True
        )
        return sorted_movies[:5]

class UserSimilarityRecommender(Recommender):
    def recommend(self, user_id):
        if user_id not in self.db.users:
            raise ValueError("User not found!")

        best_match, max_overlap = None, 0
        user_movies = self.db.users[user_id]
        for other, movies in self.db.users.items():
            if other != user_id:
                overlap = len(user_movies & movies)
                if overlap > max_overlap:
                    best_match, max_overlap = other, overlap

        if not best_match:
            return ["No similar users found."]
        suggestions = self.db.users[best_match] - user_movies
        if not suggestions:
            return ["No new movies to recommend"]

        sorted_suggestions = sorted(
            suggestions,
            key=lambda m_id: self.db.movies[m_id].average_rating(),
            reverse=True
        )
        top_5 = sorted_suggestions[:5]
        return [self.db.movies[m].title for m in top_5]

def recursive_menu(db):
    while True:
        try:
            print("\n1. Search movie\n2. Rate movie\n3. Get recommendations\n4. Exit")
            choice = input("Choose: ")

            if choice == "1":
                term = input("Enter movie title: ").lower()
                found = [f"{m.title} (Avg. Rating: {m.average_rating():.2f})" 
                        for m in db.movies.values() if term in m.title.lower()]
                print(found or ["No movie found."])

            elif choice == "2":
                uid = int(input("User ID: "))
                title_or_id = input("Enter Movie ID or Title: ").strip()

                movie = None
                if title_or_id.isdigit():
                    movie_id = int(title_or_id)
                    movie = db.movies.get(movie_id)
                else:
                    matches = [m for m in db.movies.values() if title_or_id.lower() in m.title.lower()]

                    if len(matches) == 0:
                        print("No movies found with that title.")
                        continue
                    elif len(matches) == 1:
                        movie = matches[0]
                    else:
                        print("\nMultiple matches found:")
                        for i, m in enumerate(matches, start=1):
                            print(f"{i}. {m.title} (Avg. Rating: {movie.average_rating():.2f})")
                        try:
                            choice_num = int(input("Enter the number of the movie you meant: "))
                            if 1 <= choice_num <= len(matches):
                                movie = matches[choice_num - 1]
                            else:
                                print("Invalid selection.")
                                continue
                        except ValueError:
                            print("Invalid input.")
                            continue
                if not movie:
                    print("Movie Not Found")
                    continue
            
                rating = float(input(f"Rating {movie.title} (0–5): "))
                db.users.setdefault(uid, set()).add(movie.id)
                movie.add_rating(rating)
                print(f"Rating saved for {movie.title} (Avg. Rating: {m.average_rating():.2f})!")

            elif choice == "3":
                rec_type = input("Type (genre/user): ").lower()

                if rec_type == "genre":
                    recommender = GenreRecommender(db)
                    print("\nAvailable Genres: ")
                    print("\n".join(sorted(set(db.genres.keys()))))
                    genre_input = input("\nEnter a Genre from the list above: ").strip().lower()
                    recommendations = recommender.recommend_by_genre(genre_input)
                    if recommendations:
                        print("\nRecommended Movies:")
                        for i,m in enumerate(recommendations, start=1):
                            print(f"{i}. {m.title} (Avg. Rating: {m.average_rating():.2f})")
                    else:
                        print("No Recommendations found for that genre.")
                elif rec_type =="user":
                    uid = int(input("User ID: "))
                    recommender = UserSimilarityRecommender(db)
                    recommendations = recommender.recommend(uid)
                    print("\nRecommended Movies:")
                    for i, title in enumerate(recommendations, start=1):
                        movie_obj = next((m for m in db.movies.values() if m.title == title), None)
                        if movie_obj:
                            print(f"{i}. {movie_obj.title} (Avg. Rating: {movie_obj.average_rating():.2f})")
                else:
                    print("Invalid type. Choose 'Genre' or 'User'")

            elif choice == "4":
                print("Goodbye!")
                return
            else:
                print("Invalid option.")
        except Exception as e:
            print("Error:", e)
        

if __name__ == "__main__":
    db = MovieDatabase("./movies.csv", "./ratings.csv")
    print("Welcome to Movie Recommender!")
    recursive_menu(db)
