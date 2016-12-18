import os
import urllib2

import imdb
from bs4 import BeautifulSoup

from tinydb import TinyDB, Query

URL = "https://prime.be/films/alle"
PRIME_LIST_FILE_PATH = "prime_list.txt"

db = TinyDB('primedb_db.json')
imdb_service = imdb.IMDb()


class primedb:
    def do_your_thing(self):
        # db.purge()
        self.preload_prime_list()
        self.parse_prime_films()

        film_query = Query()
        # prime_films = db.all()
        prime_films = db.search(film_query.rating == None)

        for prime_film in prime_films:
            self.process_prime_film(prime_film)

    def preload_prime_list(self):
        if not os.path.isfile(PRIME_LIST_FILE_PATH):
            response = urllib2.urlopen(URL)
            page_source = response.read()

            print "Downloading Source from {}".format(URL)
            with open(PRIME_LIST_FILE_PATH, 'w') as list_file:
                list_file.write(page_source)

    def parse_prime_films(self):
        print "Loading Source from {}".format(PRIME_LIST_FILE_PATH)
        soup = BeautifulSoup(open(PRIME_LIST_FILE_PATH), 'html.parser')
        # prime_films = soup.find_all("div", class_="section overlay")
        prime_films = soup.find_all("a", class_="filmsimage")

        films = []

        for prime_film in prime_films:

            film_query = Query()
            film = self.parse_prime_film(prime_film)
            db_film = db.search(film_query.url == film["url"])
            if not db_film:
                db.insert(film)

            films.append(film)

        return films

    def parse_prime_film(self, prime_film):
        url = prime_film['href']
        section_overlay = prime_film.find_all("div", class_="section overlay")[0]
        title = section_overlay.h2.contents[0]
        year = int(section_overlay.p.contents[0])
        film = {"title": title, "year": year, "url": url, "rating": None}
        return film

    def process_prime_film(self, prime_film):
        title = prime_film["title"]
        year = prime_film["year"]

        print "{}".format(prime_film)
        imdb_rating = self.lookup_imdb_rating(title, year)
        if imdb_rating:
            film = Query()
            db.update({'rating': imdb_rating}, film.url == prime_film["url"])
            print imdb_rating
        else:
            print "--- NO IMDB INPUT FOUND ---"

    def lookup_imdb_rating(self, title, year):
        rating = None

        imdb_items = imdb_service.search_movie(title)
        for imdb_item in imdb_items:
            if 'year' in imdb_item.data:
                imdb_titel = imdb_item.data['title']
                imdb_year = imdb_item.data['year']
                imdb_kind = imdb_item.data['kind']
                if imdb_kind == 'movie' and title in imdb_titel and imdb_year == year:
                    film_details = imdb_service.get_movie(imdb_item.movieID)
                    rating = film_details.data['rating'] if 'rating' in film_details.data else "(no rating)"
                    break

        return rating

    def print_db(self):
        score_spreading = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, -1:0}

        prime_films = db.all()
        sorted_by_rating_prime_films = sorted(prime_films, key=lambda k: k['rating'], reverse=True)
        for prime_film in sorted_by_rating_prime_films:
            rating = prime_film["rating"]
            if isinstance(rating, float):
                score_spreading[round(rating)] += 1
            else:
                score_spreading[-1] += 1
            print prime_film

        print score_spreading

    def print_db_year_limit(self, year_limit):
        score_spreading = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, -1:0}

        prime_films = db.all()
        sorted_by_rating_prime_films = sorted(prime_films, key=lambda k: k['rating'], reverse=True)
        for prime_film in sorted_by_rating_prime_films:
            rating = prime_film["rating"]
            year = prime_film["year"]

            if int(year) < year_limit:
                continue

            if isinstance(rating, float):
                score_spreading[round(rating)] += 1
            else:
                score_spreading[-1] += 1

        print score_spreading


primedb = primedb()

# primedb.do_your_thing()
primedb.print_db()
primedb.print_db_year_limit(2010)
primedb.print_db_year_limit(2014)
