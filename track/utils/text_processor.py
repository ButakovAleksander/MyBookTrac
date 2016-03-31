# -*- coding: utf-8 -*-

import re
from urllib.parse import quote_plus

class TextProcessor(object):

    # знаки, которые будут удаляться в начале и конце токена
    PUNCTUATION = "∙!‼¡\"#£€$¥%&'()*+±×÷·,-./:;<=>?¿@[\]^ˆ¨_`—–­{|}’“”«»≫‘…¦"
    # для разбивки на токены по пробелам и слешам
    SPLITCHARS = re.compile(r'[\s\\\/\(\)\[\]\<\>\;\:\,\‚\—\?\!\|\"«»…#]|\.\.\.+|\-\-|\.[\'\"’“”«»‘′″„-]')

    def tokenize_for_api(self, string):

        tokens = (quote_plus(token.strip(self.PUNCTUATION), encoding='utf-8') 
                        for token in self.SPLITCHARS.split(string) 
                            if len(token) > 0
                    )

        return "+".join(tokens)

    def tokenize_string(self, string):

        tokens = [token.strip(self.PUNCTUATION).lower()
                        for token in self.SPLITCHARS.split(string) 
                            if len(token) > 0
                    ]

        return tokens


    