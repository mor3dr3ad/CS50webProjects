from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    category = models.CharField(max_length=128)

class Listing(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length = 32)
    description = models.TextField()
    starting_bid = models.FloatField(default=0)
    URL = models.CharField(max_length=256)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="listings_in_category")
    active = models.BooleanField(default=True)
    current_price = models.FloatField(default=0)
    date = models.DateField()

    def __str__(self):
        return f"{self.title}, price {self.starting_bid}"

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="user_bids")
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bidder")
    bid = models.PositiveIntegerField()
    date = models.DateField()

    def __str__(self):
        return f"{self.listing.title}, {self.bid} from {self.username}"

class Comment(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments")
    comment = models.TextField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return f"Comment from {self.username}"

class Watchlist(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watched_items")
    listing = models.ManyToManyField(Listing, blank=True, related_name="watchlist")

    def __str__(self):
        return f"Watchlist from {self.username}"        




