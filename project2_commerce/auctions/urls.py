from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("<int:id>/add_watchlist", views.add_watchlist, name="add_watchlist"),
    path("<int:id>/bid", views.submit_bid, name="submit_bid"),
    path("<int:id>/close_bid", views.close_bid, name="close_bid"),
    path("<int:id>/reopen_bid", views.reopen_bid, name="reopen_bid"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("<int:id>/comment", views.comment, name="comment"),
    path("create", views.create, name="create"),
    path("categories", views.categories, name="categories"),
    path("category/<int:id>", views.category, name="category")
    #path("<int:id>/edit", views.edit, name="edit")

]
