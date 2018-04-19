from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^register/supplier/$', views.supplierRegister, name='supplier-register'),
    url(r'^register/consumer/$', views.consumerRegister, name='consumer-register'),
    url(r'^home/$', views.index, name='index'),
    url(r'^home/searchdrinks/$', views.search_drinks, name='searchdrinks'),
    url(r'^home/review/(?P<id>[0-9]+)/$', views.createReview, name='create-review'),
    #url(r'^home/profile/$', views.viewProfile, name='view-profile'),
    url(r'^home/supplier/profile/$', views.viewSupplierProfile, name='view-supplier-profile'),
    #url(r'^sellrecipe/$', views.sellRecipe, name='sell-recipe'),
    #url(r'^customerhistory/$', views.customerHistory, name='customer-history'),
    url(r'^recipe/sell/$', views.sellRecipe, name='sell-recipe'),
    url(r'^recipe/editrecipe/(?P<id>[0-9]+)/$', views.editRecipe, name='edit-recipe'),
    url(r'^recipe/buy/(?P<id>[0-9]+)/$', views.buyRecipe, name='buy-recipe'),
   # url(r'^recipe/details/(?P<id>[0-9]+)/$', views.recipeDetails, name='recipe-details'),
    url(r'^recipe/delete/(?P<id>[0-9]+)/$', views.deleteReview, name='delete-review'),
    url(r'^recipe/edit/(?P<id>[0-9]+)/$', views.editReview, name='edit-review'),
    url(r'^ajax/search/recipe/$', views.ajax_search_recipe, name='ajax-search-recipe'),
    url(r'^ajax/available/recipe/$', views.ajax_available_recipe, name='ajax-available-recipe'),
    url(r'^ajax/unavailable/recipe/$', views.ajax_unavailable_recipe, name='ajax-unavailable-recipe'),
    url(r'^review/upvote/(?P<id>[0-9]+)/$', views.review_upvote, name='review-upvote'),
    url(r'^review/downvote/(?P<id>[0-9]+)/$', views.review_downvote, name='review-downvote'),
    url(r'^export/customer/$', views.export_customer, name='export-customer'),
    url(r'^export/supplier/$', views.export_supplier, name='export-supplier'),
    url(r'^recipe/cancel/(?P<id>[0-9]+)/$', views.cancelOrder, name='cancel-order'),
]
