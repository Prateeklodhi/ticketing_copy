from django.contrib import admin
from .models import Ticket,Operator,NidanTicket,AreaProjectManager,TypeOfProblem,Category,City,MMU
from django.forms import ModelForm
from phonenumber_field.widgets import PhoneNumberPrefixWidget
# Register your models here.
admin.site.register(Operator)
admin.site.register(NidanTicket)
admin.site.register(AreaProjectManager)
admin.site.register(TypeOfProblem)
admin.site.register(Category)
admin.site.register(MMU)
admin.site.register(City)

class CallerForm(ModelForm):
    class Meta:
        widgets = {
            'phone':PhoneNumberPrefixWidget(initial='IN'),
        }


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    form = CallerForm