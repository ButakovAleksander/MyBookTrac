#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "booktrack.settings")

import django
django.setup()

from track.models import Status, Book, Language, Genre

def populate():

    LANGUAGES = (
        'Russian',
        'English',
        'German',
        'French',
        'Spanish',
        'Italian',
        'Arabic'
    )

    GENRES = (
        'Detective',
        'Novel',
        'Non-fiction',
        'PopSci',
        'War Novel',
        'Philosophical Novel'
    )

    # for lang in LANGUAGES:
    # 	add_language(lang)

    for genre in GENRES:
    	add_genre(genre)

    # # just printing what've been added
    # for l in Language.objects.all():
    # 	print('language added: {}'.format(str(l)))

    # just printing what've been added
    for g in Genre.objects.all():
    	print('Genre added: {}'.format(str(g)))


def add_language(lang_name):

	'''
	Создаем объект language, из-за get_or_create он является tuple (object, created). 
	Берем 0 элемент object. Передаем ему название языка и сохраняем.
	'''

	language = Language.objects.get_or_create(language=lang_name)[0]
	language.save()

	return language


def add_genre(genre_name):

	genre = Genre.objects.get_or_create(genre=genre_name)[0]
	genre.save()

	return genre


if __name__ == '__main__':
    print("Starting SQLITE3 population script...")
    populate()