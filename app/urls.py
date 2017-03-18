from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^register/supplier/$', views.supplierRegister, name='supplier-register'),
    url(r'^register/customer/$', views.customerRegister, name='customer-register'),
    url(r'^home/$', views.index, name='index'),
]
