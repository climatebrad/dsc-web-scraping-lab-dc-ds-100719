"""Parse books.toscrape"""

import re
import bs4
from bs4 import BeautifulSoup
import requests
from word2number import w2n

class SoupBook(bs4.element.Tag):
    """Extend book element"""

    def __init__(self):
        super().__init__()

    @classmethod
    def convert_to_soupbook(cls, obj):
        obj.__class__ = SoupBook

    @property
    def title(self):
        """Retrieves book title. Found in <h3><a title='...'>"""
        return self.h3.a['title']

    @property
    def rating(self):
        """Retrieves book rating as number.
    Found in <p class='star-rating (One|Two|Three|Four|Five)'>
    """
        regex = re.compile("star-rating (.*)")
        return w2n.word_to_num(self.find('p', {"class" : regex}).attrs['class'][-1])

    @property
    def price(book):
        """Returns price as float. Found in <p class='price_color'>"""
        return re.sub(r'[^\d.]', '', self.find(class_="price_color").text)

    @property
    def availability(self):
        """Found in <p class='instock availability'>"""
        return self.find(class_="instock availability").text.strip()

    def as_dict(self):
        """Return dict of book elements"""
        return {
            'title' : self.title,
            'rating' : self.rating,
            'price' : self.price,
            'availability' : self.availability
        }

def retrieve_books(soup):
    """Return a list of SoupBooks.
    Found in <article class="product_pod">"""
    books = soup.select(".product_pod")
    map (SoupBook.convert_to_soupbook, books)
    return books

def retrieve_book_dicts(soup):
    """Returns list of dicts of books, with title, rating, price, and availability."""
    books = []
    for book in retrieve_book_containers(soup):
        books.append(book.as_dict())
    return books
