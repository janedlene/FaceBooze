from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from django.db import connection
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth import hashers
from django.core import serializers
import xmlrpclib
import json
import datetime

from .forms import *


def login_required(f):
    def wrap(request, *args, **kwargs):
        # try authenticating the user
        if request.session.get('uname', None) == None:
            messages.error(request, "Must login to Facebooze.")
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
            cursor.execute("SELECT * from retailer WHERE r_username = %s AND r_password = %s", user)
            query = dictfetchall(cursor)
            if query:
                dat_user = query[0]
                request.session["uname"] = dat_user['r_username']
                request.session["name"] = dat_user['r_name']
                messages.success(request, 'Successfully logged in')
                return HttpResponseRedirect(reverse('index'))
            cursor.execute("SELECT * from producer WHERE p_username = %s AND p_password = %s", user)
            query = dictfetchall(cursor)
            if query:
                dat_user = query[0]
                request.session["uname"] = dat_user['p_username']
                request.session["name"] = dat_user['p_name']
                messages.success(request, 'Successfully logged in')
                return HttpResponseRedirect(reverse('index'))
            messages.error(request, 'Incorrect username/password')
            return HttpResponseRedirect(reverse('index'))
        else:
            messages.error(request, 'Must fill out all fields')
    form = LoginForm()
    context = {'form': form}
    return render(request, 'login.html', context)


def supplierRegister(request):
    # if logged in redirect to home
    if request.session.get('uname', None) != None:
        return HttpResponseRedirect(reverse('index'))
    # if this is a POST request we need to process the form data
    cursor = connection.cursor()
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            pass1 = form.cleaned_data['password']
            pass2 = form.cleaned_data['confirm_pass']
            if pass1 != pass2:
                messages.error(request, "Passwords do not match")
                return HttpResponseRedirect(reverse('supplier-register'))
            password = form.cleaned_data['password']
            org_name = form.cleaned_data['org_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            acct_type = form.cleaned_data['user_type']
            tableName = 'retailer' if acct_type == 'R' else 'producer'
            address = form.cleaned_data['address']
            business_type = form.cleaned_data['business_type']
            supplier = [username, password, org_name, email, phone_number, address, business_type]
            with connection.cursor() as cursor:
                # cursor.execute("SELECT username FROM " + tableName + " WHERE username = %s", [username])
                # data = cursor.fetchall()
                # if len(data) > 0:
                #     messages.error(request, "Username is already taken.")
                #     return HttpResponseRedirect(reverse('supplier-register'))
                # TODO put username, password stuff back in
                if tableName == 'retailer':
                    cursor.execute("SELECT r_username FROM " + tableName + " WHERE r_email = %s", [email])
                    data = cursor.fetchall()
                    if len(data) > 0:
                        messages.error(request, "Email is already taken.")
                        return HttpResponseRedirect(reverse('supplier-register'))
                    cursor.execute(
                        "INSERT INTO retailer(r_username, r_password, r_name, r_email, r_phone, r_location, r_type) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        supplier)
                else:
                    cursor.execute("SELECT p_username FROM " + tableName + " WHERE p_email = %s", [email])
                    data = cursor.fetchall()
                    if len(data) > 0:
                        messages.error(request, "Email is already taken.")
                        return HttpResponseRedirect(reverse('supplier-register'))
                    cursor.execute(
                        "INSERT INTO producer(p_username, p_password, p_name, p_email, p_phone, p_location, p_type) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        supplier)

            messages.success(request, 'Successfully registered!')
            return HttpResponseRedirect(reverse('login'))
        else:
            messages.error(request, 'Must fill out all fields')
    form = SupplierForm()
    context = {'form': form}
    return render(request, 'supplierRegister.html', context)


@login_required
def index(request):
    cursor = connection.cursor()
    query = []
    with connection.cursor() as cursor:
        isProd = False
        isRet = False
        cursor.execute("SELECT * FROM producer WHERE p_username = %s", [request.session["uname"]])
        data1 = cursor.fetchall()
        if len(data1) > 0:
            isProd = True
        cursor.execute("SELECT * FROM retailer WHERE r_username = %s", [request.session["uname"]])
        data2 = cursor.fetchall()
        if len(data2) > 0:
            isRet = True
    if isProd:
        return producer_profile(request, request.session['uname'])
    elif isRet:
        return retailer_profile(request, request.session['uname'])
    return HttpResponseRedirect(reverse('logout'))

@login_required
def producer_profile(request, p_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM producer WHERE p_username=%s", [p_id])
        producer = dictfetchall(cursor)[0]

        cursor.execute("SELECT * FROM drink WHERE p_username=%s", [p_id])
        query = dictfetchall(cursor)

    isOwner = (request.session.get('uname', None) == p_id)
    context = {'query': query, 'producer': producer, 'allow_edit': isOwner}
    return render(request, 'producerProfile.html', context)



def addDrink(p_id, name, abv):
    with connection.cursor() as cursor:
        cursor.execute("SELECT max(d_id) FROM drink")
        d_id = cursor.fetchone()[0] + 1
        cursor.execute("INSERT INTO drink(d_id, d_name, d_abv, p_username) VALUES (%s, %s, %s, %s)", [d_id, name, abv, p_id])
        return d_id


@login_required
def producer_add_drink_beer(request):
    context = {}
    if request.method == 'GET':
        form = BeerForm()
        context = {'title': 'Add a new beer', 'form': form}
    elif request.method == 'POST':
        form = BeerForm(request.POST)
        if form.is_valid():
            d_id = addDrink(request.session['uname'], form.cleaned_data['name'], form.cleaned_data['abv'])
            with connection.cursor() as cursor:
                cursor.execute('INSERT INTO beer(d_id, b_type, b_ibu) VALUES (%s, %s, %s)',
                               [d_id, form.cleaned_data['type'], form.cleaned_data['ibu']])
            return HttpResponseRedirect(reverse('index'))
    return render(request, 'genericForm.html', context=context)

@login_required
def producer_add_drink_wine(request):
    context = {}
    if request.method == 'GET':
        form = WineForm()
        context = {'title': 'Add a new wine', 'form': form}
    elif request.method == 'POST':
        form = WineForm(request.POST)
        if form.is_valid():
            d_id = addDrink(request.session['uname'], form.cleaned_data['name'], form.cleaned_data['abv'])
            with connection.cursor() as cursor:
                cursor.execute('INSERT INTO wine(d_id, w_type, w_year) VALUES (%s, %s, %s)',
                               [d_id, form.cleaned_data['type'], form.cleaned_data['year']])
            return HttpResponseRedirect(reverse('index'))
    return render(request, 'genericForm.html', context=context)

@login_required
def producer_add_drink_liquor(request):
    context = {}
    if request.method == 'GET':
        form = LiquorForm()
        context = {'title': 'Add a new liquor', 'form': form}
    elif request.method == 'POST':
        form = LiquorForm(request.POST)
        if form.is_valid():
            d_id = addDrink(request.session['uname'], form.cleaned_data['name'], form.cleaned_data['abv'])
            with connection.cursor() as cursor:
                cursor.execute('INSERT INTO liquor(d_id, l_type, flavor) VALUES (%s, %s, %s)',
                               [d_id, form.cleaned_data['type'], form.cleaned_data['flavor']])
            return HttpResponseRedirect(reverse('index'))

    return render(request, 'genericForm.html', context=context)

@login_required
def producer_add_drink_other(request):
    context = {}
    if request.method == 'GET':
        form = ProducerAddDrinkForm()
        context = {'title': 'Add a new drink', 'form': form}
    elif request.method == 'POST':
        form = ProducerAddDrinkForm(request.POST)
        if form.is_valid():
            d_id = addDrink(request.session['uname'], form.cleaned_data['name'], form.cleaned_data['abv'])
            return HttpResponseRedirect(reverse('index'))
    return render(request, 'genericForm.html', context=context)


@login_required
def producer_delete_drink(request, d_id):
    uname = request.session['uname']
    with connection.cursor() as cursor:
        cursor.execute("SELECT d_id FROM drink WHERE d_id=%s AND p_username=%s", [d_id, uname])
        if len(cursor.fetchall()) != 1:
            return HttpResponseForbidden()
        cursor.execute("DELETE FROM drink WHERE d_id=%s", [d_id])

    return HttpResponseRedirect(reverse('index'))

@login_required
def retailer_profile(request, r_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM retailer WHERE r_username=%s", [r_id])
        producer = dictfetchall(cursor)[0]

        cursor.execute("SELECT * FROM drink NATURAL JOIN retail_inv WHERE r_username=%s", [r_id])
        query = dictfetchall(cursor)

    isOwner = (request.session.get('uname', None) == r_id)
    context = {'query': query, 'producer': producer, 'allow_edit': isOwner}
    return render(request, 'retailerProfile.html', context)


@login_required
def retailer_add_stock(request):
    context = {}
    if request.method == 'GET':
        form = RetailerAddStockForm()
        context = {'title': 'Add a new stock item', 'form': form}
    elif request.method == 'POST':
        form = RetailerAddStockForm(request.POST)
        if form.is_valid():
            with connection.cursor() as cursor:
                uname = request.session['uname']
                cursor.execute("INSERT INTO retail_inv(r_username, d_id, quantity) VALUES (%s,%s,%s)",
                               [uname, form.cleaned_data['d_id'], form.cleaned_data['quantity']])
            return HttpResponseRedirect(reverse('index'))

    return render(request, 'genericForm.html', context=context)


@login_required
def retailer_delete_stock(request, d_id):
    uname = request.session['uname']
    with connection.cursor() as cursor:
        cursor.execute("SELECT d_id FROM retail_inv WHERE d_id=%s AND r_username=%s", [d_id, uname])
        if len(cursor.fetchall()) != 1:
            return HttpResponseForbidden()
        cursor.execute("DELETE FROM retail_inv WHERE d_id=%s AND r_username=%s", [d_id, uname])

    return HttpResponseRedirect(reverse('index'))

@login_required
def search(request):
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
            cursor.execute("select d_id,d_name,p_name,p_username,p_location \
            from facebooze.drink natural join facebooze.producer")
            query = dictfetchall(cursor)
    context = {'query': query, 'form': form}
    return render(request, 'searchResults.html', context)

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

#### MYSQL QUERY EXAMPLE
# def my_custom_sql(self):
#     with connection.cursor() as cursor:
#         cursor.execute("UPDATE bar SET foo = 1 WHERE baz = %s", [self.baz])
#         cursor.execute("SELECT foo FROM bar WHERE baz = %s", [self.baz])
#         row = cursor.fetchone()

#     return row

# Create your views here.
