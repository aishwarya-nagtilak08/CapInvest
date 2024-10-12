import logging
from datetime import datetime

from django.conf import settings as SETTINGS
from django.db import IntegrityError
from allauth.account.adapter import get_adapter
from rest_framework import serializers
from rest_auth.serializers import PasswordChangeSerializer

from custapp.models import Customer

logger = logging.getLogger(__name__)

class CustomerPasswordChangeSerializer(PasswordChangeSerializer):
    def validate_old_password(self, value):
        if self.user.is_password_set:
            value = super(CustomerPasswordChangeSerializer, self).validate_old_password(value)
        else:
            self.user.is_password_set = True
            self.user.save()
        return value


