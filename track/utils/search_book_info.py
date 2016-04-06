# -*- coding: utf-8 -*-

import urllib.request
import re
import json
import ssl
from urllib.parse import quote_plus

from .text_processor import TextProcessor
from .cossim import find_relevant_book

class InfoSearcher(object):

    """
    Find description and a cover image for a book.
    """

    # https://www.googleapis.com/books/v1/volumes?q=intitle:+&inauthor:

    GOOGLE_BOOKS_API = "https://www.googleapis.com/books/v1/volumes?q="
    API_KEYWORDS = ["intitle", "inauthor"]

    def __init__(self):
        self.tokenizer = TextProcessor()

    def make_request(self, title, author):

        query = self.build_query_string(title, author)

        headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
        }

        context = ssl._create_unverified_context()

        req = urllib.request.Request(query, headers=headers)

        response = urllib.request.urlopen(req, context=context)

        encoding = response.headers.get_content_charset()
        response = response.read().decode(encoding)

        return response

    def parse_response(self, api_response, title, author):

        book_json = json.loads(api_response)
        
        if len(book_json):
            item_with_book = find_relevant_book(book_json["items"], title, author)
            
            if item_with_book is not None:
                book_dict = item_with_book["volumeInfo"]
            else:
                return None
        
        else:
            return None

        fields = ["description", "imageLinks"]
        book_info = {}
        for key, value in book_dict.items():
            if key in fields:
                if key == "imageLinks":
                    book_info["image"] = book_dict["imageLinks"]["thumbnail"]
                else:
                    book_info[key] = value

        return book_info

    def build_query_string(self, title, author):

        encoded_title = self.tokenizer.tokenize_for_api(title)
        encoded_author = self.tokenizer.tokenize_for_api(author)

        query = '{url}{intitle}:"{title}"&{inauthor}:"{author}"'.format(url=self.GOOGLE_BOOKS_API, intitle=self.API_KEYWORDS[0], 
                                                                    title=encoded_title, inauthor=self.API_KEYWORDS[1], 
                                                                    author=encoded_author)
        return query


def get_book_info(title, author):

    searcher = InfoSearcher()
    response = searcher.make_request(title, author)

    return searcher.parse_response(response, title, author)

    