from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.db import connection
from django.core.urlresolvers import reverse
from django.contrib import messages

from .forms import SupplierForm, CustomerForm, LoginForm, RecipeForm, ReviewForm

def logout(request):
    context = {}
    if request.session["login"]:
        request.session["login"] = False
        messages.success(request, 'Successfully logged out')
    else:
        messages.error(request, 'Cannot logout if you are not logged in')
    return HttpResponseRedirect(reverse('login'))
    

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = [username, password]
            with connection.cursor() as cursor:
                query = cursor.execute("SELECT username FROM Customer WHERE username = %s AND password = %s", user)
            if query:
                request.session["login"] = True
                messages.success(request, 'Successfully logged in')
                return HttpResponseRedirect(reverse('index'))
            messages.error(request, 'Incorrect username/password')
            return HttpResponseRedirect(reverse('login'))
    else:
        form = LoginForm()
    context = {'form': form}
    return render(request, 'login.html', context)

def customerRegister(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            street = form.cleaned_data['street']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zip_code = form.cleaned_data['zip_code']
            customer = [username, password, first_name, last_name, email, phone_number, street, city, state, zip_code]
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO Customer(username, password, first_name, last_name, email, phone_number, street, city, state, zip_code) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", customer)
            return HttpResponseRedirect(reverse('login'))
    else:
        form = CustomerForm()
    context = {'form': form}
    return render(request, 'customerRegister.html', context)

def supplierRegister(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            org_name = form.cleaned_data['org_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            website = form.cleaned_data['website']
            street = form.cleaned_data['street']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zip_code = form.cleaned_data['zip_code']
            supplier = [org_name, email, phone_number, website, street, city, state, zip_code]
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO Supplier(org_name, email, phone_number, website, street, city, state, zip_code) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", supplier)
            return HttpResponseRedirect(reverse('login'))
    else:
        form = SupplierForm()
    context = {'form': form}
    return render(request, 'supplierRegister.html', context)

def index(request):
    context = {}
    return render(request, 'index.html', context)


def reviewRegister(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            body = form.cleaned_data['body']
            rating = form.cleaned_data['rating']
            review = [title, body, rating]
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO Review(title, body, rating, date) VALUES (%s, %s, %s, CURDATE())", review)
            return HttpResponseRedirect(reverse('index'))
    else:
        form = ReviewForm()
    context = {'form':form}
    return render(request, 'reviewRegister.html', context)

def sellRecipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            directions = form.cleaned_data['directions']
            serving_size = form.cleaned_data['serving_size']
            cooking_time = form.cleaned_data['cooking_time']
            cuisine_type = form.cleaned_data['cuisine_type']
            price = form.cleaned_data['price']
            recipe = [title, directions, serving_size, cooking_time, cuisine_type, price]
            with connection.cursor() as cursor:
                query = cursor.execute("INSERT INTO Recipe(title, directions, serving_size, cooking_time, cuisine_type, price) VALUES (%s, %s, %s, %s, %s, %s)", recipe)
            if query:
                messages.success(request, 'Successfully created new recipe called ' + title)
                #return HttpResponseRedirect(reverse('sellRecipe'))
            else:
                messages.error(request, 'Could not create new recipe')
            #return HttpResponseRedirect(reverse('sellRecipe'))
    else:
        form = RecipeForm()
    context = {'form': form}
    return render(request, 'sellRecipe.html', context)


#### MYSQL QUERY EXAMPLE
# def my_custom_sql(self):
#     with connection.cursor() as cursor:
#         cursor.execute("UPDATE bar SET foo = 1 WHERE baz = %s", [self.baz])
#         cursor.execute("SELECT foo FROM bar WHERE baz = %s", [self.baz])
#         row = cursor.fetchone()

#     return row

# Create your views here.
