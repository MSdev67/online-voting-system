from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.voter_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('otp-verify/', views.otp_verify, name='otp_verify'),
    path('vote/', views.vote, name='vote'),
    path('results/', views.results, name='results'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),  # Add this line
]