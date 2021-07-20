from django.urls import path
from . import views

from rest_framework.authtoken import views as auth_views


urlpatterns = [
    path('login/', views.ObtainAuthTokenView.as_view(), name='api-tokn-auth'),
    path('register/', views.registration_view, name='reg'),
    path('profile/', views.profile, name='profile'),
    path('friends/', views.friends, name='friendds'),
    path('users/', views.users, name='users'),
    path('add-friend/', views.AddFriendView.as_view(), name='add-friend'),
    path('chat/<uri>/', views.ChatView.as_view(), name='chat-friend'),
    path('chat/', views.ChatView.as_view(), name='chat-friend'),
]