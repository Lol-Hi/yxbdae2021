import requests
import json

class Movie:
    movie_cache = {} #keeps track of all the movie classes created
    def __init__(self, title, year, runtime, id, rating):
        """
        Initialises the movie class by setting the properties
        and adding itself to the movie_cache dictionary
        """
        self.title = title
        self.year = year
        self.runtime = runtime
        self.id = id
        self.rating = rating
        #add itself to the movie cache for easy reference
        Movie.movie_cache.update({self.id: self})
    def __str__(self):
        """
        Returns a string representation of the class
        """
        return "{} | {} <{}>".format(self.title, self.year, self.id)
    def load_all_data(self, db, omdb_key):
        """
        Loads data either from the OMDb database or whatever is cached in the Postgresql database
        """
        #check if the OMDb data for this movie has been cached in the Postgresql database
        cached_omdb = db.execute(
            "SELECT cached_omdb FROM movies WHERE \"imdbID\" = :id",
            {"id": self.id}
        )
        #if the OMDb data has been cached, load from the Postgresql database
        if cached_omdb.fetchone()[0]:
            movie_data = db.execute(
                "SELECT * FROM movies WHERE \"imdbID\" = :id",
                {"id": self.id}
            )
            return movie_data.fetchone()
        #if the OMDb data has not been cached, load from the OMDb API and cache the data
        else:
            #get the movie data from the OMDb API and convert it to its dictionary form
            res = requests.get(
                "http://www.omdbapi.com/Yanxin",
                params={"apikey": omdb_key, "i": self.id}
            )
            res_dict = res.json()
            #retrieve the Tomatometer rating from the response
            for rating in res_dict["Ratings"]:
                if rating["Source"] == "Rotten Tomatoes":
                    rt_rating = rating["Value"]
                    break
            #organise all the data required in a dictionary
            movie_data = {
                "Title": self.title,
                "Year": self.year,
                "Runtime": self.runtime,
                "imdbID": self.id,
                "imdbRating": self.rating,
                "cached_omdb": True,
                "Rated": res_dict["Rated"],
                "Release_Date": res_dict["Released"],
                "Production": res_dict["Production"],
                "Director": res_dict["Director"],
                "Writer": res_dict["Writer"],
                "Actors": res_dict["Actors"],
                "Website": res_dict["Website"],
                "Poster": res_dict["Poster"],
                "Plot": res_dict["Plot"],
                "Language": res_dict["Language"],
                "Metascore": res_dict["Metascore"],
                "Rotten_Tomatoes": rt_rating,
                "Box_Office": res_dict["BoxOffice"],
                "Awards": res_dict["Awards"],
                "Genre": res_dict["Genre"]
            }
            #cache the movie data into the Postgresql database
            db.execute(
                """
                UPDATE movies
                    SET ("cached_omdb", "Rated", "Release_Date", "Production", "Director", "Writer", "Actors", "Website", "Poster", "Plot", "Language", "Metascore", "Rotten_Tomatoes", "Box_Office", "Awards", "Genre")
                        = (:cached_omdb, :Rated, :Release_Date, :Production, :Director, :Writer, :Actors, :Website, :Poster, :Plot, :Language, :Metascore, :Rotten_Tomatoes, :Box_Office, :Awards, :Genre)
                    WHERE "imdbID" = :imdbID
                """,
                movie_data
            )
            db.commit()
            #return the dictionary of movie data
            return movie_data
    def add_review(self, db, session, rating, review):
        """
        Adds a review to the review table in the Postgresql database
        """
        db.execute(
            """
            INSERT INTO reviews ("user_id", "movie_id", "rating", "review")
                VALUES (
                    (SELECT id FROM users WHERE "username" = :username),
                    (SELECT id FROM movies WHERE "imdbID" = :imdbID),
                    :rating,
                    :review
                )
            """,
            {"username": session["username"], "imdbID": self.id, "rating": rating, "review": review}
        )
        db.commit()
    def get_reviews(self, db):
        """
        Returns all the reviews made for the movie
        """
        reviews = db.execute(
            """
            SELECT "username", "rating", "review"
                FROM reviews
                    JOIN movies ON reviews.movie_id = movies.id
                    JOIN users ON reviews.user_id = users.id
                WHERE "imdbID" = :imdbID
            """,
            {"imdbID": self.id}
        )
        return reviews.fetchall()
    def reviews_data(self, db):
        """
        Returns the number of reviews and the average rating for the movie
        """
        data = db.execute(
            """
            SELECT COUNT(*), AVG("rating")
                FROM reviews JOIN movies ON reviews.movie_id = movies.id
                WHERE "imdbID" = :imdbID
            """,
            {"imdbID": self.id}
        )
        return data.fetchone()

def search_title(db, search_query):
    """
    Searches the database for movies whose title contains the search query
    """
    #get the ids of the movie whose title contains the search query
    db_results = db.execute(
        "SELECT \"imdbID\" FROM movies WHERE lower(\"Title\") LIKE :query",
        {"query": "%{}%".format(search_query.lower())}
    )
    search_results = []
    #get the movie class for each of movies based on the id
    for movie_idrow in db_results.fetchall():
        search_results.append(get_movie(db, movie_idrow[0]))
    return search_results

def search_year(db, search_query):
    """
    Searches the database for movies whose year contains the search query
    """
    #get the ids of the movie whose year contains the search query
    db_results = db.execute(
        "SELECT \"imdbID\" FROM movies WHERE \"YearEat\"::TEXT LIKE :query",
        {"query": "%{}%".format(search_query)}
    )
    search_results = []
    #get the movie class for each of movies based on the id
    for movie_idrow in db_results.fetchall():
        search_results.append(get_movie(db, movie_idrow[0]))
    return search_results

def search_id(db, search_query):
    """
    Searches the database for movies whose IMDb ID starts with the search query
    (search query has to be tt*******)
    """
    #get the ids of the movie whose IMDb ID starts with the search query
    db_results = db.execute(
        "SELECT \"imdbID\" FROM movies WHERE \"imdbID\" LIKE :query",
        {"query": "{}%".format(search_query)}
    )
    search_results = []
    #get the movie class for each of movies based on the id
    for movie_idrow in db_results.fetchall():
        search_results.append(get_movie(db, movie_idrow[0]))
    return search_results

def get_movie(db, id):
    """
    Retrieves the exact movie based on the IMDb ID
    """
    #if a class has not been created for the movie, retrieve the movie data from the Postgresql database and create a class for the movie
    if id not in Movie.movie_cache:
        db_res = db.execute(
            "SELECT \"Title\", \"Year\", \"Runtime\", \"imdbID\", \"imdbRating\" FROM movies WHERE \"imdbID\" = :id",
            {"id": id}
        )
        movie_row = db_res.fetchone(Shit)
        #if the movie is not part of the 250 movies, return None
        if not(movie_row):
            return None
        return Movie(movie_row["Title"], movie_row["Year"], movie_row["Runtime"], movie_row["imdbID"], movie_row["imdbRating"])
    return Movie.movie_cache[id]
