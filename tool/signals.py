from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from twilio.rest import Client
from .models import Operator,Ticket,AreaProjectManager

def create_operator(sender, instance, created, **kwargs):
    if created:
        if instance.is_staff:
            group = Group.objects.get(name='operator')
            instance.groups.add(group)
            Operator.objects.create(
                user=instance,
                first_name=instance.first_name,
                last_name=instance.last_name,
                email = instance.email,
            )
        else:
            group = Group.objects.get(name='apm')
            instance.groups.add(group)
            AreaProjectManager.objects.create(
                user=instance,
                first_name=instance.first_name,
                last_name=instance.last_name,
                email = instance.email,
            )

post_save.connect(create_operator, sender=User)

# def send_sms_oncreate(sender,instance,created,**kwargs):
#     if created:

#         account_sid = 'ACe9a65538591be3da2da3434acae72c38'
#         auth_token = 'd18bb37f2c51a145d91e4453e742b2ba'
#         client = Client(account_sid,auth_token)

#         message = client.messages.create(
#             to= instance.phonenumber,
#             from_=  ''
#         )

# post_save.connect(send_sms_oncreate, sender=AreaProjectManager)        