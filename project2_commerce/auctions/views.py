from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.timezone import datetime
from django.db.models import Max

from .models import *

class CreateForm(forms.Form):
    title = forms.CharField(required=True, widget=forms.TextInput(attrs={"placeholder":"title", "class":"form-control mb-4"}))
    description = forms.CharField(required=True, widget=forms.Textarea(attrs={"placeholder":"description", "class":"form-control mb-4"}) )
    URL = forms.CharField(required=False, widget=forms.TextInput(attrs={"placeholder":"url", "class":"form-control mb-4"}))
    starting_price = forms.IntegerField(required=True, label="Starting Price", widget=forms.NumberInput(attrs={"placeholder":"starting price", "class":"form-control mb-4"}) )
    def __init__(self, *args, **kwargs):
        super(CreateForm, self).__init__(*args, **kwargs)
        self.fields['category'] = forms.ChoiceField(choices=[(value['id'], value['category']) for value in Category.objects.all().values()])

def index(request):
    return render(request, "auctions/index.html", {
        "listings":Listing.objects.all()
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

@login_required(login_url="login")
def create(request):
    if request.method=="GET":
        form = CreateForm()
        #categories = Category.objects.all()
        return render(request, "auctions/create.html", {
            "form":form 
            })
    if request.method=="POST":
        user = User.objects.get(username=request.user.username)
        form = CreateForm(request.POST)
        if form.is_valid():
            print("valid")
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            URL = form.cleaned_data['URL'] 
            starting_price = form.cleaned_data['starting_price'] 
            category = form.cleaned_data['category']
            listing = Listing(username = user, title=title, description=description, starting_bid=starting_price, URL=URL, date=datetime.today(), category=Category.objects.get(pk=category))
            listing.save()
            messages.add_message(request, messages.SUCCESS, f"Your listing {listing.title} has been successfully published" )
            return HttpResponseRedirect(reverse("listing", args=(listing.id,)))

@login_required(login_url="login")
def listing(request, id):
    #get current user: TODO what if no one is logged in? 
    user = User.objects.get(username=request.user.username)
    try:
        listing = Listing.objects.get(id=id)
    except:
        return render(request, "auctions/404.html", { 
            "message":"Ooooops - this listing does not exist."
        })
    
    is_active = listing.active
    is_owner = listing.username==user
    on_watchlist = bool(Watchlist.objects.filter(username=user, listing=listing)) 
    comments = Comment.objects.filter(listing=listing)

    try:
        highest_bid = Bid.objects.get(bid=Bid.objects.filter(listing=listing).aggregate(Max('bid'))['bid__max'])
    except:
        highest_bid = 0
    
    bidders = listing.user_bids.values("username").distinct()
    active_bidders = []
    for bidder in bidders:
        active_bidders.append(User.objects.get(id=bidder['username']))




    return render(request, "auctions/listing.html", {
        "listing":listing,
        "bidders":active_bidders,
        "is_active":is_active,
        "is_owner":is_owner,
        "on_watchlist":on_watchlist,
        "highest_bid":highest_bid,
        "comments":comments
    })


@login_required(login_url="login")
def category(request, category):
    category = Listing.objects.filter(category="")
    pass


@login_required(login_url="login")
def watchlist(request):
    watchlist = Watchlist.objects.get(username=User.objects.get(username=request.user.username))
    return render(request, "auctions/watchlist.html", {
        "watchlist":watchlist.listing.all()
    })

@login_required(login_url="login")
def add_watchlist(request, id):
    if request.method=="POST":
        listing = Listing.objects.get(pk=id)
        user = User.objects.get(username=request.user.username)
        try:
            watchlist = Watchlist.objects.get(username=user)
        except:
            watchlist = Watchlist()
            watchlist.username = user 
            watchlist.save()
        on_watchlist = bool(Watchlist.objects.filter(username=user, listing=listing))
        if on_watchlist:
            watchlist.listing.remove(listing)
        else:
            watchlist.listing.add(listing)
        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))

@login_required(login_url="login")
def submit_bid(request, id):
    if request.method=="POST":
        user = User.objects.get(username=request.user.username)
        listing = Listing.objects.get(pk=id)
        bid = float(request.POST.get("bid"))
        if bid > listing.current_price:
            listing.current_price = bid
            listing.save()
            new_bid = Bid(username=user, listing=listing, bid=bid, date=datetime.today())
            new_bid.save()
            messages.add_message(request, messages.SUCCESS, f"Your bid of {bid} has been successfully placed")
            return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
        messages.add_message(request, messages.ERROR, f"Your bid must be higher than {listing.current_price}")
        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))

            
@login_required(login_url="login")
def close_bid(request, id):
    if request.method=="POST":
        listing = Listing.objects.get(pk=id)
        listing.active=False
        #set winner?
        listing.save()
        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))

@login_required(login_url="login")
def reopen_bid(request, id):
    if request.method=="POST":
        listing = Listing.objects.get(pk=id)
        listing.active=True
        #unset winner?
        listing.save()
        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
        

@login_required(login_url="login")
def comment(request, id):
    if request.method=="POST":
        listing = Listing.objects.get(pk=id)
        user = User.objects.get(username=request.user.username)
        new_comment = Comment(username=user, date=datetime.today(), listing=listing, comment=request.POST['comment'])
        if new_comment.comment == "":
            messages.add_message(request, messages.ERROR, "Your comment is empty!")
            return HttpResponseRedirect(reverse("listing", args=(id,)))
        new_comment.save()
        messages.add_message(request, messages.SUCCESS,  f"Your comment has been published!", extra_tags="comment",)
        return HttpResponseRedirect(reverse("listing", args=(id,)))

@login_required(login_url="login")
def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories":categories
    }
    )

@login_required(login_url="login")
def category(request, id):
    category = Category.objects.get(pk=id)
    listings = category.listings_in_category.all()
    return render(request, "auctions/category.html", {
        "listings":listings, "category":category
    })


#@login_required(login_url="login")
#def edit(request,id):
#    if request.method=="GET":
#        listing = Listing.objects.get(pk=id)
#        form = CreateForm(initial={
#            "title":listing.title,
#            "description":listing.description,
#            "category":listing.category,
#            "URL":listing.URL,
#            "starting_price":listing.starting_bid})
#        return render(request, "auctions/edit.html", {
#                "form":form
#            })