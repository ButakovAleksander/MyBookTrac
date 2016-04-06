# -*- coding: utf-8 -*-

import math
import json
import numpy
from collections import defaultdict, Counter

from .text_processor import TextProcessor


class SimilarityFinder(object):
    

    def __init__(self):

        self.tokenizer = TextProcessor()

    def _find_similar(self, query_counter, book_items_counters):

        result_dict = {}
        for book_item, item_dicts in book_items_counters.items():
            cossim_title = self.cosine_similarity(query_counter[0], item_dicts[0])
            cossim_author = self.cosine_similarity(query_counter[1], item_dicts[1])
            total_cossim = cossim_title + cossim_author
            result_dict[book_item] = total_cossim

        relevant_book = sorted(((book, cos) for book, cos in result_dict.items()), 
                                    key=lambda x: x[1], reverse=True)[0]

        relevant_book = json.loads(relevant_book[0])

        return relevant_book

    def build_query_counter(self, title, author):

        tokenized_title = self.tokenizer.tokenize_string(title)
        tokenized_author = self.tokenizer.tokenize_string(author)
        title_counter = Counter({term: 1 for term in tokenized_title})
        author_counter = Counter({term: 1 for term in tokenized_author})

        return title_counter, author_counter

    def build_response_counter(self, items_list):

        book_items_counters = {}
        for item in items_list:

            if ("authors" in item["volumeInfo"]) and ("title" in item["volumeInfo"]):
                tokenized_item_title = self.tokenizer.tokenize_string(item["volumeInfo"]["title"])
                
                tokenized_item_author = []
                for auth in item["volumeInfo"]["authors"]:
                    tokenized_item_author.append(self.tokenizer.tokenize_string(auth))

                item_title_counter = Counter({term: 1 for term in tokenized_item_title})
                item_author_counter = Counter({term: 1 for tokens_list in tokenized_item_author 
                                                        for term in tokens_list})

                item = json.dumps(item)
                book_items_counters[item] = [item_title_counter, item_author_counter]

        return book_items_counters

    @staticmethod
    def cosine_similarity(query_dict, response_dict):
        """
        https://en.wikipedia.org/wiki/Cosine_similarity
        """

        terms = set(query_dict.keys()).union(set(response_dict.keys()))

        query_vector = [query_dict[k] for k in terms]
        response_vector = [response_dict[k] for k in terms]

        query_vector = numpy.asanyarray(query_vector, dtype=float)
        response_vector = numpy.asanyarray(response_vector, dtype=float)

        dot_product = 0.0
        for v1, v2 in zip(query_vector, response_vector):
            dot_product += v1*v2

        magnitude_v1 = math.sqrt(sum(i1**2 for i1 in query_vector))
        magnitude_v2 = math.sqrt(sum(i2**2 for i2 in response_vector))

        if magnitude_v2 != 0 and magnitude_v1 != 0:

            return dot_product / (magnitude_v1 * magnitude_v2)
        else:
            return 0.0


def find_relevant_book(items_list, title, author):

    sim_finder = SimilarityFinder()

    query_counter = sim_finder.build_query_counter(title, author)
    response_counter = sim_finder.build_response_counter(items_list)

    relevant_book = sim_finder._find_similar(query_counter, response_counter)

    return relevant_book
