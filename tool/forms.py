from django.forms import ModelForm
from .models import Ticket,Operator,NidanTicket,AreaProjectManager,City,MMU
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class AreaProjectManagerForm(ModelForm):
    class Meta:
        model = AreaProjectManager
        fields = '__all__'


class NidanForm(ModelForm):
    class Meta:
        model = NidanTicket
        fields =['status','remark']
        exclude = ['docket_number','citizen_name','phone','address','email','municipality','section','message','subsection','grievance_remark',]
        widgets = {
            'remark':forms.Textarea(attrs={'cols': '60', 'rows': '3','remark':'remark'})
        }


class OperatorProfile(ModelForm):
    class Meta:
        model = Operator
        fields = '__all__'
        exclude = ['user']


class UserRegistrationForm(UserCreationForm):
      class Meta:
        model =User  
        fields = ['username','first_name','last_name','email','is_staff',]
        widgets = {
            
        }

class TicketForm(ModelForm):
    class Meta:
        model = Ticket
        fields = '__all__'
        exclude =['creatd_by',]
        widgets = {
            'description':forms.Textarea(attrs={'cols': '60', 'rows': '3','description':'description'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.fields['mmus'].quertset = MMU.objects.none()

        if 'city' in self.data:
            try:
                city_id = int(self.data.get('city'))
                self.fields['mmus'].queryset = MMU.objects.filter(city_id = city_id).order_by('name')
            except(ValueError,TypeError):
                pass
        elif self.instance.pk:
            self.fields['mmus'].queryset = self.instance.city.mmus_set.order_by('name')
