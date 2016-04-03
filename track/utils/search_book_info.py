# -*- coding: utf-8 -*-

import urllib.request
import re
import json
import ssl
from urllib.parse import quote_plus

from .text_processor import TextProcessor
from .cossim import find_relevant_book

class InfoSearcher(object):

    # https://www.googleapis.com/books/v1/volumes?q=intitle:+&inauthor:

    GOOGLE_BOOKS_API = "https://www.googleapis.com/books/v1/volumes?q="
    API_KEYWORDS = ["intitle", "inauthor"]

    # знаки, которые будут удаляться в начале и конце токена
    PUNCTUATION = "∙!‼¡\"#£€$¥%&'()*+±×÷·,-./:;<=>?¿@[\]^ˆ¨_`—–­{|}’“”«»≫‘…¦"
    # для разбивки на токены по пробелам и слешам
    SPLITCHARS = re.compile(r'[\s\\\/\(\)\[\]\<\>\;\:\,\‚\—\?\!\|\"«»…#]|\.\.\.+|\-\-|\.[\'\"’“”«»‘′″„-]')

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

        # response = urllib.request.urlopen(query)
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
        print(query)
        return query


    # def find_relevant_book(self, items_list, title, author):
        
    #     from collections import defaultdict, Counter
    #     from .cossim import SimilarityFinder

    #     # tokenized_title = self.tokenizer.tokenize_string(title)
    #     # tokenized_author = self.tokenizer.tokenize_string(author)
    #     # title_counter = Counter({term: 1 for term in tokenized_title})
    #     # author_counter = Counter({term: 1 for term in tokenized_author})

    #     # book_items_counters = {}
    #     # for item in items_list:

    #     #     if ("authors" in item["volumeInfo"]) and ("title" in item["volumeInfo"]):
    #     #         tokenized_item_title = self.tokenizer.tokenize_string(item["volumeInfo"]["title"])
                
    #     #         tokenized_item_author = []
    #     #         for auth in item["volumeInfo"]["authors"]:
    #     #             tokenized_item_author.append(self.tokenizer.tokenize_string(auth))

    #     #         item_title_counter = Counter({term: 1 for term in tokenized_item_title})
    #     #         item_author_counter = Counter({term: 1 for tokens_list in tokenized_item_author 
    #     #                                                 for term in tokens_list})

    #     #         item = json.dumps(item)
    #     #         book_items_counters[item] = [item_title_counter, item_author_counter]


    #     result_dict = {}
    #     for book_item, item_dicts in book_items_counters.items():
    #         cossim_title = SimilarityFinder().cosine_similarity(title_counter, item_dicts[0])
    #         cossim_author = SimilarityFinder().cosine_similarity(author_counter, item_dicts[1])
    #         total_cossim = cossim_title + cossim_author
    #         result_dict[book_item] = total_cossim

    #         # print()
    #         # print('a',item_dicts[1])
    #         # print('t', item_dicts[0])
    #         # print('c', total_cossim)
            
    #     relevant_book = sorted(((book, cos) for book, cos in result_dict.items()), 
    #                                 key=lambda x: x[1], reverse=True)[0]

    #     relevant_book = json.loads(relevant_book[0])

    #     return relevant_book


def get_book_info(title, author):

    searcher = InfoSearcher()
    response = searcher.make_request(title, author)

    return searcher.parse_response(response, title, author)



# s = InfoSearcher()
# # print(s.tokenize_string("Angus, Thongs and Full-frontal Snogging: Confessions of Georgia Nicolson, Louise Rennison"))
# response = s.make_request("Angus, Thongs and Full-frontal Snogging: Confessions of Georgia Nicolson", "Louise Rennison")
# book_info = s.parse_response(response)

# import codecs
# with codecs.open(r'output.txt', 'w', 'utf-8') as outfile:
#     for key, value in book_info.items():
#         outfile.write(key)
#         outfile.write(": ")
#         outfile.write(value)
#         outfile.write("\n")




    