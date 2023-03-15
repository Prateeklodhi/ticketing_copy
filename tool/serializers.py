from rest_framework import serializers
from .models import NidanTicket

class NidanSolvedSerializer(serializers.ModelSerializer):
    class Meta:
        model = NidanTicket
        fields = ['id','docket_number','citizen_name','phone','remark','status','created_date','updated_date']