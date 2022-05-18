from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .forms import AuctionForm, BidForm, CommentForm
from .models import User, Auction, Watchlist, Bid, Comment


def index(request):

    # get all active listings and display them
    auctions = Auction.objects.filter(active=True)

    return render(request, "auctions/index.html", {
        "auctions": auctions
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def display_listing(request, listing_pk):

    # Load model associated to listing
    auction = Auction.objects.get(pk=listing_pk)

    # get highest bid for this listing
    highest_bid = Bid.objects.filter(auction=auction.id).order_by('-amount').first()

    # handle watchlist elements, check if user is seller
    if request.user.is_authenticated:
        watchlist_item = Watchlist.objects.filter(
                        auction=auction.id,
                        user=User.objects.get(id=request.user.id)).first()

        if watchlist_item:
            on_watch = True
        else:
            on_watch = False

        if request.user.id == auction.seller.id:
            is_seller = True
        else:
            is_seller = False

    else:
        on_watch = False
        is_seller = False

    # check if auction is active and check winner
    if auction.active is False and auction.winner:
        if request.user.is_authenticated:
            if auction.winner.id == request.user.id:
                is_winner = True
            else:
                is_winner = False
        else:
            is_winner = False
    else:
        is_winner = False

    bid_form = BidForm()

    # handle comments
    comments = Comment.objects.filter(auction=listing_pk)

    comment_form = CommentForm()

    return render(request, "auctions/display_listing.html", {
            "auction": auction,
            "is_seller": is_seller,
            "on_watch": on_watch,
            "is_winner": is_winner,
            "bid_form": bid_form,
            "comments": comments,
            "comment_form": comment_form
    })


def categories(request):
    # display all categories, link redirects to active listings in the category
    categories = [c[1] for c in Auction.category.field.choices]
    categories.sort()
    return render(request, 'auctions/categories.html', {
        'categories': categories
    })


def category(request, category):
    # display listings in that category
    # Filter auctions

    if category == 'Unspecified':
        auctions = Auction.objects.filter(category='', active=True)
    else:
        auctions = Auction.objects.filter(category=category.lower(), active=True)
    return render(request, 'auctions/category.html', {
        'category': category,
        'auctions': auctions
    })


@login_required(login_url="login")
def add_listing(request):

    if request.method == 'POST':
        form = AuctionForm(request.POST)

        if form.is_valid():

            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            category = form.cleaned_data["category"]
            initial_price = form.cleaned_data["initial_price"]
            current_price = initial_price
            image_url = form.cleaned_data["image_url"]

            # Save a record
            auction = Auction(
                seller=User.objects.get(pk=request.user.id),
                title=title,
                description=description,
                category=category,
                initial_price=initial_price,
                current_price=current_price,
                image_url=image_url
            )
            auction.save()

            return redirect("listings/%i"%auction.pk)
                # display_listing(request, listing_pk=auction.pk)
        else:
            # If the form is invalid, re-render the page with existing information.
            return render(request, "auctions/add_listing.html", {
                "form": form
            })

    return render(request, "auctions/add_listing.html", {
        'form': AuctionForm()
    })


@login_required(login_url="login")
def place_bid(request, listing_pk):

    if request.method == 'POST':
        # get data from form
        form = BidForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]
            auction = Auction.objects.get(pk=listing_pk)
            # first bid has to be > than current highest bid
            highest_bid = Bid.objects.filter(auction=auction.id).order_by('-amount').first()
            if (highest_bid and amount > highest_bid.amount) or (
                 not highest_bid and amount >= auction.initial_price):
                # Save
                bid = Bid(
                         user=request.user,
                         auction=auction,
                         amount=amount)
                bid.save()

                # update price of item
                auction.current_price = amount
                auction.save()

                # Bid placed successfully
                return display_listing(request, listing_pk) # should display updated price

            elif (highest_bid and amount <= highest_bid.amount) or (
                  not highest_bid and amount <= auction.initial_price):

                # display error that bid is not valid
                return HttpResponse("Error -- increase the amount of your bid.")



@login_required(login_url="login")
def place_comment(request, listing_pk):

    if request.method == 'POST':
        # get data from form
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.cleaned_data["comment"]
            auction = Auction.objects.get(pk=listing_pk)

           # save comment
            new_comment = Comment(user=request.user,
                                  auction=auction,
                                  comment=comment)
            new_comment.save()

            return display_listing(request, listing_pk) # should display updated comments


@login_required(login_url="login")
# to be finished, button doesn't work to close auction
def close_listing(request, listing_pk):

    if request.method == "POST":
        # get auction and close it
        auction = Auction.objects.get(pk=listing_pk)
        auction.active = False

        # Get winner
        highest_bid = Bid.objects.filter(auction=auction.id).order_by('-amount').first()
        if highest_bid:
            auction.winner = highest_bid.user
            auction.save()
        else:
            auction.winner = None
            auction.save()

        return display_listing(request, listing_pk=listing_pk)


@login_required(login_url="login")
# to be finished, button doesn't work
def watch(request, listing_pk):

    if request.method == "POST":

        # if element in watchlist, remove it. Else, add it
        watchlist_item = Watchlist.objects.filter(
                         auction=Auction.objects.get(pk=listing_pk),
                         user=User.objects.get(id=request.user.id)).first()

        if watchlist_item:
            watchlist_item.delete()
        else:
            watchlist_item = Watchlist(
                                user=User.objects.get(id=request.user.id),
                                auction=Auction.objects.get(id=listing_pk))
            watchlist_item.save()

        return display_listing(request, listing_pk=listing_pk)


@login_required(login_url="login")
def watchlist(request):

    # Get all elements in the user's watchlist
    watchlist_items = Watchlist.objects.filter(
                         user=User.objects.get(id=request.user.id))

    return render(request, 'auctions/watchlist.html', {
                    'watchlist_items': watchlist_items
        })
