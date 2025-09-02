from django.urls import path
from . import views

urlpatterns = [
    path('async-select-search/', views.async_select_search, name='async_select_search'),
]