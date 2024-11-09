from django.urls import path, include
from rest_framework.routers import DefaultRouter
from custapp.customer_register_view import CustomerRegistrationView
from .views import CustomerView, FundsView

router = DefaultRouter()
router.register(r'customer', CustomerView, basename="customer")
router.register(r'fund', FundsView, basename="fund")

urlpatterns = [
    path('', include(router.urls)),
    path('rest-auth/register/', CustomerRegistrationView.as_view(), name='customer-register'),
]
