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
        if serializer.is_valid():
            serializer.save(request=request)  
            return Response({"code":"100", "message":"User created successfully", "data": serializer.data})
        return Response({"Invalid":serializer.errors})
    
    