# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import View
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import QueryDict
from django.contrib import auth
from django.db import IntegrityError

from .models import Status, Book, Language, Genre, Settings

from .utils.search_book_info import get_book_info
from .utils.search_for_author import get_author_info


class SignUp(View):

    """
    Class handling the process of user registration.

    With 'get' method it shows an html-template with
    a registration form.
    With 'post' method it receives user's credentials
    and stores them in auth_user table.
    """

    def get(self, request, *args, **kwargs):

        """ On response show a web-page with a registration form"""

        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('track:index',
                                                args=(request.user.id,)))
        else:
            return render(request, 'track/registration.html')

    def post(self, request, *args, **kwargs):

        """
        Get user's credentials.

        Check if email is unique.
        If unique, create a user with given credentials
        and redirect him/her to the board.

        """

        username = request.POST.get("username").strip()
        email = request.POST.get("email").strip()
        password = request.POST.get("password").strip()
        password2 = request.POST.get("password2").strip()

        if password == password2:

            if email and User.objects.filter(email=email).exclude(username=username).count():
                return HttpResponse("User with this email already exists")

            else:

                try:
                    user = User.objects.create_user(username=username, email=email, password=password)
                except IntegrityError:
                    return HttpResponse("User with this name already exists")
                except ValueError:
                    return HttpResponse("You should fill in all the fields in the registration form")
                else:

                    user.save()
                    user = auth.authenticate(username=username, password=password)

                    user.settings_set.create()
                    auth.login(request, user)

                    return HttpResponseRedirect(reverse('track:index',
                                                        args=(user.id,)))
        else:
            return HttpResponse("Password confirmation is incorrect! Try again")


class SignIn(View):

    """
    Class handling the process of user login.

    With 'get' method it shows a web-page with a login form.
    With 'post' method it receives user's credentials.
    If user exists (user's email in DB), authenticate him/her,
    check if user is active --> login user and redirect him/her
    to the board.
    """

    def get(self, request, *args, **kwargs):
        
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('track:index',
                                                args=(request.user.id,)))

        else:
            template = 'track/login.html'
            return render(request, template)

    def post(self, request, *args, **kwargs):

        email = request.POST.get("email").strip()
        password = request.POST.get("password").strip()
        
        try:
            username = User.objects.get(email=email)
        except User.DoesNotExist:
            return HttpResponse("User with this email does not exist")

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


def signout(request):

    """ 
    The function uses built-in django method
    to logout the user.
    After logging out it redirects to main page.

    """

    auth.logout(request)

    return HttpResponseRedirect(reverse('track:main'))


def landing_page(request):

    """
    The function shows the main web-page.
    If a user is authenticated, it redirects
    him/her to the books board.
    Otherwise it suggests to sign up/in.
    """

    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('track:index', args=(request.user.id,)))

    else:

        template = 'track/main.html'
        return render(request, template)


def index(request, user_id):

    """
    The function shows the books board.
    First it tries to load a user setting (show my board to others).
    Then it checks if the id of the user in session is not equal to
    the id of a requested board and if the setting is set to False,
    it restricts the user to see the board.
    Otherwise it shows the board.
    """

    try:
        sh_board = Settings.objects.get(user_id=user_id).show_board

    except Settings.DoesNotExist:

        response = "User with an ID: {} is not found".format(user_id)
        return HttpResponse(response)

    if int(user_id) != request.user.id and sh_board == False:

        return HttpResponse("This user has forbidden to see his/her board. Return to your page.")

    else:

        template = 'track/base.html'
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            response = "User with an ID: {} is not found".format(user_id)
            return HttpResponse(response)

        else:
            # getting user's books and statuses
            books = user.book_set.order_by('-date_pub_modified')
            status_list = Status.objects.all()

            # making an empty dictionary, where keys are statuses
            # and values are books
            books_list = {status: [] for status in status_list}

            # adding books to statuses according to
            # the status, assigned to each book.
            for book in books:
                if book.status in status_list:
                    books_list[book.status].append(book)

                else:
                    response = "Can't find the status for book '{}'".format(book.title)
                    return HttpResponse(response)

            # removing Deleted column,
            # in order not to show it on the board
            status_to_delete = Status.objects.all().filter(status_text="Deleted")[0]
            books_list.pop(status_to_delete)

            context = {'status_list': status_list, 'books_list': books_list, 'user_id': int(user_id)}

            return render(request, template, context)


class AddBook(View):

    """
    Class handling the process of adding a new book
    to the DB.
    The 'get' method shows the form for adding a book.
    The 'post' method get book data from form fields
    and inserts it into the DB and redirects to the board
    where the added book appears in the Books To Read column.

    """

    def get(self, request, *args, **kwargs):

        # select all languages from Language table
        language_list = Language.objects.all()
        # select all genres from Genre table
        genre_list = Genre.objects.all()

        template = 'track/add_book.html'
        context = {'language_list': language_list, 'genre_list': genre_list}

        return render(request, template, context)

    def post(self, request, status_id=1, *args, **kwargs):

        # setting status_id to 1 since we can add books
        # only with the status 'Books To Read'.
        status = Status.objects.get(pk=status_id)

        title = request.POST['title'].strip()
        author = request.POST['author'].strip()
        year = request.POST['year'].strip()
        language_id = request.POST.get('language')
        genre_id = request.POST.get('genre')

        book = status.book_set.create(
            title=title, author=author,
            year=year, language_id=language_id,
            genre_id=genre_id, user_id=request.user.id
        )
        book.save()

        return HttpResponseRedirect(reverse('track:index', args=(request.user.id,)))


class BoardSettings(View):

    """
    Class handles the process of setting and changing
    user settings. During a new user creation these settings
    are added by default. Later a user can change them.

    So far only one setting is configurable - show board to others.
    """

    def get(self, request, *args, **kwargs):

        template = 'track/board_settings.html'
        bks_amount = Settings.objects.get(user_id=request.user.id).books_amount
        sh_board = Settings.objects.get(user_id=request.user.id).show_board
        sh_cover = Settings.objects.get(user_id=request.user.id).show_cover

        
        # showing some statistics about genres
        # in the user profile.
        if request.user.book_set.all():
            genres = Genre.objects.all()

            fav_genres = []

            for genre in genres:
                g_count = request.user.book_set.filter(genre__genre="{}".format(genre)).count()
                fav_genres.append((genre, g_count))

            fav_genres_sorted = sorted(((g, c) for g, c in fav_genres), key=lambda g: g[1], reverse=True)
            fav_genres = [(gen, count) for gen, count in fav_genres_sorted if count > 1][:3]
        else:
            fav_genres = []


        context = {
            'books_amount': bks_amount, 'show_board': sh_board,
            'show_cover': sh_cover, 'fav_genres': fav_genres
        }

        return render(request, template, context)

    def post(self, request, *args, **kwargs):

        if request.method == "POST":
            setting = Settings.objects.get(user_id=request.user.id)

            # books_amount = request.POST.get("books_amount")
            # setting.books_amount = books_amount

            if request.POST.get('show_board'):
                setting.show_board = True
            else:
                setting.show_board = False

            if request.POST.get('show_cover'):
                setting.show_cover = True
            else:
                setting.show_cover = False

            setting.save()

        return HttpResponseRedirect(reverse('track:change_settings', args=(request.user.id,)))


@csrf_exempt
def change_status(request):

    """ 
    The function updates a book's status
    via handling ajax requests.
    """

    data = QueryDict(request.body)
    print('STATUS: ', data['s_id'])
    print('BOOK: ', data['b_id'])
    book_id_str = data['b_id']
    status_id_str = data['s_id']
    book_id = book_id_str[book_id_str.find('_') + 1:]
    status_id = status_id_str[status_id_str.find('_') + 1:]

    book = Book.objects.get(pk=book_id)
    book.status_id = status_id
    book.save()

    return HttpResponse('')


def delete_book(request, book_id):

    """
    The function deletes the book from the board.
    In essence, it just sets the book status to 'Deleted'
    and later the book is filtered out 
    from being shown on the board.
    The book is still in the DB.
    """

    book = Book.objects.get(pk=book_id)
    status_to_delete_id = Status.objects.all().filter(status_text="Deleted")[0].id
    book.status_id = status_to_delete_id
    book.save()

    return HttpResponseRedirect(reverse('track:index', args=(request.user.id,)))


def details(request, book_id):

    """
    The function shows a page with detailed book info.
    First of all it loads info from the table 
    (title, author, language, etc),
    then it tries to find additional info in 
    Google Books (book description),
    Google Images (author image),
    Wikipedia (author bio)
    by sending API requests
    """
    try:
        book = Book.objects.get(pk=book_id)
    except Book.DoesNotExist:
        response = "There is no such book in the database"
        return HttpResponse(response)
    else:
        template = 'track/book_info.html'

        language = Language.objects.get(pk=book.language_id).language

        book_info = get_book_info(book.title, book.author)

        author_info = get_author_info(book.author, language)

        context = {'book': book, 'book_info': book_info, 'author_info': author_info}

        return render(request, template, context)
