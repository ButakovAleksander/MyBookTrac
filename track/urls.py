from django.conf.urls import url

from . import views
from track.views import AddBook, LogIn, SignUp, BoardSettings

app_name = 'track'
urlpatterns = [
	url(r'^$', views.landing_page, name='main'),
	url(r'^login/$', LogIn.as_view(), name='login'),
	url(r'^logout/$', views.logout, name='logout'),
	url(r'^register/$', SignUp.as_view(), name='register'),
    url(r'^user/(?P<user_id>[0-9]+)/$', views.index, name='index'),
    url(r'^add/$', AddBook.as_view(), name='create_book'),
    url(r'^user/(?P<user_id>[0-9]+)/board_settings/$', BoardSettings.as_view(), name='change_settings'),
    url(r'^change_status/$', views.change_status, name='change_status'),
    url(r'^delete_book/(?P<book_id>[0-9]+)/$', views.delete_book, name='delete_book'),
    # url(r'^change_status/(?P<book_id>[0-9]+)$', views.change_status, name='change_status'),
    # url(r'^(?P<status_id>[0-9]+)/$', views.detail, name='detail'),
    # url(r'^add/$', views.add, name='add'),
    url(r'^(?P<book_id>[0-9]+)/about/$', views.details, name='details')
]