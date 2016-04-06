# -*- coding: utf-8 -*-

import urllib.request
import re
import json
import ssl
import wikipedia

from urllib.parse import quote_plus

from .text_processor import TextProcessor


class AuthorSearcher(object):

    """
    Find some info about the author in wikipedia.
    The returned bio is language dependant.
    Uses the language given for a book.
    """

    def __init__(self):
        
        self.language_dict = {
                'Russian': 'ru',
                'English': 'en',
                'Spanish': 'es',
                'German': 'de',
                'French': 'fr',
                'Italian': 'it',
                'Portuguese': 'pt',
                'Arabic': 'ar',
                'Polish': 'pl',
                'Dutch': 'nl',
                'Chinese': 'zh',
                'Hindi/Urdu': 'hi',
                'Japanese': 'ja',
                'Bengali': 'bn',
                'Korean': 'ko',
                'Finnish': 'fi'
        }

    def find_author_in_wiki(self, author, language):

        wiki_lang = self.language_dict[language]

        wikipedia.set_lang(wiki_lang)        

        search_results = wikipedia.search(author)
        
        if not search_results:
            suggested_author = wikipedia.suggest(author)
        else:
            suggested_author = author
        
        
        w_author = suggested_author

        try:
            author_bio = wikipedia.summary(w_author, sentences=5)
        except (wikipedia.exceptions.DisambiguationError):
            return None

        
        return author_bio


class PhotoSearcher(object):


    GOOGLE_IMAGES_API = 'https://www.google.com/search?site=&tbm=isch&q='

    CLASS_WITH_IMAGE = "//*[re:test(@class, 'rg_meta', 'i')]"
    RG_META = re.compile(r'<div\s+class=\"rg_meta\">(.*?)</div>')

    LANGUAGE_DICT = {
                'Russian': 'писатель',
                'English': 'writer',
                'Spanish': 'writer',
                'German': 'schriftsteller',
                'French': 'writer',
                'Italian': 'writer',
                'Portuguese': 'writer',
                'Arabic': 'writer',
                'Polish': 'writer',
                'Dutch': 'writer',
                'Chinese': 'writer',
                'Hindi/Urdu': 'writer',
                'Japanese': 'writer',
                'Bengali': 'writer',
                'Korean': 'writer',
                'Finnish': 'writer'
        }

    def __init__(self):
        self.tokenizer = TextProcessor()

    def get_photo(self, author, language):

        query = self._build_query_string(author, language)
        response = self._load_images(query)
        photo = self._find_first_image(response)

        return photo

    def _load_images(self, query):

        headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
        }

        context = ssl._create_unverified_context()

        req = urllib.request.Request(query, headers=headers)

        response = urllib.request.urlopen(req, context=context)
        encoding = response.headers.get_content_charset()
        response = response.read().decode(encoding)

        return response

    def _find_first_image(self, htree):

        rg_meta_div = self.RG_META.search(htree).group(1)
        image_meta = json.loads(rg_meta_div)
        image_link = image_meta["ou"]

        return image_link

    def _build_query_string(self, author, language):

        encoded_author = self.tokenizer.tokenize_for_api(author)

        query = '{url}{lang}+"{author}"'.format(url=self.GOOGLE_IMAGES_API, lang=quote_plus(self.LANGUAGE_DICT[language]), author=encoded_author)

        return query



def get_author_info(author, language):

    bio_searcher = AuthorSearcher()
    photo_searcher = PhotoSearcher()
    author_bio = bio_searcher.find_author_in_wiki(author, language)
    photo = photo_searcher.get_photo(author, language)

    author_info = {

        'author_bio': author_bio,
        'photo': photo
    }

    return author_info