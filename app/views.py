from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db import connection
import sys
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth import hashers
from django.core import serializers
if sys.version_info[0] < 3:
    import xmlrpclib
else:
    from xmlrpc import client as xmlrpclib
import json
import datetime
import time 
time.strftime('%Y-%m-%d %H:%M:%S')
from .forms import SupplierForm, SearchDrinkForm, ConsumerForm, LoginForm, RecipeForm, ReviewForm, OrderHistoryForm

def login_required(f):
    def wrap(request, *args, **kwargs):
        # try authenticating the user
        if request.session.get('uname', None) == None:
            messages.error(request, "Must login to lazychef.")
            return HttpResponseRedirect(reverse('login'))
        return f(request, *args, **kwargs)
    return wrap

@login_required
def logout(request):
    context = {}
    if request.session.get('uname', None) != None:
        del request.session["uname"]
        request.session.modified = True
        messages.success(request, 'Successfully logged out')
    else:
        messages.error(request, 'Cannot logout if you are not logged in')
    return HttpResponseRedirect(reverse('login'))

def login(request):
    # if logged in redirect to home
    if request.session.get('uname', None) != None:
        return HttpResponseRedirect(reverse('index'))
    cursor = connection.cursor()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = [username, password]
            print("Login attempted: ", user)
            cursor.execute("SELECT * FROM consumer WHERE c_username = %s AND c_password=%s", user)
            query = dictfetchall(cursor)
            if query:
                dat_user = query[0]
                request.session["uname"] = dat_user['c_username']
                request.session["name"] = dat_user['c_name']
                messages.success(request, 'Successfully logged in')
                return HttpResponseRedirect(reverse('index'))
            messages.error(request, 'Incorrect username/password')
            return HttpResponseRedirect(reverse('login'))
            '''query = cursor.fetchone()
            if query:
                query = query[0]
                if hashers.check_password(password, query):
                    request.session["uname"] = username
                    messages.success(request, 'Successfully logged in')
                    return HttpResponseRedirect(reverse('index'))'''
        else:
            messages.error(request, 'Must fill out all fields')
    form = LoginForm()
    context = {'form': form}
    return render(request, 'login.html', context)

def consumerRegister(request):
    # if logged in redirect to home
    if request.session.get('uname', None) != None:
        return HttpResponseRedirect(reverse('index'))
    cursor = connection.cursor()
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        form = ConsumerForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            name = form.cleaned_data['name'] 
            password = form.cleaned_data['password'] 
            confirm_password = form.cleaned_data['confirm_password'] 
           # c_id_iterator = c_id_iterator + 1
            with connection.cursor() as cursor:
                cursor.execute("SELECT c_username FROM consumer WHERE c_username = %s", [username])
                data = cursor.fetchall()
                if len(data) > 0:
                    messages.error(request, "Username is already taken.")
                    return HttpResponseRedirect(reverse('consumer-register'))
                if password != confirm_password:
                    messages.error(request, "Password doesn't match confirm password.")
                    return HttpResponseRedirect(reverse('consumer-register'))
                consumer = [name, username, password, datetime.datetime.now()]
                cursor.execute("INSERT INTO consumer(c_name, c_username, c_password, c_join_date) \
                VALUES (%s, %s, %s, %s)", consumer)
            messages.success(request, 'Successfully registered!')
            return HttpResponseRedirect(reverse('login'))
        else:
            messages.error(request, 'Must fill out all fields')
    form = ConsumerForm()
    context = {'form': form}
    return render(request, 'consumerRegister.html', context)

@login_required
def removeFromFavorites(request, d_id):
    cursor = connection.cursor()
    drink_id = d_id
    c_uname = request.session.get('uname', None)
    with connection.cursor() as cursor:
        cursor.execute("SELECT c_username, d_id FROM favorites WHERE c_username = %s AND d_id = %s", [c_uname,drink_id])
        data = cursor.fetchall()
        if len(data) == 0:
            messages.error(request, "This drink is not in your favorites.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        cursor.execute("DELETE FROM favorites where c_username=%s AND d_id=%s", [c_uname,drink_id])
    messages.success(request, 'Successfully deleted favorite!')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
@login_required
def addToFavorites(request, d_id):
    cursor = connection.cursor()
    drink_id = d_id
    c_username = request.session.get('uname', None)
    with connection.cursor() as cursor:
        cursor.execute("SELECT c_username, d_id FROM favorites WHERE c_username = %s AND d_id = %s", [c_username,drink_id])
        data = cursor.fetchall()
        if len(data) > 0:
            messages.success(request, "This drink is already in your favorites.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        fav = [c_username, d_id]
        cursor.execute("INSERT INTO favorites (c_username, d_id) VALUES (%s, %s)", fav)
    messages.success(request, 'Successfully added favorite!')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
@login_required
def search_drinks(request):
    form=[]
    query=[]
    if request.method == 'POST':
        form = SearchDrinkForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search_string']
            print(search)
            with connection.cursor() as cursor:
                cursor.execute("select * \
                from facebooze.drink natural join facebooze.producer \
                WHERE MATCH (d_name) AGAINST (%s IN NATURAL LANGUAGE MODE) \
                or MATCH (p_location) AGAINST (%s IN NATURAL LANGUAGE MODE) \
                or MATCH (p_name) AGAINST (%s IN NATURAL LANGUAGE MODE);" \
                ,[search,search,search])
                query = dictfetchall(cursor)
    else:
        form = SearchDrinkForm()
        with connection.cursor() as cursor:
            cursor.execute("select d_id,d_name,p_name \
            from facebooze.drink natural join facebooze.producer")
            query = dictfetchall(cursor)
    context = {'query': query, 'form': form}
    return render(request, 'searchResults.html', context)
@login_required
def index(request):
    cursor = connection.cursor()
    query=[]
    with connection.cursor() as cursor:
        cursor.execute("select * from \
        (facebooze.consumer natural join facebooze.favorites \
        natural join facebooze.drink natural join facebooze.producer) \
        where c_username=%s", [request.session.get("uname", None)])
        query = dictfetchall(cursor)
    context = {'query': query}
    return render(request, 'index.html', context)

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]
@login_required
def viewProfile(request):
    cursor = connection.cursor()
    query = []
    with connection.cursor() as cursor:
        sess_user = request.session.get('uname', None)
        query = cursor.execute("SELECT Recipe.title, Recipe.price, purchase.date, Recipe.recipe_id FROM Recipe NATURAL JOIN Customer NATURAL JOIN purchase WHERE Customer.username = %s", [sess_user])
        query = dictfetchall(cursor)
        customerinfo = cursor.execute("SELECT * FROM Customer WHERE Customer.username = %s", [sess_user])
        customerinfo = dictfetchall(cursor)
    context = {'query' : query, 'customerinfo' : customerinfo}
    return render(request, 'profile.html', context)


#### MYSQL QUERY EXAMPLE
# def my_custom_sql(self):
#     with connection.cursor() as cursor:
#         cursor.execute("UPDATE bar SET foo = 1 WHERE baz = %s", [self.baz])
#         cursor.execute("SELECT foo FROM bar WHERE baz = %s", [self.baz])
#         row = cursor.fetchone()

#     return row

# Create your views here.
