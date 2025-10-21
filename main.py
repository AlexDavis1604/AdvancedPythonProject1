import pandas as pd

class Movie:
    def __init__(self, movie_id, title, genres):
        self.id = movie_id
        self.title = title
        self.genres = genres
        # self.average_rating = average_rating

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
                # self.movies[movie_id].add_rating(rating)
                self.users.setdefault(user_id, set()).add(movie_id)

        for m in self.movies.values():
            for g in m.genres.split('|'):
                self.genres.setdefault(g, set()).add(m.id)

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

        recs = []
        for g in liked_genres:
            for m_id in self.db.genres.get(g, []):
                m = self.db.movies[m_id]
                if m.average_rating() > 4.0 and m_id not in self.db.users[user_id]:
                    recs.append(m.title)
        return recs or ["No recommendations available."]

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
        return [self.db.movies[m].title for m in suggestions] or ["No new movies to recommend."]

def recursive_menu(db):
    try:
        print("\n1. Search movie\n2. Rate movie\n3. Get recommendations\n4. Exit")
        choice = input("Choose: ")

        if choice == "1":
            term = input("Enter movie title: ").lower()
            found = [m.title for m in db.movies.values() if term in m.title.lower()]
            print(found or ["No movie found."])

        elif choice == "2":
            uid = int(input("User ID: "))
            mid = int(input("Movie ID: "))
            rating = float(input("Rating (0–5): "))
            db.users.setdefault(uid, set()).add(mid)
            db.movies[mid].add_rating(rating)
            print("Rating saved!")

        elif choice == "3":
            uid = int(input("User ID: "))
            rec_type = input("Type (genre/user): ").lower()
            rec = GenreRecommender(db) if rec_type == "genre" else UserSimilarityRecommender(db)
            print("Recommendations:", rec.recommend(uid))

        elif choice == "4":
            print("Goodbye!")
            return
        else:
            print("Invalid option.")
    except Exception as e:
        print("Error:", e)
    recursive_menu(db)  # recursion

if __name__ == "__main__":
    db = MovieDatabase("./movies.csv", "./ratings.csv")
    print("Welcome to Movie Recommender!")
    recursive_menu(db)