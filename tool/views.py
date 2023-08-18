from django.shortcuts import render, redirect, get_object_or_404
from .forms import TicketForm, UserRegistrationForm, OperatorProfile, NidanForm, AreaProjectManagerForm
from .models import Ticket, Operator, NidanTicket, AreaProjectManager
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.contrib.auth.decorators import login_required
import requests
from django.contrib import messages
from .forms import UserRegistrationForm
from .decorators import unauthorized_user, allowed_users
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import NidanSolvedSerializer
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
import csv
from django.utils import timezone
import datetime 
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from .utils import daterangeTicketData
from django.utils.timezone import now
@unauthorized_user
def loginuser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.groups.filter(name='apm'):
                    messages.success(request, 'Welcome, you have been logged in successfully.')
                    return redirect('apm_dashboard')
            else:
                    print('Here I am in Operator And Admin Block')
                    messages.success(
                        request, 'Welcome, you have been logged in successfully.')
                    return redirect('index')
        else:
            messages.error(request, 'username or password might be wrong.')
    return render(request, 'credential/login.html')


def logoutuser(request):
    messages.success(request, 'Logout Successfully')
    logout(request)
    return redirect('login')


@allowed_users(allowed_roles=['admin',])
def registeruser(request):
    form = UserRegistrationForm()                                             
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            first = form.cleaned_data.get('first_name')
            last = form.cleaned_data.get('last_name')
            password = form.cleaned_data.get('password1')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            send_mail(
                ('Gloitel Ticketing tool credential of '+first+''+last+'.'),
                str('Hey '+first+''+last+'. Your username is ' +
                    username+' and your password is '+password+'.'+' Login to gloitelticketing.gloitel.in '),
                'gloitelticketing@gmail.com',
                [email],
                fail_silently=False,
            )
            messages.success(
                request, 'Account Created Successfully For '+first+' '+last+', Mail has been sent.')
            return redirect('index')
    dic = {
        'user_form': form,
    }
    return render(request, 'credential/register.html', dic)

@login_required(login_url='login')
@allowed_users(allowed_roles=['apm',])
def apmDashboard(request): 
    
    return render(request,'ticket/APM/dashboardAPM.html')


@login_required(login_url='login')
@allowed_users(allowed_roles=['operator'])
def userSettings(request):
    operator_id = request.user
    operator = Operator.objects.get(user=operator_id)
    form = OperatorProfile(instance=operator)
    if request.method == 'POST':
        form = OperatorProfile(request.POST, request.FILES, instance=operator)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Your profile has been updated successfully.')
        else:
            messages.error(request, 'Something went wrong.')
    dic = {
        'form': form,
    }
    return render(request, 'ticket/userprofile.html', dic)


# Nidan flows starts from here
@login_required(login_url='login')
# @allowed_users(allowed_roles=['operator'])
def api_nidan(request):  # to retrive all the nidan api data and store it in to the data base if data already exsists it drop the save function and if new data will arrive it will take the data as pending data and save it into the data base.
    message_flag = None
    try:
        url = 'https://uat3.cgg.gov.in/cggrievancemmu/getDocketDetails'
        # url = 'https://cggrievancemmu.cgg.gov.in/getDocketDetails'
        response = requests.get(url)
        data = response.json()
        response_data = data['data']
        for glpi_client in response_data:
            client = NidanTicket(
                docket_number=glpi_client['docketNo'],
                citizen_name=glpi_client['citizenName'],
                phone=glpi_client['phone'],
                address=glpi_client['address']+' '+glpi_client['houseNo']+' ' +
                glpi_client['colonyName']+' '+glpi_client['districtName'],
                email=glpi_client['email'],
                municipality=glpi_client['municipality'],
                section=glpi_client['section'],
                message=glpi_client['message'],
                subsection=glpi_client['subsection'],
                status=glpi_client['status'],
                call_start = glpi_client['callStart'],
                grievance_remark=glpi_client['grievanceRemarks'],
            )
            try:
                client.save()
                message_flag = True
            except:
                message_flag = False
    except:
        pass
    if message_flag == True:
        messages.success(request, 'New data is arrived')
    else:
        messages.warning(
            request, 'All data have been fatched from the Nidan Api')
    nidan_ticket = NidanTicket.objects.all()
    query = request.GET.get('query') if request.GET.get(
        'query') != None else ''
    nidan_tickets = nidan_ticket.filter(
        Q(docket_number__icontains=query)
    )
    dic = {
        'nidan_tickets': nidan_tickets,
    }
    return render(request, 'ticket/nidan_all_tickets.html', dic)


@login_required(login_url='login')
def generateNidanExcel(request):
    response = HttpResponse(content='')
    date = timezone.datetime.now()
    print(date)
    response['Content-Disposition']='attechment; filename="TicketList.csv"'
    writer = csv.writer(response)
    writer.writerow([date,])
    header = ['docket_number','citizen_name','phone','address','email','municipality','section','message','status','grievance_remark','remark','created_date','updated_date']
    writer.writerow(header)
    nidan_ticket = NidanTicket.objects.all()
    tickets = nidan_ticket.values_list('docket_number','citizen_name','phone','address','email','municipality','section','message','status','grievance_remark','remark','created_date','updated_date')
    for item in tickets:
        writer.writerow(item)
    return response


@login_required(login_url='login')
def nidanTicketData(request, pk):
    nidan_instance = get_object_or_404(NidanTicket, id=pk)
    nidan_form = NidanForm(request.POST or None, instance=nidan_instance)
    if nidan_form.is_valid():
        nidan_form_status = nidan_form.save(commit=False)
        if nidan_form_status.status == 'solved':
            nidan_form_status.save()
            messages.success(request, 'Docket for ' +
                             str(nidan_instance)+" is solved now.")
            return redirect('api_nidan')
        else:
            messages.warning(request, 'No changes detacted.')
    dic = {
        'nidan_form': nidan_form,
        'nidan_instance': nidan_instance,
    }
    return render(request, 'ticket/nidan_form.html', dic)


@login_required(login_url='login')
def nidan_pending_data(request):
    nidan_tickets = NidanTicket.objects.filter(status='pending')
    dic = {
        'nidan_tickets': nidan_tickets,
    }
    return render(request, 'ticket/nidan_pending_tickets.html', dic)


# to show all the solved data of the nidan api
@login_required(login_url='login')
def nidan_solved_data(request):
    nidan_tickets = NidanTicket.objects.filter(status='solved')
    dic = {
        'nidan_tickets': nidan_tickets,
    }
    return render(request, 'ticket/nidan_solved_tickets.html', dic)


# to search docket number.
@login_required(login_url='login')
def nidan_search(request):
    query = request.GET.get('query') if request.GET.get(
        'query') != None else ''
    nidan_tickets = NidanTicket.objects.filter(
        Q(docket_number__icontains=query))
    dic = {
        'nidan_tickets': nidan_tickets,
    }
    return render(request, 'ticket/nidan_all_tickets.html', dic)


# this api will return all the sovled docket number
@api_view(['GET'])
def nidanSolvedList(request):
    nidansolved = NidanTicket.objects.filter(status='solved')
    print(nidansolved)
    nidanserializer = NidanSolvedSerializer(nidansolved, many=True)
    return Response(nidanserializer.data)


# this api will return selected sovled docket number
@api_view(['GET'])
def nidanSolvedDetail(request, dcnum):
    Nidansolvedticket = NidanTicket.objects.get(docket_number=dcnum)
    nidanserializer = NidanSolvedSerializer(Nidansolvedticket, many=False)
    return Response(nidanserializer.data)


@login_required(login_url='login')
def searchnidan(request):
    nidan_ticket = NidanTicket.objects.all()
    query = request.GET.get('query') if request.GET.get(
        'query') != None else ''
    tickets = nidan_ticket.filter(
        Q(docket_number__icontains=query)
    )
    return render(request, 'ticket/nidan_all_tickets.html', {'tickets': tickets})

# this is the home page of ticketing tool webapplication allowed user for this page are admin and operator.


@login_required(login_url='login')
@allowed_users(allowed_roles=['operator', 'admin','apm'])
def index(request):
    if str(request.user.groups.all()[0]) == 'apm':
        print('Hey')
        return redirect('apm_dashboard')
    if str(request.user.groups.all()[0]) == 'admin':
        tickets = Ticket.objects.all()
        total_ticket = tickets.count()
        ticket_open = tickets.filter(status='Open').count()
        ticket_reopened = tickets.filter(status='Reopened').count()
        ticket_resolved = tickets.filter(status='Resolved').count()
        ticket_closed = tickets.filter(status='Closed').count()
    elif str(request.user.groups.all()[0]) == 'operator':
        tickets = request.user.ticket_operator.ticket_set.all()    
        total_ticket = tickets.count()
        ticket_open = tickets.filter(status='Open').count()
        ticket_reopened = tickets.filter(status='Reopened').count()
        ticket_resolved = tickets.filter(status='Resolved').count()
        ticket_closed = tickets.filter(status='Closed').count()
    else:
        print('wrong')
    nidan_tickets = NidanTicket.objects.all().count()
    nidan_pending = NidanTicket.objects.filter(status='pending').count()
    nidan_solved = NidanTicket.objects.filter(status='solved').count()
    data = {
        'ticket_open': ticket_open,
        'ticket_closed': ticket_closed,
        'total_ticket': total_ticket,
        'ticket_reopened': ticket_reopened,
        'ticket_resolved': ticket_resolved,
        'nidan_tickets': nidan_tickets,
        'nidan_pending': nidan_pending,
        'nidan_solved': nidan_solved,
    }
    return render(request, 'ticket/home.html', data)


@login_required(login_url='login')
@allowed_users(allowed_roles=['operator'])
def createTicket(request):
    ticket_form = TicketForm()
    if request.method == 'POST':
        ticket_form = TicketForm(request.POST, request.FILES)
        typeofproblem = request.POST.get('type_of_problem')
        category = request.POST.get('category')
        print(typeofproblem+' '+category)
        if ticket_form.is_valid():
            new_form = ticket_form.save(commit=False)
            new_form.created_by = request.user.ticket_operator
            new_form.save()
            messages.success(request, 'Ticket created succfully for ' +
                             str(new_form.full_name+'.'))
            return redirect('create_ticket')
    return render(request, 'ticket/ticket.html', {'ticket_form': ticket_form})


def deleteTicket(request):
    pass


@login_required(login_url='login')
@allowed_users(allowed_roles=['operator'])
def updateTicket(request, pk):
    ticket = Ticket.objects.get(id=pk)
    ticket_form = TicketForm(instance=ticket)
    if request.method == 'POST':
        ticket_form = TicketForm(request.POST, request.FILES,instance=ticket)
        if ticket_form.is_valid():
            new_form = ticket_form.save(commit=False)
            new_form.created_by = request.user.ticket_operator
            new_form.save()
            messages.success(request, 'Ticket updated succfully for ' + str(new_form.full_name+'.'))
            return redirect('all_tickets')
    return render(request, 'ticket/ticket.html', {'ticket_form': ticket_form})



@login_required(login_url='login')
@allowed_users(allowed_roles=['operator', 'admin'])
def allTicket(request):
    tickets = []
    query = request.GET.get('query') if request.GET.get(
        'query') != None else ''
    page_number = request.GET.get('page', 1)
    date = request.GET.get('date') if request.GET.get('date') != None else ''
    if str(request.user.groups.all()[0]) == 'admin':
        tickets_object = Ticket.objects.all()
    if str(request.user.groups.all()[0]) == 'operator':
        tickets_object = request.user.ticket_operator.ticket_set.all()
    if query:
        tickets = tickets_object.filter(
            Q(contact__icontains=query) |
            Q(full_name__icontains=query)
        )
    elif date:
        tickets = tickets_object.filter(
            Q(create_date__lte=query))
    else:
        tickets = tickets_object.filter(
            Q(contact__icontains=query) |
            Q(full_name__icontains=query)
        )
    paginator = Paginator(tickets, 10)
    try:
        tickets = paginator.page(page_number)
    except PageNotAnInteger:
        tickets = paginator.page(1)
    except EmptyPage:
        tickets = paginator.page(paginator.num_pages)
    return render(request, 'ticket/alltickets.html', {'tickets': tickets, })


@login_required(login_url='login')
def openticketslist(request):
    if str(request.user.groups.all()[0]) == 'admin':
        tickets = tickets = Ticket.objects.filter(status='Open')
    if str(request.user.groups.all()[0]) == 'operator':
        tickets = request.user.ticket_operator.ticket_set.filter(status='Open')
    page_number = request.GET.get('page', 1)
    paginator = Paginator(tickets, 10)
    try:
        tickets = paginator.page(page_number)
    except PageNotAnInteger:
        tickets = paginator.page(1)
    except EmptyPage:
        tickets = paginator.page(paginator.num_pages)
    dic = {
        'tickets': tickets,
    }
    return render(request, 'ticket/open_tickets.html', dic)


@login_required(login_url='login')
def reopenticketslist(request):
    if str(request.user.groups.all()[0]) == 'admin':
        tickets = tickets = Ticket.objects.filter(status='Reopened')
    if str(request.user.groups.all()[0]) == 'operator':
        tickets = request.user.ticket_operator.ticket_set.filter(
            status='Reopened')
    page_number = request.GET.get('page', 1)
    paginator = Paginator(tickets, 10)
    try:
        tickets = paginator.page(page_number)
    except PageNotAnInteger:
        tickets = paginator.page(10)
    except EmptyPage:
        tickets = paginator.page(paginator.num_pages)
    dic = {
        'tickets': tickets,
    }
    return render(request, 'ticket/reopen_tickets.html', dic)


@login_required(login_url='login')
def resolvedticketslist(request):
    if str(request.user.groups.all()[0]) == 'admin':
        tickets = tickets = Ticket.objects.filter(status='Resolved')
    if str(request.user.groups.all()[0]) == 'operator':
        tickets = request.user.ticket_operator.ticket_set.filter(
            status='Resolved')
    page_number = request.GET.get('page', 1)
    paginator = Paginator(tickets, 10)
    try:
        tickets = paginator.page(page_number)
    except PageNotAnInteger:
        tickets = paginator.page(1)
    except EmptyPage:
        tickets = paginator.page(paginator.num_pages)
    dic = {
        'tickets': tickets,
    }
    return render(request, 'ticket/resolved_tickets.html', dic)


@login_required(login_url='login')
def closeticketslist(request):
    if str(request.user.groups.all()[0]) == 'admin':
        tickets = tickets = Ticket.objects.filter(status='Closed')
    if str(request.user.groups.all()[0]) == 'operator':
        tickets = request.user.ticket_operator.ticket_set.filter(
            status='Closed')
    page_number = request.GET.get('page', 1)
    paginator = Paginator(tickets, 10)
    try:
        tickets = paginator.page(page_number)
    except PageNotAnInteger:
        tickets = paginator.page(1)
    except EmptyPage:
        tickets = paginator.page(paginator.num_pages)
    dic = {
        'tickets': tickets,
    }
    return render(request, 'ticket/close_tickets.html', dic)


@login_required(login_url='login')
def generateTicketExcel(request):
    print(now())
    response = HttpResponse(content='')
    today = datetime.date.today()
    filname = f"Ticket_Data_{today}.csv"
    response['Content-Disposition'] = f'attechment; filename="{filname}"'
    writer = csv.writer(response)
    header = ['Created By', 'Full Name', 'Category', 'Contact', 'Title', 'Created', 'Updated',
              'Description', 'Status', 'Priority', 'Image', 'Type Of Problem']
    writer.writerow(header)
    if str(request.user.groups.all()[0]) == 'admin':
        tickets = Ticket.objects.all()
    elif str(request.user.groups.all()[0]) == 'operator':
        tickets = request.user.ticket_operator.ticket_set.all()
    else:
        tickets = Ticket.objects.none()
    if request.method == 'POST':
        startdate = request.POST.get('startdate')
        enddate = request.POST.get('enddate')
        if startdate and enddate:
            tickets = daterangeTicketData(request,startdate,enddate)
        else:
            date_range_start = datetime.datetime.now() - datetime.timedelta(days=180)
            tickets = tickets.filter(created__gte=date_range_start)
    for ticket in tickets:
        row = [
            ticket.created_by.first_name if ticket.created_by else '',
            ticket.full_name,
            ticket.category.name if ticket.category else '',
            str(ticket.contact),
            ticket.title,
            ticket.created,
            ticket.updated,
            ticket.description,
            ticket.status,
            ticket.priority,
            str(ticket.image) if ticket.image else '',
            ticket.type_of_problem.name if ticket.type_of_problem else '',
        ]
        writer.writerow(row)
    return response
