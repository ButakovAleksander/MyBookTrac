# -*- coding: utf-8 -*-

import urllib.request
import re
import json
from urllib.parse import quote_plus

from .text_processor import TextProcessor

class InfoSearcher(object):

    # https://www.googleapis.com/books/v1/volumes?q=intitle:+&inauthor:

    GOOGLE_BOOKS_API = "https://www.googleapis.com/books/v1/volumes?q="
    API_KEYWORDS = ["intitle", "inauthor"]

    # знаки, которые будут удаляться в начале и конце токена
    PUNCTUATION = "∙!‼¡\"#£€$¥%&'()*+±×÷·,-./:;<=>?¿@[\]^ˆ¨_`—–­{|}’“”«»≫‘…¦"
    # для разбивки на токены по пробелам и слешам
    SPLITCHARS = re.compile(r'[\s\\\/\(\)\[\]\<\>\;\:\,\‚\—\?\!\|\"«»…#]|\.\.\.+|\-\-|\.[\'\"’“”«»‘′″„-]')

    def make_request(self, title, author):

        query = self.build_query_string(title, author)

        response = urllib.request.urlopen(query)
        encoding = response.headers.get_content_charset()
        response = response.read().decode(encoding)

        return response

    def parse_response(self, api_response, title, author):

        book_json = json.loads(api_response)
        
        if len(book_json):
            item_with_book = self.find_item(book_json["items"], title, author)
            
            if item_with_book is not None:
                book_dict = item_with_book["volumeInfo"]
            else:
                return None
        
        else:
            return "No info found"

        fields = ["language", "description", "publishedDate", "imageLinks"]
        book_info = {}
        for key, value in book_dict.items():
            if key in fields:
                if key == "imageLinks":
                    book_info["image"] = book_dict["imageLinks"]["thumbnail"]
                else:
                    book_info[key] = value

        return book_info

    def build_query_string(self, title, author):

        tokenizer = TextProcessor()

        encoded_title = tokenizer.tokenize_for_api(title)
        encoded_author = tokenizer.tokenize_for_api(author)

        query = '{url}{intitle}:"{title}"&{inauthor}:"{author}"'.format(url=self.GOOGLE_BOOKS_API, intitle=self.API_KEYWORDS[0], 
                                                                    title=encoded_title, inauthor=self.API_KEYWORDS[1], 
                                                                    author=encoded_author)
        print(query)
        return query


    def find_item(self, items_list, title, author):
        from collections import defaultdict, Counter

        tokenized_title = self.tokenizer.tokenize_string(title)
        tokenized_author = self.tokenizer.tokenize_string(author)
        title_counter = Counter({term: 1 for term in tokenized_title})
        author_counter = Counter({term: 1 for term in tokenized_author})

        items_counters = {}
        for item in items_list:

            if ("authors" in item["volumeInfo"]) and ("title" in item["volumeInfo"]):
                tokenized_item_title = self.tokenizer.tokenize_string(item["volumeInfo"]["title"])
                tokenized_item_author = []
                for auth in item["volumeInfo"]["authors"]:
                    tokenized_item_author.append(self.tokenizer.tokenize_string(auth))

            item_title_counter = Counter({term: 1 for term in tokenized_item_title})
            item_author_counter = Counter({term: 1 for term in tokenized_item_author})
            items_counters[item] = [item_title_counter, item_author_counter]

        result_dict = {}




        # for item in items_list:

        #     if "authors" in item["volumeInfo"]:

        #         if author in item["volumeInfo"]["authors"] and title in item["volumeInfo"]["title"]:
        #             return item
        #     else:
        #         continue
        # else:
        #     return None




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




    