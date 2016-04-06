# -*- coding: utf-8 -*-

import re
from urllib.parse import quote_plus

class TextProcessor(object):

    """
    Class for splitting text into tokens (words)
    Used in InfoSearcher and AuthorSearcher to insert
    author name and title into an API request.
    """

    # punct. signs to be stripped off a token.
    PUNCTUATION = "∙!‼¡\"#£€$¥%&'()*+±×÷·,-./:;<=>?¿@[\]^ˆ¨_`—–­{|}’“”«»≫‘…¦"
    # for splitting a string to tokens by whitespaces and slashes
    SPLITCHARS = re.compile(r'[\s\\\/\(\)\[\]\<\>\;\:\,\‚\—\?\!\|\"«»…#]|\.\.\.+|\-\-|\.[\'\"’“”«»‘′″„-]')

    def tokenize_for_api(self, string):

        """ split the string and join tokens with '+' sign for API """

        tokens = (quote_plus(token.strip(self.PUNCTUATION), encoding='utf-8') 
                        for token in self.SPLITCHARS.split(string) 
                            if len(token) > 0
                    )

        return "+".join(tokens)

    def tokenize_string(self, string):

        """ split the string and return a list of tokens """

        tokens = [token.strip(self.PUNCTUATION).lower()
                        for token in self.SPLITCHARS.split(string) 
                            if len(token) > 0
                    ]

        return tokens


    