from datetime import timedelta
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone
from desk.models import Ticket, TicketCategory

class Command(BaseCommand):
    def handle(self,*args,**kwargs):
        if Ticket.objects.exists() or TicketCategory.objects.exists() or User.objects.filter(username__in=['applicant','worker','admin']).exists():
            self.stdout.write('База не пуста, заполнение отменено.'); return
        a=User.objects.create_user('applicant',password='study12345')
        b=User.objects.create_user('worker',password='study12345')
        User.objects.create_superuser('admin','admin@example.test','study12345')
        cats=[TicketCategory.objects.create(name=n) for n in ['Техника','Доступ','Другое']]
        for i in range(12):
            Ticket.objects.create(category=cats[i%3],subject=f'Обращение {i+1}',description='Учебное обращение',applicant=a,assignee=b,response_due=timezone.now()+timedelta(days=i+1))
        self.stdout.write('Созданы 3 категории, 3 пользователя и 12 обращений.')
