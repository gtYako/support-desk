from django.utils import timezone
from django.contrib.auth import get_user_model
from .labels import UserRelatedField
from rest_framework import serializers
from .models import Ticket, TicketCategory, Comment, TicketEvent

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=TicketCategory
        fields='__all__'

class TicketSerializer(serializers.ModelSerializer):
    assignee = UserRelatedField(queryset=get_user_model().objects.all(), required=False, allow_null=True)
    overdue=serializers.SerializerMethodField()
    class Meta:
        model=Ticket
        fields='__all__'
        read_only_fields=('applicant','created_at','updated_at','overdue')
    def get_overdue(self,obj):
        return obj.status == 'new' and obj.response_due < timezone.now()
    def validate(self, attrs):
        now=timezone.now()
        if 'response_due' in attrs and attrs['response_due'] < (self.instance.created_at if self.instance else now):
            raise serializers.ValidationError({'response_due':'Срок не может быть раньше создания обращения.'})
        user=self.context['request'].user
        if not self.instance:
            if attrs.get('status',Ticket.Status.NEW) != Ticket.Status.NEW:
                raise serializers.ValidationError({'status':'Новая заявка должна иметь статус new.'})
            if attrs.get('assignee') and not user.is_staff:
                raise serializers.ValidationError({'assignee':'Назначение доступно администратору.'})
        else:
            old=self.instance.status
            new=attrs.get('status',old)
            if old == Ticket.Status.CLOSED:
                if not user.is_staff or new != Ticket.Status.IN_PROGRESS or set(attrs) != {'status'}:
                    raise serializers.ValidationError({'status':'Закрытое обращение может открыть только администратор отдельным запросом.'})
            elif new != old and (old,new) not in [('new','in_progress'),('in_progress','closed')]:
                raise serializers.ValidationError({'status':'Недопустимый переход.'})
            if 'assignee' in attrs and not user.is_staff:
                raise serializers.ValidationError({'assignee':'Назначение доступно администратору.'})
            if new != old and not (user.is_staff or self.instance.assignee_id == user.id):
                raise serializers.ValidationError({'status':'Статус меняет исполнитель или администратор.'})
        return attrs

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Comment
        fields=('id','ticket','author','text','created_at')
        read_only_fields=('ticket','author','created_at')

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model=TicketEvent
        fields='__all__'
        read_only_fields=('id','ticket','user','old_status','new_status','created_at')
