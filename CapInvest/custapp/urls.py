from django.urls import path
from custapp.customer_register_view import CustomerRegistrationView

urlpatterns = [
    path('rest-auth/register/', CustomerRegistrationView.as_view(), name='customer-register'),
]
