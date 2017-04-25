from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^register/supplier/$', views.supplierRegister, name='supplier-register'),
    url(r'^register/customer/$', views.customerRegister, name='customer-register'),
    url(r'^home/$', views.index, name='index'),
    url(r'^home/review/(?P<id>[0-9]+)/$', views.createReview, name='create-review'),
    url(r'^customerhistory/$', views.customerHistory, name='customer-history'),
    url(r'^recipe/sell/$', views.sellRecipe, name='sell-recipe'),
	url(r'^recipe/buy/(?P<id>[0-9]+)/$', views.buyRecipe, name='buy-recipe'),
	url(r'^recipe/details/(?P<id>[0-9]+)/$', views.recipeDetails, name='recipe-details'),
	url(r'^recipe/cancel/(?P<id>[0-9]+)/$', views.cancelOrder, name='cancel-order'),
    url(r'^ajax/search/recipe/$', views.ajax_search_recipe, name='ajax-search-recipe'),
    url(r'^ajax/available/recipe/$', views.ajax_available_recipe, name='ajax-available-recipe'),
    url(r'^ajax/unavailable/recipe/$', views.ajax_unavailable_recipe, name='ajax-unavailable-recipe'),

]
