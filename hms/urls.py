from django.contrib import admin
from django.urls import path
from selection import views
from django.conf.urls import include, url
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='register'),
    path('reg_form/', views.register, name='reg_form'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    path('login/', views.user_login, name='login'),
    path('student_profile/', views.student_profile, name='student_profile'),
    path('warden_login/', views.warden_login, name='warden_login'),
    path('warden_login/empty/', views.empty_rooms, name='empty_rooms'),
    path('warden_profile/', views.warden_profile, name='warden_profile'),
    path('warden_dues/', views.warden_dues, name='warden_dues'),
    path('warden_add_due/', views.warden_add_due, name='warden_add_due'),
    path('warden_remove_due/', views.warden_remove_due, name='warden_remove_due'),
    path('hostels/', views.hostels, name='hostel_all'),
    path('hostels/<slug:hostel_name>/', views.hostel_detail_view, name='hostel'),
    path('login/edit/', views.edit, name='edit'),
    path('login/select/', views.select, name='select'),
    path('login/repair/', views.repair, name='repair'),
    path('logout/', views.logout_view, name='logout'),
    path('reg_form/login/edit/', views.edit, name='update'),
    ]
