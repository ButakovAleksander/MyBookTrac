#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "booktrack.settings")
django.setup()
from track.models import Status, Book, Language, Genre, Settings

class DBPopulator(object):

    LANGUAGES = (
        'Russian', 'English', 'German',
        'French', 'Spanish', 'Italian',
        'Polish', 'Dutch', 'Arabic',
        'Portuguese', 'Chinese', 'Hindi/Urdu',
        'Japanese', 'Bengali', 'Korean', 'Finnish'
    )

    GENRES = (
        'Detective', 'Novel', 'Non-fiction',
        'PopSci', 'War Novel', 'Philosophical Novel',
        'Fantasy', 'Epos', 'Documentary', 'History',
        'Memoir', 'Education', 'Biography', 'Comics',
        'Cookbooks', 'Poetry'
    )

    STATUSES = (
        'Books To REad',
        'Currently Reading',
        'Read',
        'Archived',
        'Deleted'
    )

    def populate(self, param):

        if param == 'Language':
            for lang in self.LANGUAGES:
                self._add_language(lang)

        elif param == 'Genre':
            for genre in self.GENRES:
                self._add_genre(genre)

        elif param == 'Status':
            for status in self.STATUSES:
                self._add_status(status)

        # # # just printing what've been added
        # for l in Language.objects.all():
        # 	print('language added: {}'.format(str(l)))

    @staticmethod
    def _add_language(lang_name):
        '''
        Создаем объект language, из-за get_or_create он является tuple (object, created).
        Берем 0 элемент object. Передаем ему название языка и сохраняем.
        '''

        language = Language.objects.get_or_create(language=lang_name)[0]
        language.save()

        return language

    @staticmethod
    def _add_genre(genre_name):
        genre = Genre.objects.get_or_create(genre=genre_name)[0]
        genre.save()

        return genre

    @staticmethod
    def _add_status(status_name):
        status = Status.objects.get_or_create(status_text=status_name)[0]
        status.save()

        return status


if __name__ == '__main__':
    print("Starting SQLITE3 population script...")
    populator = DBPopulator()
    populator.populate('Language')
