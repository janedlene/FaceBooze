from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db import connection
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth import hashers
import datetime

from .forms import SupplierForm, CustomerForm, LoginForm, RecipeForm, ReviewForm, OrderHistoryForm

def login_required(f):
    def wrap(request, *args, **kwargs):
        # try authenticating the user
        if request.session.get('lazylogin', None) == None:
            messages.error(request, "Must login to lazychef.")
            return HttpResponseRedirect(reverse('login'))
        return f(request, *args, **kwargs)
    return wrap

@login_required
def logout(request):
    context = {}
    if request.session.get('lazylogin', None) != None:
        print request.session["lazylogin"]
        del request.session["lazylogin"]
        request.session.modified = True
        messages.success(request, 'Successfully logged out')
    else:
        messages.error(request, 'Cannot logout if you are not logged in')
    return HttpResponseRedirect(reverse('login'))

def login(request):
    # if logged in redirect to home
    if request.session.get('lazylogin', None) != None:
        return HttpResponseRedirect(reverse('index'))
    cursor = connection.cursor()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = [username]
            if request.POST.get('submit', None) == 'Customer Login':
                cursor.execute("SELECT password FROM Customer WHERE username = %s", user)
            else:
                cursor.execute("SELECT password FROM Supplier WHERE username = %s", user)
            query = cursor.fetchone()
            if query:
                query = query[0]
                if hashers.check_password(password, query):
                    request.session["lazylogin"] = username
                    messages.success(request, 'Successfully logged in')
                    return HttpResponseRedirect(reverse('index'))
            messages.error(request, 'Incorrect username/password')
            return HttpResponseRedirect(reverse('login'))
        else:
            messages.error(request, 'Must fill out all fields')
    form = LoginForm()
    context = {'form': form}
    return render(request, 'login.html', context)

def customerRegister(request):
    # if logged in redirect to home
    if request.session.get('lazylogin', None) != None:
        return HttpResponseRedirect(reverse('index'))
    cursor = connection.cursor()
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            pass1 = form.cleaned_data['password']
            pass2 = form.cleaned_data['confirm_pass']
            if pass1 != pass2:
                messages.error(request, "Passwords do not match")
                return HttpResponseRedirect(reverse('customer-register'))
            password = hashers.make_password(form.cleaned_data['password'])
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
                cursor.execute("SELECT username FROM Customer WHERE username = %s", [username])
                data = cursor.fetchall()
                if len(data) > 0:
                    messages.error(request, "Username is already taken.")
                    return HttpResponseRedirect(reverse('customer-register'))
                cursor.execute("SELECT username FROM Supplier WHERE username = %s", [username])
                data = cursor.fetchall()
                if len(data) > 0:
                    messages.error(request, "Username is already taken.")
                    return HttpResponseRedirect(reverse('customer-register'))
                cursor.execute("SELECT username FROM Customer WHERE email = %s", [email])
                data = cursor.fetchall()
                if len(data) > 0:
                    messages.error(request, "Email is already taken.")
                    return HttpResponseRedirect(reverse('customer-register'))
                cursor.execute("INSERT INTO Customer(username, password, first_name, last_name, email, phone_number, street, city, state, zip_code) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", customer)
            messages.success(request, 'Successfully registered!')
            return HttpResponseRedirect(reverse('login'))
        else:
            messages.error(request, 'Must fill out all fields')
    form = CustomerForm()
    context = {'form': form}
    return render(request, 'customerRegister.html', context)

def supplierRegister(request):
    # if logged in redirect to home
    if request.session.get('lazylogin', None) != None:
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
            password = hashers.make_password(form.cleaned_data['password'])
            org_name = form.cleaned_data['org_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            website = form.cleaned_data['website']
            street = form.cleaned_data['street']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zip_code = form.cleaned_data['zip_code']
            supplier = [username, password, org_name, email, phone_number, website, street, city, state, zip_code]
            with connection.cursor() as cursor:
                cursor.execute("SELECT username FROM Supplier WHERE username = %s", [username])
                data = cursor.fetchall()
                if len(data) > 0:
                    messages.error(request, "Username is already taken.")
                    return HttpResponseRedirect(reverse('supplier-register'))
                cursor.execute("SELECT username FROM Customer WHERE username = %s", [username])
                data = cursor.fetchall()
                if len(data) > 0:
                    messages.error(request, "Username is already taken.")
                    return HttpResponseRedirect(reverse('supplier-register'))
                cursor.execute("SELECT username FROM Supplier WHERE email = %s", [email])
                data = cursor.fetchall()
                if len(data) > 0:
                    messages.error(request, "Email is already taken.")
                    return HttpResponseRedirect(reverse('supplier-register'))
                cursor.execute("INSERT INTO Supplier(username, password, org_name, email, phone_number, website, street, city, state, zip_code) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", supplier)
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
    customerPurchases = []
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Recipe")
        query = dictfetchall(cursor)
        cursor.execute("SELECT recipe_id FROM purchase WHERE username = %s", [request.session.get('lazylogin', None)])
        customerPurchases = cursor.fetchall()
    isCust = isCustomer(request.session.get('lazylogin', None))
    history = []
    for purchase in customerPurchases:
        history.append(purchase[0])
    context = {'isCustomer': isCust, 'query': query, 'custHistory': history}
    return render(request, 'index.html', context)

@login_required
def createReview(request, id):
    cursor = connection.cursor()
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        print form.errors
        recipe_id = id
        if form.is_valid():
            print "forms valid"
            title = form.cleaned_data['title']
            body = form.cleaned_data['body']
            rating = form.cleaned_data['rating']
            review = [title, body, rating]

            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO Review(title, body, rating, date) VALUES (%s, %s, %s, CURDATE())", review)
                cursor.execute("INSERT INTO has(review_id, recipe_id) VALUES (%s, %s)", [cursor.lastrowid, recipe_id])
            return HttpResponseRedirect(reverse('index'))
    else:
        form = ReviewForm()
    context = {'form':form}
    return render(request, 'createReview.html', context)

@login_required
def sellRecipe(request):
    cursor = connection.cursor()
    if request.method == 'POST':
        form = RecipeForm(request.POST, extra=request.POST.get('ingredient_count'))
        if form.is_valid():
            title = form.cleaned_data['title']
            directions = form.cleaned_data['directions']
            serving_size = form.cleaned_data['serving_size']
            cooking_time = form.cleaned_data['cooking_time']
            cuisine_type = form.cleaned_data['cuisine_type']
            price = form.cleaned_data['price']
            recipe = [title, directions, serving_size, cooking_time, cuisine_type, price]

            ingredient_count = form.cleaned_data['ingredient_count']
            username = request.session.get('lazylogin', None)
            

            with connection.cursor() as cursor:
                query = cursor.execute("INSERT INTO Recipe(title, directions, serving_size, cooking_time, cuisine_type, price) VALUES (%s, %s, %s, %s, %s, %s)", recipe)
                #insert ingredients into ingredients table and into many to many table
                rid = cursor.lastrowid
                selling = [rid, username]
                query2 = cursor.execute("INSERT INTO sell(recipe_id, username) VALUES (%s, %s)", selling)
                for x in range (int(ingredient_count)):
                    ingred = form.cleaned_data['ingredient_' + str(x)]
                    #check if ingredient is in ingredient list, if it isn't, add it
                    query3 = cursor.execute("""INSERT INTO Ingredient(name) VALUES (%s) ON DUPLICATE KEY UPDATE name = %s """, (ingred, ingred))
                    ingredient = [ingred, rid]
                    query4 = cursor.execute("INSERT INTO contains(name, recipe_id) VALUES (%s, %s)", ingredient)
            if query and query2 and query3 and query4:
                messages.success(request, 'Successfully created new recipe called ' + title)
                form = RecipeForm()
            else:
                messages.error(request, 'Could not create new recipe')
    else:
        form = RecipeForm()
    context = {'form': form}
    return render(request, 'sellRecipe.html', context)


def buyRecipe(request, id):
    cursor = connection.cursor()
    if not isCustomer(request.session.get('lazylogin', None)):
        messages.error(request, 'Must be a customer to buy a recipe')
        return HttpResponseRedirect(reverse('index'))
    recipe_id = id
    username = request.session.get('lazylogin', None)
    date = datetime.datetime.now()
    purchase = [username, recipe_id, date]
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Recipe WHERE recipe_id = %s", [recipe_id])
        query = dictfetchall(cursor)
        # print query[0]['available']
        if query[0]['available'] == False:
            messages.error(request, "Cannot buy an unavailable recipe")
            return HttpResponseRedirect(reverse('index'))
        cursor.execute("SELECT * FROM purchase WHERE username = %s AND recipe_id = %s", [username, recipe_id])
        if len(cursor.fetchall()) > 0:
            messages.error(request, "Cannot buy recipe already purchased")
            return HttpResponseRedirect(reverse('index'))
        cursor.execute("INSERT INTO purchase(username, recipe_id, date) VALUES (%s, %s, %s)", purchase)
    messages.success(request, 'Successfully purchased recipe!')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def isCustomer(username):
    cursor = connection.cursor()
    with connection.cursor() as cursor:
        cursor.execute("SELECT username FROM Customer WHERE username = %s", [username])
        data = cursor.fetchall()
        if len(data) > 0:
            return True
    return False


#### FIX THIS ######
def didPurchase(username, id):
    cursor = connection.cursor()
    with connection.cursor() as cursor:
        sess_user = request.session.get('lazylogin', None)
        recipe_id = id
        check = [[sess_user], recipe_id]
        cursor.execute("SELECT Recipe.title FROM Recipe NATURAL JOIN Customer NATURAL JOIN purchase WHERE Customer.username = %s AND Recipe.id = %s", check)
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

def customerHistory(request):
    cursor = connection.cursor()
    query = []
    
    with connection.cursor() as cursor:
        sess_user = request.session.get('lazylogin', None)
        query = cursor.execute("SELECT Recipe.title, Recipe.price, purchase.date FROM Recipe NATURAL JOIN Customer NATURAL JOIN purchase WHERE Customer.username = %s", [sess_user])
        print request.session.get('lazylogin', None)
        query = dictfetchall(cursor)
        #print query 
    print query
    context = {'query' : query}
    return render(request, 'customerHistory.html', context)

def recipeDetails(request, id):
    cursor = connection.cursor()
    query = []
    recipe_id = id
    with connection.cursor() as cursor:
        sess_user = request.session.get('lazylogin', None)
        cursor.execute("SELECT * FROM Recipe WHERE recipe_id = %s", [recipe_id])
        query = dictfetchall(cursor)
        cursor.execute("SELECT * FROM sell WHERE username = %s", [request.session.get('lazylogin', None)])
        supplierRecipes = dictfetchall(cursor)
    isCust = isCustomer(request.session.get('lazylogin', None))
    supplierRecipeIDs = []
    for recipe in supplierRecipes:
        supplierRecipeIDs.append(recipe['recipe_id'])
    context = {'isCustomer': isCust, 'query' : query, 'supplierRecipes': supplierRecipeIDs}
    return render(request, 'recipeDetails.html', context)

def ajax_search_recipe(request):
    cursor = connection.cursor()
    query = []
    if request.is_ajax():
        q = "'%" + request.GET.get('q') + "%'"
        if q is not None:            
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM  Recipe WHERE title LIKE " + q + " OR serving_size LIKE " + q)
                query = dictfetchall(cursor)
                cursor.execute("SELECT recipe_id FROM purchase WHERE username = %s", [request.session.get('lazylogin', None)])
                customerPurchases = cursor.fetchall()
    isCust = isCustomer(request.session.get('lazylogin', None))
    history = []
    for purchase in customerPurchases:
        history.append(purchase[0])
    context = {'query': query, 'isCustomer' : isCust, 'custHistory': history} 
    return render(request, '_recipes.html', context)

### FIX THISS TOOO ###
def cancelOrder(request, id):
    cursor = connection.cursor()
    query = []
    with connection.cursor() as cursor:
        recipe_id = id
        sess_user = request.session.get('lazylogin', None)
        check = [recipe_id, sess_user]
        query = cursor.execute("DELETE * FROM purchase NATURAL JOIN Recipe NATURAL JOIN Customer WHERE purchase.recipe_id = %s AND Customer.username = %s", check)
        if query:
            messages.success(request, 'Successfully cancelled order')
    context = {'query': query}
    return render(request, 'recipeDetails.html', context)


### AND THISSSS ###
def showReviews(request, id):
    cursor = connection.cursor()
    reviews = []
    with connection.cursor() as cursor:
        recipe_id = id
        reviews = cursor.execute("SELECT * FROM Review NATURAL JOIN has WHERE has.recipe_id = %s", [recipe_id])
        reviews = dictfetchall(cursor)
    context = {'reviews' : reviews}
    return render(request, 'recipeDetails.html', context)

def ajax_available_recipe(request):
    cursor = connection.cursor()
    if request.is_ajax():
        q = request.GET.get('q')
        cursor.execute("UPDATE Recipe SET available = 1 WHERE recipe_id = %s", [q])
    return HttpResponse(q)

def ajax_unavailable_recipe(request):
    cursor = connection.cursor()
    if request.is_ajax():
        q = request.GET.get('q')
        cursor.execute("UPDATE Recipe SET available = 0 WHERE recipe_id = %s", [q])
    return HttpResponse(q)

#### MYSQL QUERY EXAMPLE
# def my_custom_sql(self):
#     with connection.cursor() as cursor:
#         cursor.execute("UPDATE bar SET foo = 1 WHERE baz = %s", [self.baz])
#         cursor.execute("SELECT foo FROM bar WHERE baz = %s", [self.baz])
#         row = cursor.fetchone()

#     return row

# Create your views here.
