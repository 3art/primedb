import os
import urllib2

import imdb
from bs4 import BeautifulSoup

URL = "https://prime.be/films/alle"
PRIME_LIST_FILE_PATH = "prime_list.txt"

if not os.path.isfile(PRIME_LIST_FILE_PATH):
    response = urllib2.urlopen(URL)
    page_source = response.read()

    print "Downloading Source from {}".format(URL)
    with open(PRIME_LIST_FILE_PATH, 'w') as list_file:
        list_file.write(page_source)
else:
    print "Loading Source from {}".format(PRIME_LIST_FILE_PATH)
soup = BeautifulSoup(open(PRIME_LIST_FILE_PATH), 'html.parser')

films = soup.find_all("div", class_="section overlay")

imdb_service = imdb.IMDb()

for film in films:
    title = film.h2.contents[0]
    year = int(film.p.contents[0])
    imdb_items = imdb_service.search_movie(title)
    for imdb_item in imdb_items:
        if 'year' in imdb_item.data:
            imdb_titel = imdb_item.data['title']
            imdb_year = imdb_item.data['year']
            if imdb_titel == title and imdb_year == year:
                film_details = imdb_service.get_movie(imdb_item.movieID)
                rating = film_details.data['rating'] if 'rating' in film_details.data else "(no rating)"
                print "{} - {} - {}".format(title, year, rating)
                break

    print "{} - {}".format(title, year)
