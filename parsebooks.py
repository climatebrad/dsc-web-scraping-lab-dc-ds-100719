"""Parse books.toscrape"""

import re
import requests
import bs4
from bs4 import BeautifulSoup
from word2number import w2n

class SoupBook(bs4.element.Tag):
    """Extend book element"""

    def __init__(self):
        super().__init__()

    @classmethod
    def convert_to_soupbook(cls, obj):
        """Convert to a SoupBook class."""
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
    def price(self):
        """Returns price as float. Found in <p class='price_color'>"""
        return float(re.sub(r'[^\d.]', '', self.find(class_="price_color").text))

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
    for book in books:
        SoupBook.convert_to_soupbook(book)
    return books

def retrieve_book_dicts(soup):
    """Returns list of dicts of books, with title, rating, price, and availability."""
    books = []
    for book in retrieve_books(soup):
        books.append(book.as_dict())
    return books

def retrieve_next_url(base_url: str, soup):
    """Returns the url of the next page, if it exists.
Found in <li class="next"><a href="...">"""
    next_page = soup.find('li', class_='next')
    if next_page:
        return requests.compat.urljoin(base_url, next_page.a['href'])
    return None

def get_soup(url: str):
    """Returns the soup of the url."""
    return BeautifulSoup(requests.get(url).content, 'html.parser')

def get_book_dicts_from_url(url: str):
    """Returns book dicts, given a url"""
    soup = get_soup(url)
    return retrieve_book_dicts(soup)

def retrieve_all_book_dicts(base_url: str, limit: int = None):
    """Returns list of book dicts, traversing pages from base_url.
If limit is set, stops when length of books is greater than or equal to limit."""
    books = []
    current_url = base_url
    while current_url:
        soup = get_soup(current_url)
        books.extend(retrieve_book_dicts(soup))
        if limit and (len(books) > limit):
            break
        current_url = retrieve_next_url(current_url, soup)
    return books
