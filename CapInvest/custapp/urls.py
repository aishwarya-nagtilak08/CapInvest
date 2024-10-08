from django.urls import path
from custapp.views import CustomerRegistrationView

urlpatterns = [
    path('rest-auth/register/', CustomerRegistrationView.as_view(), name='customer-register'),
]
