from django.urls import path
from . import views

urlpatterns = [
    path('/payu_checkout', views.payu_checkout, name='payu demo')
]