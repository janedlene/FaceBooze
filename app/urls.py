from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^register/supplier/$', views.supplierRegister, name='supplier-register'),
    url(r'^home/producer_profile/(?P<p_id>.+)/$', views.producer_profile, name='producer-profile'),
    url(r'^home/retailer_profile/(?P<p_id>.+)/$', views.retailer_profile, name='retailer-profile'),
    url(r'^home/producer_add_drink/beer/$', views.producer_add_drink_beer, name='producer-add-drink-beer'),
    url(r'^home/producer_add_drink/wine/$', views.producer_add_drink_wine, name='producer-add-drink-wine'),
    url(r'^home/producer_add_drink/liquor/$', views.producer_add_drink_liquor, name='producer-add-drink-liquor'),
    url(r'^home/producer_add_drink/other/$', views.producer_add_drink_other, name='producer-add-drink-other'),
    url(r'^home/producer_delete_drink/(?P<d_id>[0-9]+)/$', views.producer_delete_drink, name='producer-delete-drink'),
    url(r'^home/retailer_add_stock/$', views.retailer_add_stock, name='retailer-add-inv'),
    url(r'^home/retailer_delete_stock/(?P<d_id>[0-9]+)/$', views.retailer_delete_stock, name='retailer-delete-inv'),
    url(r'^home/$', views.index, name='index'),
]
