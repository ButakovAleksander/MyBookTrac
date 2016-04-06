# -*- coding: utf-8 -*-
import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

"""
DB structure:

Tables:

1. BOOK [id, title, author, year, language_id (FK), genre_id(FK), user_id (FK), status_id (FK), date_created, date_modified]
2. Status [id, status_text]
3. Language [id, language]
4. Genre [id, genre]
5. Settings [id, book_amount, show_board, show_cover, user (FK)]
6. User (default django table)

"""


class Settings(models.Model):

    """
    Class for making a table Settings in DB with a 'user' foreign key
    """

    books_amount = models.CharField(max_length=20, default=10)
    show_board = models.BooleanField(default=False)
    show_cover = models.BooleanField(default=False)
    # The table is connected with auth_user table
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        settings = "{},{},{}".format(str(self.books_amount), str(self.show_board), str(self.show_cover))
        return settings


class Status(models.Model):

    """
    Class for making a table Status in DB.
    So far five statuses are in the table:
    Book To Read, Currently Reading, Read, Archived, Deleted
    The table is populated with the help of '/utils/populate_database.py' script
    """

    status_text = models.CharField(max_length=100)

    def __str__(self):
        return self.status_text


class Language(models.Model):

    """
    Class for making a table Language in DB.
    So far 16 languages are in the table.
    To populate the table with other languages
    you may use this script '/utils/populate_database.py'
    """

    language = models.CharField(max_length=100)

    def __str__(self):
        return self.language


class Genre(models.Model):

    """
    Class for making a table Genre in DB.
    So far 16 genres are in the table.
    To populate the table with other genres
    you may use this script '/utils/populate_database.py'
    """

    genre = models.CharField(max_length=100)

    def __str__(self):
        return self.genre


class Book(models.Model):

    """
    The main table in DB.
    All the books and their properties are stored here.
    Fields 'year' and 'genre' can have null values as these
    parameters are not important for book processing
    """
   
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    year = models.CharField(max_length=200, null=True)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, null=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    date_pub_created = models.DateTimeField('date published', editable=False, null=True)
    date_pub_modified = models.DateTimeField('date published')

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''

        # if the book does not exist
        # add date_pub_created field
        # else: add date_pub_modified field
        if not self.id:
            self.date_pub_created = timezone.now()
        self.date_pub_modified = timezone.now()
        return super(Book, self).save(*args, **kwargs)

    def __str__(self):
        book_string = "{}, {}, {}, {}".format(self.title, self.author, self.genre, self.language)
        return book_string

