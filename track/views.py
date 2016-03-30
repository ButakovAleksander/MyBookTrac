# -*- coding: utf-8 -*-

import urllib.request

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import View
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import QueryDict
from django.contrib import auth
from django.contrib.auth.views import login
from django.db import IntegrityError

from .models import Status, Book, Language, Genre

from .utils.post_in_social_network import Recommender
from .utils.search_book_info import get_book_info
from .utils.search_for_author import get_author_info


class LogIn(View):

	def get(self, request, *args, **kwargs):
		if request.user.is_authenticated():
			return HttpResponseRedirect(reverse('track:index', 
												args=(request.user.id,)))

		else:
			template = 'track/login.html'
			return render(request, template)

	def post(self, request, *args, **kwargs):
		
		email = request.POST.get("email")
		password = request.POST.get("password")
		try:
			username = User.objects.get(email=email)
		except User.DoesNotExist:
			return HttpResponse("There is no user with this email")

		else:

			user = auth.authenticate(username=username, password=password)
			if user is not None:
				if user.is_active:
					auth.login(request, user)
					return HttpResponseRedirect(reverse('track:index', 
														args=(user.id,)))
				else:
					return HttpResponse("Your password is valid, but the account was disabled, \
											please contact administrator.")
			else:
				return HttpResponse("Password is incorrect.")


class SignUp(View):

	def get(self, request, *args, **kwargs):

		if request.user.is_authenticated():
			return HttpResponseRedirect(reverse('track:index', 
												args=(request.user.id,)))
		else:
			return render(request,'track/registration.html')

	def post(self, request, *args, **kwargs):

		username = request.POST.get("username")
		email = request.POST.get("email")
		password = request.POST.get("password")
		password2 = request.POST.get("password2")

		if password == password2:

			if email and User.objects.filter(email=email).exclude(username=username).count():
				return HttpResponse("User with this email already exists")

			else:

				try:
					user = User.objects.create_user(username=username, email=email, password=password)
				except IntegrityError:
					return HttpResponse("User with this name already exists")
				else:

					user.save()
					user = auth.authenticate(username=username, password=password)
					auth.login(request, user)

					return HttpResponseRedirect(reverse('track:index', 
													args=(user.id,)))
		else:
			return HttpResponse("Password confirmation is incorrect! Try again")


def logout(request):

	auth.logout(request)

	return HttpResponseRedirect(reverse('track:main'))
		

def landing_page(request):

	if request.user.is_authenticated():
		return HttpResponseRedirect(reverse('track:index', args=(request.user.id,)))

	else:
	
		template = 'track/main.html'
		return render(request, template)


def index(request, user_id):

	if int(user_id) != request.user.id:
		return HttpResponse("This user has forbidden to see his/her board. Return to your page.")
		
	else:
		
		template = 'track/base.html'
		try:
			user = User.objects.get(pk=user_id)
		except User.DoesNotExist:
			response = "User with an ID: {} is not found".format(user_id)
			return HttpResponse(response)

		else:
			books = user.book_set.all()
			status_list = Status.objects.all()
			
			books_list = {status:[] for status in status_list}
			
			for book in books:
				if book.status in status_list:
					books_list[book.status].append(book)

				else:
					response = "Can't find the status for book '{}'".format(book.title)
					return HttpResponse(response)


			# # removing Deleted column
			status_to_delete = Status.objects.all().filter(status_text="Deleted")[0]
			books_list.pop(status_to_delete)
			
			context = {'status_list': status_list,'books_list': books_list}
			return render(request, template, context)


class AddBook(View):

	def get(self, request, *args, **kwargs):
		# status = Status.objects.get(pk=status_id)
		language_list = Language.objects.all()
		genre_list = Genre.objects.all()
		template = 'track/add_book.html'
		context = {'language_list': language_list, 'genre_list': genre_list}
		return render(request, template, context)


	def post(self, request, status_id=1, *args, **kwargs):

		status = Status.objects.get(pk=status_id)

		title = request.POST['title']
		author = request.POST['author']
		year = request.POST['year']
		language_id = request.POST.get('language')

		genre_id = request.POST.get('genre')
		
		book = status.book_set.create(
										title=title, author=author, 
										year=year, language_id=language_id, 
										genre_id=genre_id, user_id=request.user.id
										)
		book.save()

		return HttpResponseRedirect(reverse('track:index', args=(request.user.id,)))

@csrf_exempt
def change_status(request):
    
	data = QueryDict(request.body)
	book_id_str = data['b_id']
	status_id_str = data['s_id']
	book_id = book_id_str[book_id_str.find('_')+1:]
	status_id = status_id_str[status_id_str.find('_')+1:]
    
	book = Book.objects.get(pk=book_id)
	book.status_id = status_id
	book.save()

	if int(book.status_id) == Status.objects.all().filter(status_text="Recommend To Friends")[0].id:

		message = 'I recommend the book "{0}" from {1}'.format(book.title, book.author)
		r = Recommender()
		r.post_to_vk(message)

	# #return HttpResponseRedirect(reverse('track:index'))
	return HttpResponse('')


def delete_book(request, book_id):

	book = Book.objects.get(pk=book_id)
	status_to_delete_id = Status.objects.all().filter(status_text="Deleted")[0].id
	book.status_id = status_to_delete_id
	book.save()

	return HttpResponseRedirect(reverse('track:index', args=(request.user.id,)))
	# return HttpResponse('')


def details(request, book_id):

	try:
		book = Book.objects.get(pk=book_id)
	except Book.DoesNotExist:
		# raise Http404("There is no such book in the database")
		response = "There is no such book in the database"
		return HttpResponse(response)
	else:
		template = 'track/book_info.html'

		language = Language.objects.get(pk=book.language_id).language

		book_info = get_book_info(book.title, book.author)

		author_info = get_author_info(book.author, language)
		
		context = {'book': book, 'book_info': book_info, 'author_info': author_info}

		return render(request, template, context)
