from django.forms import ModelForm
from .models import User, Auction, Bid, Comment


class AuctionForm(ModelForm):
    class Meta:
        model = Auction
        fields = ['title', 'description', 'initial_price', 'category', 'image_url']


class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']