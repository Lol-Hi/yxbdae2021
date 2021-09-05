# did u see this file in the README
# no right
# so y did u still check here?
# smh never follow instructions

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

movies = []
with open("movies.csv") as f:
    headers = f.readline().strip().split(";")
    for line in f:
        line_lst = line.strip().split(";")
        movie_dict = dict(zip(headers, line_lst))
        movies.append(movie_dict)

db.execute(
    """
    CREATE TABLE movies (
        "id" SERIAL PRIMARY KEY,
        "Title" TEXT NOT NULL,
        "Year" INT4 NOT NULL,
        "Runtime" INT4 NOT NULL,
        "imdbID" VARCHAR NOT NULL,
        "imdbRating" FLOAT8 NOT NULL,
        "cached_omdb" BOOL NOT NULL,
        "Rated" VARCHAR,
        "Release_Date" VARCHAR,
        "Production" VARCHAR,
        "Director" VARCHAR,
        "Writer" VARCHAR,
        "Actors" VARCHAR,
        "Website" VARCHAR,
        "Poster" VARCHAR,
        "Plot" VARCHAR,
        "Language" VARCHAR,
        "Metascore" VARCHAR,
        "Rotten_Tomatoes" VARCHAR,
        "Box_Office" VARCHAR,
        "Awards" VARCHAR,
        "Genre" VARCHAR
    )
    """
)
db.commit()

for movie in movies:
    db.execute(
        """
        INSERT INTO movies ("Title", "Year", "Runtime", "imdbID", "imdbRating", "cached_omdb")
            VALUES (:Title, :Year, :Runtime, :imdbID, :imdbRating, FALSE)
        """,
        movie
    )
    db.commit()

db.close()
