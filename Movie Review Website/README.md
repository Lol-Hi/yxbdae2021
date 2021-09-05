## Project Title
Movie Review Website (using Flask)

----
## Description
This is a website that lists out details of the top 250 movies of all time,
and allows users to leave a rating and review for the movies
– much like the IMDb website.

There is also an API service which provides details like the
title, year of release, IMDb ID, director, actors and IMDb rating of the movie,
as well as the number of reviews provided by users on the site
and the average rating given by the users of this site for the movie.

----
## Motivations
Honestly there isn't any personal motivation for this project other than to
get the marks for my CEP grade (since this is an assigned task anyway). 😇

----
## Build Status
- Importing movie data to database: `Working`
- Creating the navbar: `Working`
- Login page: `Working`
- Signup page: `Working`
- Search function: `Working`
- Individual movie pages with movie data from OMDb API: `Working`
- Processing reviews: `Working`
- API service: `Working`

----
## Screenshots, Features and Code Snippets

#### Homepage
There is really nothing much to the homepage except for some movie recommendations, which are simply 5 random movies taken from the Postgresql database.

###### Function for the homepage
```python
# in application.py

@app.route("/")
def index():
    """
    Renders the homepage, with movie recommendations
    """
    #get the ids of 5 random movies from the Postgres database
    db_movies = db.execute(
        "SELECT \"imdbID\" FROM movies ORDER BY RANDOM() LIMIT 5"
    )
    movie_lst = []
    #get the movie class for each of the 5 movies based on the id
    for movie_idrow in db_movies.fetchall():
        movie_lst.append(get_movie(db, movie_idrow[0]))
    return render_template("index.html", movies=movie_lst)
```

###### Function to retrieve the relevant movie class
```python
# in movie.py

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
        movie_row = db_res.fetchone()
        #if the movie is not part of the 250 movies, return None
        if not(movie_row):
            return None
        return Movie(movie_row["Title"], movie_row["Year"], movie_row["Runtime"], movie_row["imdbID"], movie_row["imdbRating"])
    return Movie.movie_cache[id]
```

#### Login and Signup pages
The login page is the usual one which only requires the username and password of the user.
The signup page is also relatively simple with the username, email and 2 fields for the password (password and confirm password).

The password is checked locally by checking the entered password against the password saved in the database – instead of directly using SQL statements – such that SQL injection would not occur.
Furthermore, the passwords are hashed when they are saved in the database to further prevent against SQL injection and since it is a one-way hash, anyone with access to the database would still be unable to get the password of someone else's account.

###### Functions for the login and signup pages
```python
# in application.py

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Renders the login page
    If the user manages to log in, will redirect to the homepage
    """
    login_error_message = ""
    if request.method == "POST":
        #get the username and password entered
        username = request.form.get("login_username")
        password = request.form.get("login_password")
        #if any field is empty, return to the login page with an error message
        if not (username and password):
            return render_template(
                "login.html",
                login_error_message="Login failed. Please ensure that you have filled in all the fields"
            )
        #Check for the hashed password
        db_query = db.execute(
            "SELECT password FROM users WHERE username = :username",
            {"username": username}
        )
        #if the account does not exist, return to the login page with an error message
        if db_query.rowcount == 0:
            return render_template(
                "login.html",
                login_error_message="Login failed. Please enter a valid username"
            )
        #hash the entered password to compare with the hashed password saved in the database
        hashed_pw = str(hashlib.pbkdf2_hmac("sha256", bytes(password, "utf-8"), bytes(salt, "utf-8"), 100000))
        #if the password is correct, log the user in and redirect to the homepage
        if db_query.fetchone()[0] == hashed_pw:
            session["username"] = username
            return redirect(url_for(".index"))
        #if the password is incorrect, return to the login page with an error message
        return render_template(
            "login.html",
            login_error_message="Login failed. Please enter the correct password"
        )
    #if it was just a GET request then simply display the login page
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    """
    Renders the signup page
    After the user signs up, will give the options of
    - returning to the homepage
    - going to the login page
    """
    signup_error_message = ""
    if request.method == "POST":
        #get the username, email and passwords entered
        username = request.form.get("signup_username")
        email = request.form.get("signup_email")
        password = request.form.get("signup_password")
        password2 = request.form.get("signup_cfm_password")
        #if any field is empty, return to the login page with an error message
        if not(username and email and password and password2):
            return render_template(
                "signup.html",
                signup_error_message="Signup failed. Please ensure that you have filled in all the fields"
            )
        #if the passwords do not correspond, return to the login page with an error message
        if password != password2:
            return render_template(
                "signup.html",
                signup_error_message="Signup failed. Please fill in the same password for the last 2 fields"
            )
        #if the password is too long, return the the login page with an error message
        if len(password) > 30:
            return render_template(
                "signup.html",
                signup_error_message="Signup failed. Please fill in a password with less than 30 characters."
            )
        #hash the entered password and save the information to the database
        #then go the the signed_up page with options to return to the homepage or go to the login page
        hashed_pw = str(hashlib.pbkdf2_hmac("sha256", bytes(password, "utf-8"), bytes(salt, "utf-8"), 100000))
        db.execute(
            "INSERT INTO users (username, email, password) VALUES (:username, :email, :password)",
            {"username": username, "email": email, "password": hashed_pw}
        )
        db.commit()
        return render_template("signed_up.html")
    #if it was just a GET request then simply display the signup page
    return render_template("signup.html")
```

#### Search function
For the search box I used 3 functions to process the query – one to search based on title, another on the year and finally, the IMDb ID. The search then leads to a page where the results are listed out.

If the search button is clicked without any search query, the user is redirected back to the homepage.

###### Function to display the search results
```python
# in application.py

@app.route("/search_results", methods=["POST"])
def search():
    """
    Processes the search request and produces the results
    """
    #get the search query
    search_query = request.form.get("search")
    #if there is no search query, redirect to the homepage
    if not(search_query):
        return redirect(url_for(".index"))
    #search for results based on the search query
    search_results = set() #to ensure that there is no overlap in results from the 3 search functions
    search_results.update(search_title(db, search_query))
    search_results.update(search_year(db, search_query))
    search_results.update(search_id(db, search_query))
    #list out the search results in another page
    return render_template(
        "search_results.html",
        query=search_query,
        search_results=search_results,
        search_present=(len(search_results) > 0)
    )
```

###### Functions to carry out the search
```python
# in movie.py

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
        "SELECT \"imdbID\" FROM movies WHERE \"Year\"::TEXT LIKE :query",
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
```

#### Movie pages
Each individual movie page consists of data from the OMDb API and a review section at the bottom of the page.
Only users who are logged in can post a review and each user can only post one review per account per movie.

When leaving a rating, users simply have to click the green stars in the rating section to indicate the number of stars they want to give for the movie.
A hidden field is used to process the input given from the star buttons.

###### Function to display the movie page and process reviews
```python
# in application.py

@app.route("/movie/<movie_id>", methods=["GET", "POST"])
def movie(movie_id):
    """
    Renders the individual movie pages
    If the user posts a review, updates the relevant variables and renders the updated movie page
    """
    #get the movie class based on the IMDb ID
    movie = get_movie(db, movie_id)
    #if the movie is not one of the 250 movies, return a 404 error
    if not(movie):
        return redirect(url_for(".error", error_no="404", error_message="Page not found"))
    #load the data of the movie with the movie class
    movie_data = movie.load_all_data(db, os.getenv("OMDB_KEY"))
    error = None
    #if a review is posted
    if request.method == "POST":
        #get the rating and review posted
        rating = request.form.get("user_rating")
        review = request.form.get("user_review")
        #if any field is empty, return an error
        if not(rating and review):
            error = "Please ensure that you left both a rating and a review."
        #if there is not error, add the review to the movie
        movie.add_review(db, session, rating, review)
    #get all the reviews to be displayed
    movie_reviews = movie.get_reviews(db)
    can_review = False
    cannot_review_reason = ""
    #if user is logged in
    if session.get("username"):
        #check if the user has reviewed the movie
        reviewed = db.execute(
            """
            SELECT COUNT(*)
                FROM reviews
                    JOIN movies ON reviews.movie_id = movies.id
                    JOIN users ON reviews.user_id = users.id
                WHERE "imdbID" = :imdbID AND "username" = :username
            """,
            {"imdbID": movie.id, "username": session["username"]}
        )
        #if the user has reviewed the movie, do not allow him/her to review again
        if reviewed.fetchone()[0]:
            cannot_review_reason = "You have already posted a review for this movie."
        #if the user hasn't reviewed the movie, allow him/her to review it
        else:
            can_review = True
    #if the user is not logged in, do not allow him/her to review the movie
    else:
        cannot_review_reason = Markup("Please <a href=\"{{ url_for('login') }}\">log in to your account</a> to leave a review")
    #display the movie page
    return render_template(
      "movie_data.html",
      movie_data=movie_data,
      can_review=can_review,
      cannot_review_reason=cannot_review_reason,
      movie_reviews=movie_reviews,
      reviews_available=(len(movie_reviews) > 0)
    )
```

###### Method to load movie data
```python
# in movie.py

class Movie:
    # ...
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
                "http://www.omdbapi.com/",
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
```

<!---
Congrats to u u've probably found the easiest way to get out of this madness
Simply find the link inside this photo:
https://drive.google.com/file/d/1B7nw72H80jQSUv2EH7f3ZXIz5Dyir57C/view?usp=sharing

and come on lah i spent so much time setting the other 2 methods
do give them a go pls pls pls
--->

###### Methods to deal with user reviews
```python
# in movie.py

class Movie:
    # ...
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
```

#### API calls
The site also provides an API service where it would return the
- Title of the movie
- Year of the movie's release
- IMDb ID for the movie
- Director of the movie
- Actors in the movie
- IMDb rating for the movie
- Number of reviews left for the movie on this site
- Average rating left by users for the movie

###### Function to return the result from an API call
```python
# in application.py

@app.route("/api/<movie_id>")
def api_call(movie_id):
    """
    Allows the user to make calls to the API provided
    """
    #get the movie class based on the IMDb ID
    movie = get_movie(db, movie_id)
    #if the movie is not one of the 250 movies, return a 404 error
    if not(movie):
        return "Eror 404: Page not found"
    #load the data of the movie with the movie class
    movie_data = movie.load_all_data(db, os.getenv("OMDB_KEY"))
    #load the data about the reviews left with the movie class
    reviews_data = movie.reviews_data(db)
    #organise the data in a dictionary before converting it to a JSON format to be returned
    api_dict = {
        "title": movie_data["Title"],
        "year": movie_data["Year"],
        "imdb_id": movie_data["imdbID"],
        "director": movie_data["Director"],
        "actors": movie_data["Actors"],
        "imdb_rating": movie_data["imdbRating"],
        "review_count": reviews_data["count"],
        "average_score": float(reviews_data["avg"])
    }
    api_json = json.dumps(api_dict, indent=4)
    return api_json
```

###### Method to get review data
```python
# in movie.py

class Movie:
    # ...
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
```

----
## Installation
Firstly, ensure that python3 is installed in your computer. If not, you can install it [here](https://www.python.org/downloads/).

Secondly, ensure that you have downloaded the following files and folders for the program.
- `requirements.txt` – a text file containing all the libraries to be installed
- `templates` – containing all the HTML documents
  - `layout.html` - main template for all other HTML documents. Contains the navbar
  - `index.html` – main homepage
  - `login.html` – login page
  - `signup.html` – signup page
  - `signed_up.html` - page displayed after user signs up
  - `search_results.html` – page displaying the search results
  - `movie_data.html` – page for the individual movies
  - `error.html` – page that is displayed when an error occurs
- `static` – containing the CSS and Javascript files
  - `css/styles.css` – CSS stylesheet for the webpage
  - `script.js` – contains code to process the data from the rating input
- `application.py` – the main program that runs the website
- `movie.py` – containing the `Movie` class and search functions
- `import.py` – program to import the movie data from `movies.csv` to the database
- `movies.csv` – containing movie data like the title, year released, runtime, IMDb ID and IMDb rating

Last but not least, ensure that you have installed the required packages for the program by running `$ pip install -r requirements.txt`

----
## How to Use?
Before running the program, you will have to [set up a few environment variables](https://www.schrodinger.com/kb/1842).
- `FLASK_APP` – Determines the program to run for the website.
  Set it to "application.py".
- `DATABASE_URL` – URL to access the database.
  Set it to "postgres://qcqbnwzpratskd:25135160d72db5cbc00f6ff96a90582b7bf987b5dbae34a6c2deed9158777057@ec2-107-22-238-217.compute-1.amazonaws.com:5432/d2tmhfjd6dsefu".
- `OMDB_KEY` – API key for the OMDb database.
  Register at http://www.omdbapi.com/ to get it.
- `HASH_SALT` – Salt used when hashing passwords.
  If not set, will default to "salt".
  Ensure that you use the same salt every time you access the same account.

To run the program and view the website,
1. In the command line, navigate to the directory containing the app
2. Type `$ flask run` to start up the application
3. Among the lines produced, there should one that says `* Running on <URL>`. Copy the URL to your browser to see the website

The movie pages can be accessed by searching with the search box on the navbar.
Alternatively, you can access any movie page directly by its IMDb ID with `/movie/<IMDb_ID>`.

There is also an API service that can be accessed with `/api/<IMDb_ID>`.

<!-- nothing here lol -->
