from django.contrib import admin

from .models import Listing, Watchlist, Bid, Comment, Category
# Register your models here.
admin.site.register(Listing)
admin.site.register(Category)
admin.site.register(Watchlist)
admin.site.register(Bid)
admin.site.register(Comment)
