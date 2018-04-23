from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^register/consumer/$', views.consumerRegister, name='consumer-register'),
    url(r'^home/$', views.index, name='index'),
    url(r'^home/searchdrinks/$', views.search_drinks, name='search-drinks'),
    url(r'^home/addtofavs/(?P<d_id>[0-9]+)/$', views.addToFavorites, name='add-to-favorites'),
    url(r'^home/deletefromfavs/(?P<d_id>[0-9]+)/$', views.removeFromFavorites, name='delete-from-favorites')
]
