from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response

from dj_rest_auth.registration.views import RegisterView
from rest_framework.permissions import AllowAny
from rest_framework import viewsets

from custapp.serializers import CustomerSerializer, FundsSerializer
from custapp.models import Customer, Funds
from CapInvest.pagination_utils import CustomPageNumberPagination
# Create your views here.

class CustomerView(viewsets.ModelViewSet):
    queryset = Customer.objects.none()
    http_method_names = ['get', 'post', 'head']
    permission_class = [AllowAny]
    serializer_class = CustomerSerializer
    pagination_class = CustomPageNumberPagination
    # def get_serializer_class(self):
    #     return CustomerRegisterSerializer
    
    def retrieve(self, request, *args, **kwargs):
        fund = get_object_or_404(Customer, pk=kwargs.get('pk'))
        serializer = self.get_serializer(fund)
        return Response({"msg": "Customer details fetched successfully", "data": serializer.data})
    

class FundsView(viewsets.ModelViewSet):
    queryset = Funds.objects.all()
    http_method_names = ['get', 'post', 'head']
    permission_class = [AllowAny]
    serializer_class = FundsSerializer
    pagination_class = CustomPageNumberPagination
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
        
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Fallback for non-paginated response
        serializer = self.get_serializer(queryset, many=True)
        return Response({"msg": "Fund details fetched successfully", "data": serializer.data})

