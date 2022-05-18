from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Auction(models.Model):

    # Each auction is associated to one user
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=300, blank=True)
    initial_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    current_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    category_choices = [('', 'Unspecified'), ('toys', 'Toys'), ('fashion', 'Fashion'),
                        ('electronics', 'Electronics'), ('books', 'Books'),
                        ('sports', 'Sports'), ('home', 'Home'), ('music', 'Music')]

    category = models.CharField(choices=category_choices, max_length=15, blank=True)
    image_url = models.URLField(blank=True, max_length=250)
    active = models.BooleanField(default=True)  # bids still allowed if True
    winner = models.ForeignKey(User, models.SET_NULL, blank=True, null=True, related_name='winner')


class Watchlist(models.Model):
    # Each item is associated to an item and a user
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')


class Bid(models.Model):
    # Each item is associated to an item and a user
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids', default="")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class Comment(models.Model):
    # Each item is associated to a user and an auction
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment', default="")
    date = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(max_length=300, default="")
