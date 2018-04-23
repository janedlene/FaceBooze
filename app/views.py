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
                or MATCH (p_name) AGAINST (%s IN NATURAL LANGUAGE MODE);" \
                ,[search,search])
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
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

@login_required
def createReview(request, id):
    cursor = connection.cursor()
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        recipe_id = id
        if form.is_valid():
            title = form.cleaned_data['title']
            body = form.cleaned_data['body']
            rating = form.cleaned_data['rating']
            review = [title, body, rating]

            with connection.cursor() as cursor:
                sess_user = request.session.get('uname', None)

                cursor.execute("INSERT INTO Review(title, body, rating, date) VALUES (%s, %s, %s, CURDATE())", review)
                review_id = cursor.lastrowid
                cursor.execute("INSERT INTO has(review_id, recipe_id) VALUES (%s, %s)", [review_id, recipe_id])
                cursor.execute("INSERT INTO wrote(username, review_id) VALUES (%s, %s)", [sess_user, review_id])
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
            image = form.cleaned_data['src']
            recipe = [title, directions, serving_size, cooking_time, cuisine_type, price, image]

            ingredient_count = form.cleaned_data['ingredient_count']
            username = request.session.get('uname', None)
            

            with connection.cursor() as cursor:
                query = cursor.execute("INSERT INTO Recipe(title, directions, serving_size, cooking_time, cuisine_type, price, src) VALUES (%s, %s, %s, %s, %s, %s, %s)", recipe)
                #insert ingredients into ingredients table and into many to many table
                rid = cursor.lastrowid
                selling = [rid, username]
                query2 = cursor.execute("INSERT INTO sell(recipe_id, username) VALUES (%s, %s)", selling)
                for x in range (int(ingredient_count)):
                    ingred = form.cleaned_data['ingredient_' + str(x)]
                    quant = form.cleaned_data['quantity_' + str(x)]
                    #check if ingredient is in ingredient list, if it isn't, add it
                    query3 = cursor.execute("""INSERT INTO Ingredient(name) VALUES (%s) ON DUPLICATE KEY UPDATE name = %s """, (ingred, ingred))
                    ingredient = [ingred, rid, quant]
                    query4 = cursor.execute("INSERT INTO contains(name, recipe_id, quantity) VALUES (%s, %s, %s)", ingredient)
            if query and query2 and query3 and query4:
                messages.success(request, 'Successfully created new recipe called ' + title)
            else:
                messages.error(request, 'Could not create new recipe')
    else:
        form = RecipeForm()
    context = {'form': form}
    return render(request, 'sellRecipe.html', context)

@login_required
def editRecipe(request, id):
    cursor = connection.cursor()
    rid = id
    if request.method == 'POST':
        form = RecipeForm(request.POST, extra=request.POST.get('ingredient_count'))
        if form.is_valid():
            title = form.cleaned_data['title']
            directions = form.cleaned_data['directions']
            serving_size = form.cleaned_data['serving_size']
            cooking_time = form.cleaned_data['cooking_time']
            cuisine_type = form.cleaned_data['cuisine_type']
            price = form.cleaned_data['price']
            image = form.cleaned_data['src']
            recipe = [title, directions, serving_size, cooking_time, cuisine_type, price, image, rid]

            # ingredient_count = form.cleaned_data['ingredient_count']
            

            with connection.cursor() as cursor:
                query = cursor.execute("UPDATE Recipe SET title=%s, directions = %s, serving_size = %s, cooking_time = %s, cuisine_type=%s, price=%s, src=%s WHERE recipe_id = %s", recipe)
                query2 = cursor.execute("DELETE FROM contains WHERE recipe_id = %s", [rid]) #remove all old ingredients linked to recipe
                #insert ingredients into ingredients table and into many to many table
                # for x in range (int(ingredient_count)):
                #     ingred = form.cleaned_data['ingredient_' + str(x)]
                #     quant = form.cleaned_data['quantity_' + str(x)]
                #     #check if ingredient is in ingredient list, if it isn't, add it
                #     query3 = cursor.execute("""INSERT INTO Ingredient(name) VALUES (%s) ON DUPLICATE KEY UPDATE name = %s """, (ingred, ingred))
                #     ingredient = [ingred, rid, quant]
                #     query4 = cursor.execute("INSERT INTO contains(name, recipe_id, quantity) VALUES (%s, %s, %s)", ingredient)
            # if query and query2 and query3 and query4:
            if query and query2:
                messages.success(request, 'Successfully edited recipe called ' + title)
                form = RecipeForm()
            else:
                messages.error(request, 'Could not edit recipe')
        context = {'form': form}
    else:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Recipe WHERE recipe_id = %s", [rid])
            fillData = dictfetchall(cursor)
            cursor.execute("SELECT * FROM contains WHERE recipe_id = %s", [rid])
            ingredientFillData = dictfetchall(cursor)
            ingredient_count = len(ingredientFillData)
            rTitle = {'title': fillData[0]['title']}
            # form = RecipeForm(initial={'title': fillData[0]['title'], 'directions': fillData[0]['directions'], 'serving_size': fillData[0]['serving_size'],  'cooking_time': fillData[0]['cooking_time'],  'cuisine_type': fillData[0]['cuisine_type'],  'price': fillData[0]['price'], 'ingredient_count': ingredient_count})
            form = RecipeForm(initial={'src': fillData[0]['src'], 'title': fillData[0]['title'], 'directions': fillData[0]['directions'], 'serving_size': fillData[0]['serving_size'],  'cooking_time': fillData[0]['cooking_time'],  'cuisine_type': fillData[0]['cuisine_type'],  'price': fillData[0]['price']})
            context = {'form': form, 'title': rTitle, 'ingredients': ingredientFillData}
    
    return render(request, 'editRecipe.html', context)

@login_required
def buyRecipe(request, id):
    cursor = connection.cursor()
    if not isCustomer(request.session.get('uname', None)):
        messages.error(request, 'Must be a customer to buy a recipe')
        return HttpResponseRedirect(reverse('index'))
    recipe_id = id
    username = request.session.get('uname', None)
    date = datetime.datetime.now()
    purchase = [username, recipe_id, date]
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Recipe WHERE recipe_id = %s", [recipe_id])
        query = dictfetchall(cursor)
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


@login_required
def cancelOrder(request, id):
    cursor = connection.cursor()
    recipe_id = id
    username = request.session.get('uname', None)
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM purchase WHERE purchase.recipe_id = %s AND purchase.username = %s", [recipe_id, username])
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def deleteReview(request, id):
    cursor = connection.cursor()
    review_id = id
    with connection.cursor() as cursor:
        sess_user = request.session.get('uname', None)
        cursor.execute("DELETE FROM Vote WHERE Vote.review_id = %s", [review_id])
        cursor.execute("DELETE FROM has WHERE has.review_id = %s", [review_id])
        cursor.execute("DELETE FROM wrote WHERE wrote.review_id = %s AND wrote.username = %s", [review_id, sess_user])
        cursor.execute("INSERT INTO has(review_id, recipe_id) VALUES (%s, %s)", [review_id, recipe_id])
        cursor.execute("DELETE FROM Review WHERE Review.review_id = %s", [review_id])
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def editReview(request, id):
    cursor = connection.cursor()
    review_id = id
    form = ReviewForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            title = form.cleaned_data['title']
            body = form.cleaned_data['body']
            rating = form.cleaned_data['rating']

            with connection.cursor() as cursor:
                sess_user = request.session.get('uname', None)
                cursor.execute("UPDATE Review SET Review.title = %s, Review.body = %s, Review.rating = %s WHERE Review.review_id = %s", [title, body, rating, review_id])
                return HttpResponseRedirect(reverse('index'))
    else:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Review WHERE review_id = %s", [review_id])
            fillData = dictfetchall(cursor)
        form = ReviewForm(initial={'title': fillData[0]['title'], 'body': fillData[0]['body'], 'rating': fillData[0]['rating']})
    context = {'form':form}
    return render(request, 'editReview.html', context)    

@login_required
def recipeDetails(request, id):
    cursor = connection.cursor()
    query = []
    reviews = []
    customerReviews = []
    recipe_id = id

    with connection.cursor() as cursor:
        sess_user = request.session.get('uname', None)
        cursor.execute("SELECT * FROM Recipe WHERE recipe_id = %s", [recipe_id])
        query = dictfetchall(cursor)
        cursor.execute("SELECT * FROM sell WHERE username = %s", [request.session.get('uname', None)])
        supplierRecipes = dictfetchall(cursor)
        cursor.execute("SELECT name, quantity FROM contains WHERE recipe_id = %s", [recipe_id])
        ingredients = dictfetchall(cursor)
        cursor.execute("SELECT * FROM Review NATURAL JOIN has WHERE has.recipe_id = %s", [recipe_id])
        reviews = dictfetchall(cursor)
        for review in reviews:
            cursor.execute("SELECT wrote.username FROM wrote WHERE wrote.review_id = %s", [int(review['review_id'])])
            usernames = dictfetchall(cursor)
            review['username'] = usernames[0]['username']

        cursor.execute("SELECT wrote.review_id FROM wrote WHERE wrote.username = %s", [sess_user])
        customerReviews = cursor.fetchall()
    myreviews = []
    for review in customerReviews:
        myreviews.append(review[0])    

    isCust = isCustomer(request.session.get('uname', None))
    supplierRecipeIDs = []

    for recipe in supplierRecipes:
        supplierRecipeIDs.append(recipe['recipe_id'])

    context = {'isCustomer': isCust, 'query' : query, 'supplierRecipes': supplierRecipeIDs, 'reviews' : reviews, 'myreviews':myreviews, 'ingredients': ingredients}

    return render(request, 'recipeDetails.html', context)

@login_required
def review_upvote(request, id):
    cursor = connection.cursor()
    review_id = id
    sess_user = request.session.get('uname', None)
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Vote WHERE Vote.username = %s AND Vote.review_id = %s", [sess_user, review_id])
        userVotes = dictfetchall(cursor)
        if len(userVotes) > 0:
            messages.error(request, "Cannot vote for review already voted for!")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        # cursor.execute("SELECT Review.votes FROM Review WHERE Review.review_id = %s", [review_id])
        # votes = dictfetchall(cursor)
        # votes = int(votes[0]['votes'])
        # votes = votes + 1
        # cursor.execute("UPDATE Review SET votes = %s WHERE review_id = %s", [votes, review_id])
        cursor.execute("INSERT INTO Vote(review_id, username, type) VALUES (%s, %s, %s)", [review_id, sess_user, 1])
        
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def review_downvote(request, id):
    cursor = connection.cursor()
    review_id = id
    sess_user = request.session.get('uname', None)
    with connection.cursor() as cursor:
        cursor.execute("SELECT Vote.review_id FROM Vote WHERE username = %s AND review_id = %s", [sess_user, review_id])
        userVotes = dictfetchall(cursor)
        if len(userVotes) > 0:
            messages.error(request, "Cannot vote for review already voted for!")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        # cursor.execute("SELECT Review.votes FROM Review WHERE Review.review_id = %s", [review_id])
        # votes = dictfetchall(cursor)
        # votes = int(votes[0]['votes'])
        # votes = votes - 1
        # cursor.execute("UPDATE Review SET votes = %s WHERE review_id = %s", [votes, review_id])
        cursor.execute("INSERT INTO Vote(review_id, username, type) VALUES (%s, %s, %s)", [review_id, sess_user, 0])
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def ajax_search_recipe(request):
    cursor = connection.cursor()
    query = []
    if request.is_ajax():
        q = "'%" + request.GET.get('q') + "%'"
        if q is not None:            
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM  Recipe WHERE title LIKE " + q + " OR serving_size LIKE " + q)
                query = dictfetchall(cursor)
                cursor.execute("SELECT recipe_id FROM purchase WHERE username = %s", [request.session.get('uname', None)])
                customerPurchases = cursor.fetchall()
    isCust = isCustomer(request.session.get('uname', None))
    history = []
    for purchase in customerPurchases:
        history.append(purchase[0])
    context = {'query': query, 'isCustomer' : isCust, 'custHistory': history} 
    return render(request, '_recipes.html', context)


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

@login_required
def viewSupplierProfile(request):
    cursor = connection.cursor()
    query = []
    with connection.cursor() as cursor:
        sess_user = request.session.get('uname', None)
        query = cursor.execute("SELECT Recipe.title, Recipe.price, Recipe.recipe_id FROM Recipe NATURAL JOIN Supplier NATURAL JOIN sell WHERE Supplier.username = %s", [sess_user])
        query = dictfetchall(cursor)
        supplierinfo = cursor.execute("SELECT * FROM Supplier WHERE Supplier.username = %s", [sess_user])
        supplierinfo = dictfetchall(cursor)
    context = {'query' : query, 'supplierinfo' : supplierinfo}
    return render(request, 'supplierProfile.html', context)

@login_required
def export_customer(request):
    sess_user = request.session.get('uname', None)
    export_type = request.GET.get('export_type')
    cursor = connection.cursor()
    cursor.execute("SELECT Recipe.title, Recipe.price, purchase.date FROM Recipe NATURAL JOIN Customer NATURAL JOIN purchase WHERE Customer.username = %s", [sess_user])
    query = dictfetchall(cursor)
    for item in query:
        item['date'] = str(item['date'])
        item['price'] = float(item['price'])
    filename = sess_user = request.session.get('uname', None) + "History" + str(datetime.datetime.now())        
    if export_type == "JSON":
        data = json.dumps(query, indent=4, sort_keys=True)
        filename = filename + ".json"
        response = HttpResponse(data, content_type='application/json')
    elif export_type == "XML":
        data = xmlrpclib.dumps((query,))
        filename = filename + ".xml"
        response = HttpResponse(data, content_type='text/xml')
    response['Content-Disposition'] = 'attachment; filename=' + filename
    return response

@login_required
def export_supplier(request):
    sess_user = request.session.get('uname', None)
    export_type = request.GET.get('export_type')
    cursor = connection.cursor()
    cursor.execute("SELECT Recipe.title, Recipe.price, Recipe.directions, Recipe.serving_size, Recipe.cooking_time, Recipe.cuisine_type, Recipe.available FROM Recipe NATURAL JOIN Supplier NATURAL JOIN sell WHERE Supplier.username = %s", [sess_user])
    query = dictfetchall(cursor)
    for item in query:
        item['price'] = float(item['price'])
        item['cooking_time'] = float(item['cooking_time'])
        item['serving_size'] = float(item['serving_size'])
    filename = sess_user = request.session.get('uname', None) + "Recipes" + str(datetime.datetime.now())        
    if export_type == "JSON":
        data = json.dumps(query, indent=4, sort_keys=True)
        filename = filename + ".json"
        response = HttpResponse(data, content_type='application/json')
    elif export_type == "XML":
        data = xmlrpclib.dumps((query,))
        filename = filename + ".xml"
        response = HttpResponse(data, content_type='text/xml')
    response['Content-Disposition'] = 'attachment; filename=' + filename
    return response

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
