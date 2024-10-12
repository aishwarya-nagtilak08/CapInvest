import logging
from datetime import datetime

from django.conf import settings as SETTINGS
from django.db import IntegrityError
from allauth.account.adapter import get_adapter
from rest_framework import serializers

from custapp.models import Customer

logger = logging.getLogger(__name__)

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
    
    def validate_username(self, username):

        errmsg = kb_validate_username(username)
        if errmsg:
            raise serializers.ValidationError(errmsg)
        return username

    def validate_platform(self, platform):
        if platform not in (''):
            raise serializers.ValidationError(
                "Enter Valid platform from Platform List %s" % 'SIGUNP_PLATFORM_CHOICES_LIST')
        return platform

    def validate_partner_code(self, partner_code):

        if partner_code not in (''):
            raise serializers.ValidationError("partner_code Should be %s" % '')

        return partner_code

    def validate_partner_customer_id(self, partner_customer_id):  # to do : if ETB = 1 then partner customer id cannot be "" or 0
        if self.initial_data.get('customer_flag') == "1":
            invalid_partner_customer_id = ['0', '', 'null', 'None', 'none']
            if partner_customer_id in invalid_partner_customer_id:
                error = {'message': f"For ETB customer partner_customer_id can not be empty. {partner_customer_id}",
                         'code': 400,
                         'results': f"Customer {self.initial_data.get('username')} is not register in MF"}
                raise serializers.ValidationError(error)
        return partner_customer_id
    
    def validate_client_id(self,client_id):
        if client_id not in SETTINGS.CLIENT_ID_LIST:
            raise serializers.ValidationError("client_id Should be %s" % SETTINGS.CLIENT_ID_LIST)

        return client_id

    def _update(self, user_obj):

        # This method is written to call update data for existing or new user
        try:
            updated = False
            self.cleaned_data = self.data
            partner_code = self.cleaned_data['partner_code']
            customer_flag = self.cleaned_data['customer_flag']
            partner_customer_id = self.cleaned_data['partner_customer_id']

            if user_obj.platform != self.cleaned_data.get('platform'):
                user_obj.platform = self.cleaned_data.get('platform')
                updated = True

            # TO Do NTB in bfl if bfl NTB changes to ETB few days later , shall we update again in register
            # cust falg and partner cust flag not matching and it was earlier 0  for BFDL and BFL
            # In case of ETB , then do not change partner_customer_id
            partner_code = partner_code.upper()
            if partner_code == "BFL":
                if user_obj.partner_customer_flag != customer_flag and customer_flag == "1":
                    user_obj.partner_customer_flag = customer_flag
                    user_obj.partner_customer_id = partner_customer_id
                    user_obj.partner_code = partner_code
                    updated = True

                # if it is NTB then bfdl will give or bfl will give falg to be used to set cust_reference_id
                if user_obj.partner_customer_flag != customer_flag and customer_flag == "0":
                    user_obj.partner_customer_ref_id = partner_customer_id
                    user_obj.partner_customer_flag = customer_flag
                    user_obj.partner_code = partner_code
                    updated = True

            if partner_code == "BFDL":
                if user_obj.bfdl_customer_flag is None:
                    user_obj.bfdl_customer_flag = customer_flag
                    if  customer_flag == "1":
                        user_obj.bfdl_applicant_id = partner_customer_id
                    user_obj.partner_code = partner_code
                    updated = True
                if user_obj.bfdl_customer_flag != customer_flag and customer_flag == "1":
                    user_obj.bfdl_customer_flag = customer_flag
                    user_obj.bfdl_applicant_id = partner_customer_id
                    user_obj.partner_code = partner_code
                    updated = True
            
            if partner_code in ['BFLWEB', 'BFDLWEB']:
                user_obj.partner_code = partner_code
                updated = True
                
            if updated:
                user_obj.modified_by = self.cleaned_data.get("username")
                user_obj.partner_code = partner_code
                user_obj.digio_flow = self.cleaned_data.get('digio_flow')
                user_obj.save()

        except IntegrityError as interr:
            fed_data = f"""username :{self.cleaned_data['username']}, partner_code :{partner_code}, partner_customer_id : {partner_customer_id},
                                                platform :{self.cleaned_data.get('platform')}, customer_flag : {customer_flag}"""
            error = {'message': interr, 'code': 400,
                     'results': "%s not updated successfully" % user_obj.username,
                     'username': user_obj.username}
            logger.warning(f"""Register_serializer - In update - federated_data : {fed_data}""")
            return error
        
        return user_obj

    def save(self, request):
        adapter = get_adapter()
        self.cleaned_data = self.data
        # If we are not setting it then email goes as None
        # None email give error from rest auth framework about NON Null constraint violation
        self.cleaned_data['email'] = ''
        partner_code = self.cleaned_data['partner_code']
        partner_customer_id = self.cleaned_data['partner_customer_id']
        username = self.cleaned_data['username']
        customer_flag = self.cleaned_data['customer_flag']

        exiting_cust = []
        partner_code = partner_code.upper()
        if customer_flag == "1":
            if partner_code == "BFL":
                exiting_cust = Customer.objects.filter(partner_customer_id=partner_customer_id)

            if partner_code == "BFDL":
                exiting_cust = Customer.objects.filter(bfdl_applicant_id=partner_customer_id)

        if len(exiting_cust) > 0:
            cust_user = exiting_cust[0].username
            if cust_user != username:
                error = "Username %s is register for %s partner customer Id with partner_code %s" % (
                cust_user, partner_customer_id, partner_code)
                return error
        else:
            exiting_cust = Customer.objects.filter(username=username)

        if len(exiting_cust) == 0:
            user_obj = adapter.new_user(request)
            try:
                if partner_code == "BFL":
                    user_obj.partner_customer_flag = customer_flag
                    # source_customer_id nee to change to partner_customer_id
                    # chandni will give logic to set customer refrence TODO : ASHWINI
                    if customer_flag == "0":  # if it is NTB then bfdl will give or bfl will give falg to be used to set cust_reference_id
                        user_obj.partner_customer_ref_id = partner_customer_id
                    elif customer_flag == "1":
                        user_obj.partner_customer_id = partner_customer_id

                if partner_code == "BFDL" :
                    user_obj.bfdl_customer_flag = customer_flag
                    if customer_flag == "1":
                        user_obj.bfdl_applicant_id = partner_customer_id

                user_obj.pan_number = username
                user_obj.date_of_birth = datetime.strptime(self.cleaned_data.get('date_of_birth'), "%d/%m/%Y").strftime("%Y-%m-%d")
                user_obj.datetime_when_mobile_registered = datetime.now()
                user_obj.created_by = request.data.get("username")
                user_obj.partner_code = partner_code
                user_obj.mobilenumber = self.cleaned_data.get('mobilenumber')  # Additional custom field 1 for our app
                user_obj.platform = self.cleaned_data.get('platform')
                user_obj.source = self.cleaned_data.get('source')
                user_obj.arn = self.cleaned_data.get('arn')
                user_obj.ownerid = self.cleaned_data.get('ownerid')
                user_obj.client_id = self.cleaned_data.get('client_id')
                user_obj.digio_flow = self.cleaned_data.get('digio_flow')
                user_obj.is_transaction_allowed = self.cleaned_data.get('is_transaction_allowed')
                user = adapter.save_user(request, user_obj, self)
                is_new = True

            except IntegrityError as interr:
                fed_data = f"""username :{username}, partner_code :{partner_code}, partner_customer_id : {partner_customer_id},
                                                        platform :{self.cleaned_data.get('platform')}, customer_flag : {customer_flag}"""
                error = {'message': "%s not created successfully" % str(interr), 'code': 500,
                         'results': "%s not created successfully" % str(interr),
                         'username':username}
                logger.warning(f"user creation dict for save in register api : {user_obj.__dict__}")
                logger.warning(f"""Register_serializer - In save - federate_date : {fed_data}""")
                logger.warning(f"Exception while create new customer : {interr}")
                logger.warning(f"Exception while create new customer error : {error}")
                return error

        else:
            user_obj = self._update(exiting_cust[0])
            is_new = False

        return is_new,user_obj
    
    
def kb_validate_username(username):
    if len(username) < SETTINGS.ACCOUNT_USERNAME_MIN_LENGTH:
        return ("Pan number for user should have atleast %s digits. You have passed %s digits." % (
            SETTINGS.ACCOUNT_USERNAME_MIN_LENGTH, len(username)))
    if len(username) > SETTINGS.ACCOUNT_USERNAME_MAX_LENGTH:
        return ("Pan number for user cannot have more than %s digits. You have passed %s digits." % (
            SETTINGS.ACCOUNT_USERNAME_MAX_LENGTH, len(username)))
    # if username.isdigit() == False:
    #     return ("Mobile number for user cannot have Characters. You have passed %s digits." % (
    #         username))
    return None