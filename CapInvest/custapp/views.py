from django.shortcuts import render

from dj_rest_auth.registration.views import RegisterView
from rest_framework.permissions import AllowAny
# Create your views here.

class CustomerRegistrationView(RegisterView):
    permission_class = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        print(data)