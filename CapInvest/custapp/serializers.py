import logging
from datetime import datetime

from django.conf import settings as SETTINGS
from django.db import IntegrityError
from allauth.account.adapter import get_adapter
from rest_framework import serializers
from rest_auth.serializers import PasswordChangeSerializer

from custapp.models import Customer, Funds

logger = logging.getLogger(__name__)

class CustomerPasswordChangeSerializer(PasswordChangeSerializer):
    def validate_old_password(self, value):
        if self.user.is_password_set:
            value = super(CustomerPasswordChangeSerializer, self).validate_old_password(value)
        else:
            self.user.is_password_set = True
            self.user.save()
        return value

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"
    
class FundsSerializer(serializers.ModelSerializer):
    customers = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), many=True, write_only=True)
    class Meta:
        model = Funds
        fields = "__all__"
    
    def create(self, validated_data):
        cutomers = validated_data.pop("customers", [])
        fund = Funds.objects.create(**validated_data)
        fund.customers.set(cutomers)
        return fund
        
