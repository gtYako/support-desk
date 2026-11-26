from datetime import timedelta
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APITestCase
from .models import Ticket, TicketCategory, TicketEvent

class TicketTests(APITestCase):
    def setUp(self):
        self.user=User.objects.create_user('user',password='pass')
        self.worker=User.objects.create_user('worker',password='pass')
        self.admin=User.objects.create_superuser('admin',password='pass')
        self.cat=TicketCategory.objects.create(name='Техника')
        self.t=Ticket.objects.create(category=self.cat,subject='Проблема',description='Описание',applicant=self.user,assignee=self.worker,response_due=timezone.now()+timedelta(days=1))
        self.url=f'/api/tickets/{self.t.id}/';self.client.force_authenticate(self.worker)
    def test_list(self): self.assertEqual(self.client.get('/api/tickets/').status_code,200)
    def test_filter(self): self.assertEqual(self.client.get('/api/tickets/',{'priority':'high'}).data['count'],0)
    def test_history(self):
        self.assertEqual(self.client.patch(self.url,{'status':'in_progress'}).status_code,200)
        e=TicketEvent.objects.get();self.assertEqual((e.old_status,e.new_status,e.user),('new','in_progress',self.worker))
        self.assertEqual(len(self.client.get(self.url+'events/').data),1)
    def test_invalid_transition(self): self.assertEqual(self.client.patch(self.url,{'status':'closed'}).status_code,400)
    def test_closed_comment(self):
        self.t.status='closed';self.t.save();self.assertEqual(self.client.post(self.url+'comments/',{'text':'тест'}).status_code,400)
    def test_required_fields(self): self.assertEqual(self.client.post('/api/tickets/',{},format='json').status_code,400)
    def test_comment_author(self):
        r=self.client.post(self.url+'comments/',{'text':'тест','author':self.admin.id},format='json');self.assertEqual(r.status_code,201);self.assertEqual(r.data['author'],self.worker.id)
    def test_deadline(self): self.assertEqual(self.client.patch(self.url,{'response_due':(timezone.now()-timedelta(days=1)).isoformat()}).status_code,400)
    def test_reopen(self):
        self.t.status='closed';self.t.save();self.assertEqual(self.client.patch(self.url,{'status':'in_progress'}).status_code,400)
        self.client.force_authenticate(self.admin);self.assertEqual(self.client.patch(self.url,{'status':'in_progress'}).status_code,200)
    def test_overdue(self):
        self.t.response_due=timezone.now()-timedelta(seconds=1);self.t.save();self.assertEqual(self.client.get('/api/tickets/',{'overdue':'true'}).data['count'],1)
