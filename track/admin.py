from django.contrib import admin
from .models import Status, Book

# class BookAdmin(admin.ModelAdmin):
# 	fieldsets = [
# 		(None, {'fields':['title']}),
# 		('Information about the book', {'fields': [
# 											'author', 'year', 'genre', 'language', 'date_pub', 'status'
# 											]
# 										}),
# 	]

admin.site.register(Status)
admin.site.register(Book)
