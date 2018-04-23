from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^register/supplier/$', views.supplierRegister, name='supplier-register'),
    url(r'^home/producer_profile/(?P<p_id>.+)/$', views.producer_profile, name='producer-profile'),
    url(r'^home/$', views.index, name='index'),
]
