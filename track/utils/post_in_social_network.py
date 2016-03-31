# -*- coding: utf-8 -*-

import urllib.request
from urllib.parse import urlencode


class Recommender(object):

    VK_API_WALL_POST = '''https://api.vk.com/method/wall.post?'''
    ACCESS_TOKEN = ''
    OWNER_ID = ''
    V = '5.50'

    def __init__(self):
        pass

    def post_to_vk(self, message):

        parameters_list = [('access_token', self.ACCESS_TOKEN),
                            ('owner_id', self.OWNER_ID),
                            ('message', message),
                            ('v', self.V)
                            ]
        
        encoded_query = self.encode_url(parameters_list)
        binary_query = encoded_query.encode('utf-8')

        request = urllib.request.urlopen(self.VK_API_WALL_POST, data=binary_query)

    def encode_url(self, q_list):

        encoded_query = urlencode(q_list, doseq=True)

        return encoded_query