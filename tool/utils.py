from .models import Ticket

def daterangeTicketData(request,startdate,enddate):
    tickets = Ticket.objects.filter(created__range=[startdate,enddate])
    print(tickets)
    return tickets