from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("add", views.add_listing, name="add_listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("listings/<int:listing_pk>", views.display_listing, name="listing"),
    path("listings/<int:listing_pk>/close", views.close_listing, name="close_listing"),
    path("listings/<int:listing_pk>/bid", views.place_bid, name="place_bid"),
    path("listings/<int:listing_pk>/comment", views.place_comment, name="place_comment"),
    path("listings/<int:listing_pk>/watch", views.watch, name="watch"),
    path("categories", views.categories, name='categories'),
    path("categories/<str:category>", views.category, name='category')
]
