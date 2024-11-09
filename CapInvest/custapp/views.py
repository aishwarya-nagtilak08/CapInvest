from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response

from dj_rest_auth.registration.views import RegisterView
from rest_framework.permissions import AllowAny
from rest_framework import viewsets

from custapp.serializers import CustomerSerializer, FundsSerializer
from custapp.models import Customer, Funds
# Create your views here.

class CustomerView(viewsets.ModelViewSet):
    queryset = Customer.objects.none()
    http_method_names = ['get', 'post', 'head']
    permission_class = [AllowAny]
    serializer_class = CustomerSerializer
    # def get_serializer_class(self):
    #     return CustomerRegisterSerializer
    
    def retrieve(self, request, *args, **kwargs):
        fund = get_object_or_404(Customer, pk=kwargs.get('pk'))
        serializer = self.get_serializer(fund)
        return Response({"msg": "Customer details fetched successfully", "data": serializer.data})
    

class FundsView(viewsets.ModelViewSet):
    queryset = Funds.objects.none()
    http_method_names = ['get', 'post', 'head']
    permission_class = [AllowAny]
    serializer_class = FundsSerializer
    # def get_serializer_class(self):
    #     return CustomerRegisterSerializer
    
    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg":"Fund details added", "data": serializer.data})
        return Response({"msg":"Something went wrong","data": data})
    
    def retrieve(self, request, *args, **kwargs):
        fund = get_object_or_404(Funds, pk=kwargs.get('pk'))
        serializer = self.get_serializer(fund)
        return Response({"msg": "Fund details fetched successfully", "data": serializer.data})
        
    
