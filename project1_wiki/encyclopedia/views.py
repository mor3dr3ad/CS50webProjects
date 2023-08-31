from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
import markdown2
import random

from . import util

class NewPageForm(forms.Form):
    newTitle = forms.CharField(required=True, label="Title", widget=forms.TextInput(attrs={"placeholder":"Title", "class":"mb-4"}))
    newPage = forms.CharField(required=True, label="Content", widget=forms.Textarea(attrs={"placeholder":"Content", "class":"form-control mb-4", "id":"content"}))

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def search(request):
    #strip the query which is of the form search?q=asdf
    query = request.GET.get("q", "")

    #get valid entries in encyclopedia
    entries = util.list_entries()
    search_results = [entry for entry in entries if query.lower() in entry.lower()]

    #search logic
    if query is None or query == "":
        return render(request, "encyclopedia/search.html", {
            "query":"", "search_results":""
            })

    #first check if there is a full result
    if len(search_results) == 1:
        return entry_page(request, search_results[0])

    #return list of matching entries
    return render(request, "encyclopedia/search.html", {
        "query":query, "search_results":search_results
    })


def entry_page(request, entry_title):

    entry_content= util.get_entry(entry_title)
    #get entry_page with get_entry, and save to file in markdown
    if entry_content:
        entry_content = markdown2.markdown(entry_content)
    else:
        return render(request, "encyclopedia/404.html", status=404)

    return render(request, "encyclopedia/entry_page.html", {
        "entry_title":entry_title,
        "entry_content":entry_content
    })

def create_page(request):
    if request.method == 'GET':
        return render(request, "encyclopedia/create_page.html", {
            "form":NewPageForm()
        } )

    if request.method == 'POST':
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['newTitle']
            content = form.cleaned_data['newPage']

            if title.lower() in [entry.lower() for entry in util.list_entries()]:
                #return warning message
                messages.add_message(
                    request,
                    messages.WARNING,
                    message=f'Entry "{title}" already exists',
                )
                #return original create_page with user form as input
                return render(request, "encyclopedia/create_page.html", {
                     "form":form 
                })
            else:
            #save file
                with open(f"entries/{title}.md", mode='w') as f:
                    f.write("#"+title)
                    f.write('\n\n')
                    f.write(content)
                return entry_page(request, title)

        return render(request, "encyclopedia/create_page.html", {
            "form":form
        })

def edit_entry(request):
    if request.method == 'POST':
        entry_title = request.POST.get('edit_entry')
        #populate form with data from entry_page
        content = util.get_entry(entry_title)
        form = NewPageForm(initial={"newTitle":entry_title, "newPage":content})
        print(form)


        #pass form to edit_entry
        return render(request, "encyclopedia/edit_entry.html", {
            "entry_title":entry_title, "form":form
        })

    return render(request, "encyclopedia/404.html", status=404)

def save_page(request):

    form = NewPageForm(request.POST)
    if form.is_valid():
        print(form)
        title = form.cleaned_data['newTitle']
        content = form.cleaned_data['newPage']
        util.save_entry(title, content)
        return entry_page(request, title) 




def random_page(request):
    entries = util.list_entries()
    random_entry = random.choice(entries)
    return entry_page(request, random_entry)

