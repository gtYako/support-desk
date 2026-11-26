from django.db import transaction
from django.contrib.auth import get_user_model
from .labels import UserChoiceField
from django.db.models import Q
from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import permissions, viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from .models import Ticket, TicketCategory, TicketEvent
from .serializers import TicketSerializer, CategorySerializer, CommentSerializer, EventSerializer

class UserChoiceFilter(filters.ModelChoiceFilter):
    field_class = UserChoiceField

class TicketFilter(filters.FilterSet):
    assignee = UserChoiceFilter(label='Исполнитель', queryset=get_user_model().objects.all())
    overdue=filters.TypedChoiceFilter(label='Просрочено', choices=(('true','Да'),('false','Нет')), coerce=lambda v:v=='true', method='filter_overdue')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, label in {'status':'Статус', 'category':'Категория', 'priority':'Приоритет', 'assignee':'Исполнитель'}.items():
            self.filters[name].label = label
    def filter_overdue(self,qs,name,value):
        q=Q(status='new',response_due__lt=timezone.now())
        return qs.filter(q if value else ~q)
    class Meta:
        model=Ticket
        fields=('status','category','priority','assignee','overdue')

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset=TicketCategory.objects.all().order_by('id')
    serializer_class=CategorySerializer

class TicketViewSet(viewsets.ModelViewSet):
    serializer_class=TicketSerializer
    filterset_class=TicketFilter
    search_fields=('subject',)
    http_method_names=['get','post','patch','put','head','options']
    def get_queryset(self):
        qs=Ticket.objects.select_related('category','applicant','assignee').order_by('-created_at','-id')
        user=self.request.user
        return qs if user.is_staff else qs.filter(Q(applicant=user)|Q(assignee=user))
    def perform_create(self,serializer): serializer.save(applicant=self.request.user)
    @transaction.atomic
    def update(self,request,*args,**kwargs):
        instance=self.get_queryset().select_for_update().get(pk=self.get_object().pk)
        if not (request.user.is_staff or instance.assignee_id==request.user.id or instance.applicant_id==request.user.id):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied()
        serializer=self.get_serializer(instance,data=request.data,partial=kwargs.pop('partial',False))
        serializer.is_valid(raise_exception=True)
        old=instance.status
        ticket=serializer.save()
        if old != ticket.status: TicketEvent.objects.create(ticket=ticket,user=request.user,old_status=old,new_status=ticket.status)
        return Response(serializer.data)
    @action(detail=True,methods=['get','post'])
    def comments(self,request,pk=None):
        ticket=self.get_object()
        if request.method=='GET':
            return Response(CommentSerializer(ticket.comments.select_related('author').order_by('created_at'),many=True).data)
        if ticket.status=='closed': raise ValidationError({'detail':'Закрытое обращение нельзя комментировать.'})
        serializer=CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(ticket=ticket,author=request.user)
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    @action(detail=True,methods=['get'])
    def events(self,request,pk=None):
        ticket=self.get_object()
        return Response(EventSerializer(ticket.events.select_related('user').order_by('created_at','id'),many=True).data)
