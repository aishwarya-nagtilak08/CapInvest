from rest_framework import serializers

class CustomerRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)  # , write_only=True)
    mobilenumber = serializers.CharField(required=True)
    date_of_birth = serializers.DateField(required=True,format="%d/%m/%Y",input_formats=["%d/%m/%Y"], error_messages={"invalid": "Date must be in DD/MM/YYYY format."})
    partner_customer_id = serializers.CharField(required=False, max_length=32)
    partner_code = serializers.CharField(required=False, max_length=16)
    platform = serializers.CharField(required=False, max_length=30)
    customer_flag = serializers.CharField(required=False)
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True, default="")
    client_id = serializers.CharField(required=True,max_length=16)
    digio_flow = serializers.CharField(required=False, allow_null=True, max_length=30)
    is_transaction_allowed = serializers.BooleanField(required=False, allow_null=True)
    arn = serializers.CharField(required=False, max_length=20, allow_null=True, allow_blank=True)
    ownerid = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    source = serializers.CharField(required=False, allow_null=True, allow_blank=True)