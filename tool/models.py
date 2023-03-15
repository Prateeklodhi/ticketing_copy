from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

class Operator(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,null=True,related_name='ticket_operator')
    first_name = models.CharField(max_length=20,null=True,blank=False)
    last_name = models.CharField(max_length=20,null=True,blank=False)
    profile_pic = models.ImageField(upload_to='ProfilePicture/%y/%m/%d',null= True,blank=True)
    date_created = models.DateTimeField(auto_now_add=True,null=True)
    date_updated = models.DateTimeField(auto_now=True)
    email = models.EmailField(max_length=200,null=True,blank=False)
    
    class Meta:
        ordering = ['date_created']
        indexes = [
            models.Index(fields=['date_created'])
        ]

    def __str__(self) -> str:
        return str(self.user)


class AreaProjectManager(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,null=True,related_name='ticket_APM')
    profile_pic = models.ImageField(upload_to='ProfilePicture/%y/%m/%d',null= True,blank=True)
    first_name = models.CharField(max_length=50,null=True,blank=False)
    last_name = models.CharField(max_length=50,null=True,blank=False)
    phonenumber = PhoneNumberField(region='IN',max_length=13)
    address = models.TextField(null=True,blank=True)
    MMU_name = models.CharField(null=True,blank=True,max_length=50)
    email = models.EmailField(max_length=200,null=True,blank=False)
    date_created = models.DateTimeField(auto_now_add=True,null=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date_created']
        indexes = [
            models.Index(fields=['date_created'])
        ]

    def __str__(self) -> str:
        return str(self.user)



class Ticket(models.Model):
    OPEN_STATUS = 1 
    REOPENED_STATUS = 2
    RESOLVED_STATUS = 3
    CLOSED_STATUS = 4
    DUPLICATE_STATUS = 5

    STATUS_CHOICES = (
        (OPEN_STATUS, _('Open')),
        (REOPENED_STATUS, _('Reopened')),
        (RESOLVED_STATUS, _('Resolved')),
        (CLOSED_STATUS, _('Closed')),
        (DUPLICATE_STATUS, _('Duplicate'))
    )

    PRIORITY_CHOICES = (
        (1, _('Critical')),
        (2, _('High')),
        (3, _('Normal')),
        (4, _('Low')),
        (5, _('Very Low')),
    )

    MMU = 1
    WEBSITE = 2
    TREATMENT = 3
    OTHER = 4

    TYPE_OF_PROBLEM = (
        (MMU,_('MMU')),
        (WEBSITE,_('Website')),
        (TREATMENT,_('Treatment')),
        (OTHER,_('Other')),
    )
    created_by = models.ForeignKey(Operator,on_delete=models.SET_NULL,null=True,blank=True)
    first_name = models.CharField(max_length=25,blank=False,null=False)
    last_name = models.CharField(max_length=25,null=False,blank=False)
    contact = PhoneNumberField(region='IN',max_length=13)
    title = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.IntegerField(choices=STATUS_CHOICES,default=OPEN_STATUS)
    description = models.TextField(null=True,blank=True)
    priority = models.IntegerField(choices=PRIORITY_CHOICES,default=3,blank=3)
    image = models.ImageField(upload_to='TicketProblem/%y/%m/%d/',null=True,blank=True)
    type_of_problem = models.IntegerField(choices=TYPE_OF_PROBLEM,default=OTHER)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['created',])
        ]

    def __str__(self) -> str:
        return self.title+" "+self.first_name+" "+self.last_name


class NidanTicket(models.Model):
    STATUS = (
        ('pending',_('pending')),
        ('solved',_('solved')),
        )
    docket_number = models.CharField(max_length=20,null=True,unique=True)
    citizen_name = models.CharField(max_length=50,null=True)
    phone = models.CharField(max_length=13,null=True)
    address = models.TextField(null=True)
    email = models.EmailField(max_length=100,null=True)
    municipality = models.CharField(max_length=150,null=True)
    section = models.CharField(max_length=150,null=True)
    message = models.TextField(null=True)
    subsection = models.CharField(max_length=50,null=True)
    status = models.CharField(choices=STATUS,null=True,max_length=100,default='pending')
    grievance_remark = models.CharField(max_length=500,null=True)
    remark = models.TextField(null=True,blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['created_date']
        indexes = [
            models.Index(fields=['created_date',])
        ]
    
    def __str__(self) -> str:
        return self.docket_number+' '+self.citizen_name