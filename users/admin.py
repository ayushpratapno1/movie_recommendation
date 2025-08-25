from django.contrib import admin
from .models import UserProfile, Rating, Watchlist, UserInteraction

admin.site.register(UserProfile)
admin.site.register(Rating)
admin.site.register(Watchlist)
admin.site.register(UserInteraction)
