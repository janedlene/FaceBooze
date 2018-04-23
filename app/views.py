from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db import connection
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth import hashers
from django.core import serializers
import xmlrpclib
import json
import datetime

from .forms import SupplierForm, CustomerForm, LoginForm, RecipeForm, ReviewForm, OrderHistoryForm


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
    return HttpResponseRedirect(reversed('logout'))

@login_required
def producer_profile(request, p_id):
    producer = {}
    query = []
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM producer WHERE p_username=%s", [p_id])
        producer = dictfetchall(cursor)[0]

        cursor.execute("SELECT * FROM drink WHERE p_username=%s", [p_id])
        query = dictfetchall(cursor)

    isOwner = (request.session.get('uname', None) == p_id)
    context = {'query': query, 'producer': producer, 'allow_edit': isOwner}
    return render(request, 'producerProfile.html', context)

def isCustomer(username):
    cursor = connection.cursor()
    with connection.cursor() as cursor:
        cursor.execute("SELECT username FROM Customer WHERE username = %s", [username])
        data = cursor.fetchall()
        if len(data) > 0:
            return True
    return False


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
