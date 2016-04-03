# -*- coding: utf-8 -*-
import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Settings(models.Model):

    books_amount = models.CharField(max_length=20, default=10)
    show_board = models.BooleanField(default=False)
    show_cover = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        settings = "{},{},{}".format(str(self.books_amount), str(self.show_board), str(self.show_cover))
        return settings


class Status(models.Model):

    status_text = models.CharField(max_length=100)

    def __str__(self):
        return self.status_text


class Language(models.Model):

    language = models.CharField(max_length=100)

    def __str__(self):
        return self.language


class Genre(models.Model):

    genre = models.CharField(max_length=100)

    def __str__(self):
        return self.genre


class Book(models.Model):
   
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    year = models.CharField(max_length=200)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    date_pub_created = models.DateTimeField('date published', editable=False, null=True)
    date_pub_modified = models.DateTimeField('date published')

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.date_pub_created = timezone.now()
        self.date_pub_modified = timezone.now()
        return super(Book, self).save(*args, **kwargs)

    def __str__(self):
        book_string = "{}, {}, {}, {}".format(self.title, self.author, self.genre, self.language)
        return book_string

