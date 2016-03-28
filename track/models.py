# -*- coding: utf-8 -*-
import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


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
    date_pub = models.DateTimeField('date published', auto_now=True)

    def __str__(self):
        book_string = "{}, {}, {}, {}".format(self.title, self.author, self.genre, self.language)
        return book_string

    def was_added_recently(self):
        return self.date_pub >= timezone.now() - datetime.timedelta(days=1)
