# -*- coding: utf-8 -*-

import urllib.request
import re
import json
# import io
import wikipedia

# from lxml import etree
from urllib.parse import quote_plus

from .text_processor import TextProcessor

# https://wikipedia.readthedocs.org/en/latest/code.html


class AuthorSearcher(object):

    def __init__(self):
        
        self.language_dict = {
                'Russian': 'ru',
                'English': 'en',
                'Spanish': 'es',
                'German': 'de',
                'French': 'fr',
                'Italian': 'it',
                'Portuguese': 'pt',
                'Arabic': 'ar'
        }

    def find_author_in_wiki(self, author, language):

        wiki_lang = self.language_dict[language]

        wikipedia.set_lang(wiki_lang)        

        search_results = wikipedia.search(author)
        
        if not search_results:
            suggested_author = wikipedia.suggest(author)
        else:
            suggested_author = author
        
        # search_results = wikipedia.search(suggested_author)

        # if not search_results:
        #     return None

        w_author = suggested_author

        try:
            author_bio = wikipedia.summary(w_author, sentences=5)
        except (wikipedia.exceptions.DisambiguationError):
            return None

        # author_page = wikipedia.WikipediaPage(title=w_author)
        # author_photo = author_page.images[0]


        return author_bio


class PhotoSearcher(object):


    GOOGLE_IMAGES_API = 'https://www.google.com/search?site=&tbm=isch&q='

    CLASS_WITH_IMAGE = "//*[re:test(@class, 'rg_meta', 'i')]"
    RG_META = re.compile(r'<div\s+class=\"rg_meta\">(.*?)</div>')

    def __init__(self):
        self.tokenizer = TextProcessor()

    def get_photo(self, author):

        query = self._build_query_string(author)
        response = self._load_images(query)
        photo = self._find_first_image(response)
        # htree = self._parse_html(response)
        # photo = self._find_first_image(htree)

        return photo

    def _load_images(self, query):

        headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
        }

        req = urllib.request.Request(query, headers=headers)

        response = urllib.request.urlopen(req)
        encoding = response.headers.get_content_charset()
        response = response.read().decode(encoding)

        return response

    # def _parse_html(self, response):

    #     # инициализируем парсер
    #     hparser = etree.HTMLParser(encoding='utf-8')
    #     htree = etree.parse(io.StringIO(response), hparser)

    #     return htree

    def _find_first_image(self, htree):

        rg_meta_div = self.RG_META.search(htree).group(1)
        image_meta = json.loads(rg_meta_div)
        image_link = image_meta["ou"]

        # images_meta = htree.xpath(self.CLASS_WITH_IMAGE, namespaces={"re": "http://exslt.org/regular-expressions"})
        
        # first_image_node = json.loads(images_meta[0].text)

        # image_link = first_image_node["ou"]

        return image_link

    def _build_query_string(self, author):

        encoded_author = self.tokenizer.tokenize_for_api(author)

        query = '{url}"{author}"'.format(url=self.GOOGLE_IMAGES_API, author=encoded_author)

        return query



def get_author_info(author, language):

    bio_searcher = AuthorSearcher()
    photo_searcher = PhotoSearcher()
    author_bio = bio_searcher.find_author_in_wiki(author, language)
    photo = photo_searcher.get_photo(author)

    author_info = {

        'author_bio': author_bio,
        'photo': photo
    }

    return author_info
