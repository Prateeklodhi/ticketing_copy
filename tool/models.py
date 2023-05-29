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


class TypeOfProblem(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True)
    def __str__(self) -> str:
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True)
    def __str__(self) -> str:
        return self.name

class Ticket(models.Model):
    STATUS_CHOICES = (
        ('Open', _('Open')),
        ('Reopened', _('Reopened')),
        ('Resolved', _('Resolved')),
        ('Closed', _('Closed')),
    )
    PRIORITY_CHOICES = (
        ('Critical', _('Critical')),
        ('High', _('High')),
        ('Normal', _('Normal')),
        ('Low', _('Low')),
        ('Very Low', _('Very Low')),
    )
 
    created_by = models.ForeignKey(Operator,on_delete=models.SET_NULL,null=True,blank=True)
    full_name = models.CharField(max_length=250,blank=False,null=False)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,null=True)
    contact = PhoneNumberField(region='IN',max_length=13)
    title = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(choices=STATUS_CHOICES,default='Open',max_length=60)
    description = models.TextField(null=True,blank=True)
    priority = models.CharField(choices=PRIORITY_CHOICES,default='Normal',max_length=60)
    image = models.ImageField(upload_to='TicketProblem/%y/%m/%d/',null=True,blank=True)
    type_of_problem = models.ForeignKey(TypeOfProblem,on_delete=models.CASCADE,null=True)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['created',])
        ]
        
    def __str__(self) -> str:
        return self.title+" "+self.full_name
    
    def to_dict(self):
        return{
            'created_by': self.created_by.name if self.created_by else '',
            # 'created_by':self.created_by,
            'full_name':self.first_name,
            # 'category':self.category,
            'category': self.category.name if self.category else '',
            # 'contact':self.contact,
            'contact': str(self.contact),
            'title':self.title,
            'created':self.created,
            'updated':self.updated,
            'description':self.description,
            'status':self.status,
            'priority':self.priority,
            # 'image':self.image,
            'image': str(self.image) if self.image else '',
            # 'type_of_problem':self.type_of_problem,
            'type_of_problem': self.type_of_problem.name if self.type_of_problem else '',
        }


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
        return str(self.docket_number+' '+self.citizen_name)

    def to_dict(self):
        return{
           'docket_number':self.docket_number,
           'citizen_name':self.citizen_name,
           'phone':self.phone,
           'address':self.address,
           'email':self.email,
           'municipality':self.municipality,
           'section':self.section,
           'message':self.message,
           'status':self.status,
           'grievance_remark':self.grievance_remark,
           'remark':self.remark,
           'created_date':self.created_date,
           'updated_date':self.updated_date
        }