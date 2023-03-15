from django.shortcuts import render, redirect, get_object_or_404
from .forms import TicketForm, UserRegistrationForm, OperatorProfile, NidanForm, AreaProjectManagerForm
from .models import Ticket, Operator, NidanTicket, AreaProjectManager
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.contrib.auth.decorators import login_required
import requests
from django.contrib import messages
from .forms import UserRegistrationForm
from .decorators import unauthorized_user, allowed_users, admin_only
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import NidanSolvedSerializer
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
import weasyprint
import datetime
# Create your views here.
@unauthorized_user
def loginuser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.groups.filter(name='apm'):
                    print('Here I am in APM Block')
                    messages.success(
                        request, 'Welcome, you have been logged in successfully.')
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
                    username+' and your password is '+password+'.'+' Login to 192.168.1.7:8000'),
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
    response_data = None
    if request.method == 'GET':
        url = 'https://uat3.cgg.gov.in/cggrievancemmu/getDocketDetails'
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
                grievance_remark=glpi_client['grievanceRemarks'],
            )
            try:
                client.save()
                message_flag = True
            except:
                message_flag = False
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

# nidan_tickets = NidanTicket.objects.all()
#     data = [
#         'Docket_Number', 'Citizen_Name', 'Phone', 'Address', 'Email', 'Municipality ', 'Section', 'Message', 'Subsection', 'Status', 'Grievance_Remark', 'Callstart', 'Created_Date', 'Updated_Date',
#     ]
#     for nidan_ticket in nidan_tickets:
#         row = [
#             nidan_ticket.phone,
#             nidan_ticket.address,
#             nidan_ticket.email,
#             nidan_ticket.municipality,
#             nidan_ticket.section,
#             nidan_ticket.message,
#             nidan_ticket.subsection,
#             nidan_ticket.status,
#             nidan_ticket.grievance_remark,
#             nidan_ticket.callstart,
#             nidan_ticket.created_date,
#             nidan_ticket.updated_date,
#         ]
#         data.append(row)
#     response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#     response['Content-Disposition'] = 'attachment; filename="my_excel_file.xlsx"'
#     workbook = Workbook()
#     sheet = workbook.active
#     for row in data:
#         sheet.append(row)
#     header_font = Font(bold=True)
#     for col_num in range(1,len(data[0]+1)):
#         col_letter = get_column_letter(col_num)
#         cell = sheet['{}1'.format(col_letter)]
#         cell.font = header_font
#     workbook.save(response)
#     return response

@login_required(login_url='login')
def generate_nidan_all_pdf(request):
    nidan_tickets = NidanTicket.objects.all()
    current_date = datetime.date.today()
    html = render_to_string('ticket/PDFs/nidanPDF.html',{'nidan_tickets':nidan_tickets,'current_date': current_date})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition']=f'filename=nidan.pdf'
    weasyprint.HTML(string=html).write_pdf(response,stylesheets=[weasyprint.CSS(settings.STATIC_ROOT/'css/pdf.css')])
    return response

# @login_required(login_url='login')
# def generatNidanPDF(request):
#     data = NidanTicket.objects.all()
#     context = {'data':data}
#     return render(request,'ticket\my_template.html')

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
        ticket_open = tickets.filter(status=1).count()
        ticket_reopened = tickets.filter(status=2).count()
        ticket_resolved = tickets.filter(status=3).count()
        ticket_closed = tickets.filter(status=4).count()
    elif str(request.user.groups.all()[0]) == 'operator':
        tickets = request.user.ticket_operator.ticket_set.all()    
        total_ticket = tickets.count()
        ticket_open = tickets.filter(status=1).count()
        ticket_reopened = tickets.filter(status=2).count()
        ticket_resolved = tickets.filter(status=3).count()
        ticket_closed = tickets.filter(status=4).count()
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
        ticket_form = TicketForm(request.POST)
        if ticket_form.is_valid():
            new_form = ticket_form.save(commit=False)
            new_form.created_by = request.user.ticket_operator
            new_form.save()
            messages.success(request, 'Ticket created succfully for ' +
                             str(new_form.first_name+" "+new_form.last_name+'.'))
            return redirect('all_tickets')
    return render(request, 'ticket/ticket.html', {'ticket_form': ticket_form})


def deleteTicket(request):
    pass


@login_required(login_url='login')
@allowed_users(allowed_roles=['operator'])
def updateTicket(request, pk):
    ticket = Ticket.objects.get(id=pk)
    ticket_form = TicketForm(instance=ticket)
    if request.method == 'POST':
        ticket_form = TicketForm(request.POST, instance=ticket)
        if ticket_form.is_valid():
            new_form = ticket_form.save(commit=False)
            new_form.created_by = request.user.ticket_operator
            new_form.save()
            messages.success(request, 'Ticket updated succfully for ' + str(new_form.first_name+" "+new_form.last_name+'.'))
            return redirect('all_tickets')
    return render(request, 'ticket/ticket.html', {'ticket_form': ticket_form})


@login_required(login_url='login')
@allowed_users(allowed_roles=['operator', 'admin'])
def allTicket(request):
    if str(request.user.groups.all()[0]) == 'admin':
        tickets_object = Ticket.objects.all()
    if str(request.user.groups.all()[0]) == 'operator':
        tickets_object = request.user.ticket_operator.ticket_set.all()
    query = request.GET.get('query') if request.GET.get(
        'query') != None else ''
    tickets = tickets_object.filter(
        Q(contact__icontains=query) |
        Q(first_name__icontains=query)
    )
    return render(request, 'ticket/alltickets.html', {'tickets': tickets})


@login_required(login_url='login')
def openticketslist(request):
    if str(request.user.groups.all()[0]) == 'admin':
        tickets = tickets = Ticket.objects.filter(status=1)
    if str(request.user.groups.all()[0]) == 'operator':
        tickets = request.user.ticket_operator.ticket_set.filter(status=1)
    dic = {
        'tickets': tickets,
    }
    return render(request, 'ticket/open_tickets.html', dic)


@login_required(login_url='login')
def reopenticketslist(request):
    if str(request.user.groups.all()[0]) == 'admin':
        tickets = tickets = Ticket.objects.filter(status=2)
    if str(request.user.groups.all()[0]) == 'operator':
        tickets = request.user.ticket_operator.ticket_set.filter(status=2)
    dic = {
        'tickets': tickets,
    }
    return render(request, 'ticket/reopen_tickets.html', dic)


@login_required(login_url='login')
def resolvedticketslist(request):
    if str(request.user.groups.all()[0]) == 'admin':
        tickets = tickets = Ticket.objects.filter(status=3)
    if str(request.user.groups.all()[0]) == 'operator':
        tickets = request.user.ticket_operator.ticket_set.filter(status=3)
    dic = {
        'tickets': tickets,
    }
    return render(request, 'ticket/resolved_tickets.html', dic)


@login_required(login_url='login')
def closeticketslist(request):
    if str(request.user.groups.all()[0]) == 'admin':
        tickets = tickets = Ticket.objects.filter(status=4)
    if str(request.user.groups.all()[0]) == 'operator':
        tickets = request.user.ticket_operator.ticket_set.filter(status=4)
    dic = {
        'tickets': tickets,
    }
    return render(request, 'ticket/close_tickets.html', dic)


@login_required(login_url='login')
def generate_ticket_all_pdf(request):
    if str(request.user.groups.all()[0]) == 'admin':
        tickets_object = Ticket.objects.all()
    if str(request.user.groups.all()[0]) == 'operator':
        tickets_object = request.user.ticket_operator.ticket_set.all()
    current_date = datetime.date.today()
    first_name = request.user.first_name
    last_name =request.user.last_name 
    html = render_to_string('ticket/PDFs/ticketPDF.html',{'tickets':tickets_object,'current_date':current_date,'first_name':first_name,'last_name':last_name})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition']=f'filename=tickets.pdf'
    weasyprint.HTML(string=html).write_pdf(response,stylesheets=[weasyprint.CSS(settings.STATIC_ROOT/'css/pdf.css')])
    return response