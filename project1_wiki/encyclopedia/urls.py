from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<entry_title>", views.entry_page, name="entry_page"),
    path("search/", views.search, name="search"),
    path("create_page/", views.create_page, name="create_page"),
    path("random_page/", views.random_page, name="random_page"),
    path("edit_entry/", views.edit_entry, name="edit_entry"),
    path("save_page/", views.save_page, name="save_page")
    
    
]
