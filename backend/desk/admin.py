from django.contrib import admin
from .models import Ticket, TicketCategory, Comment, TicketEvent
admin.site.register([Ticket,TicketCategory,Comment,TicketEvent])
