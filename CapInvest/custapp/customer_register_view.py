from django.shortcuts import render
from rest_framework.response import Response

from dj_rest_auth.registration.views import RegisterView
from rest_framework.permissions import AllowAny

from custapp.customer_register_serializer import CustomerRegisterSerializer

class CustomerRegistrationView(RegisterView):
    permission_class = [AllowAny]
    
    def get_serializer_class(self):
        return CustomerRegisterSerializer
    
    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        print(serializer, type(serializer))
        if serializer.is_valid():
            return Response({"data":"data"})
        return Response({"data":data})
    
    