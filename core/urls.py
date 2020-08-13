from django.urls import path 
from .views import (ProcessImage)

app_name = 'core'

urlpatterns = [
    path('imageLine/',ProcessImage.as_view())
]