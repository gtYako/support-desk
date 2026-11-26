from django.conf import settings
from django.db import models

class TicketCategory(models.Model):
    name = models.CharField('Название', max_length=100, unique=True)
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
    def __str__(self): return self.name

class Ticket(models.Model):
    class Status(models.TextChoices):
        NEW='new','Новая'
        IN_PROGRESS='in_progress','В работе'
        CLOSED='closed','Закрыта'
    class Priority(models.TextChoices):
        LOW='low','Низкий'
        MEDIUM='medium','Средний'
        HIGH='high','Высокий'
    category=models.ForeignKey(TicketCategory,verbose_name='Категория',on_delete=models.PROTECT)
    subject=models.CharField('Тема',max_length=200)
    description=models.TextField('Описание')
    priority=models.CharField('Приоритет',max_length=10,choices=Priority.choices,default=Priority.MEDIUM,db_index=True)
    status=models.CharField('Статус',max_length=20,choices=Status.choices,default=Status.NEW,db_index=True)
    applicant=models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name='Заявитель',on_delete=models.PROTECT,related_name='tickets')
    assignee=models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name='Исполнитель',on_delete=models.PROTECT,related_name='assigned_tickets',null=True,blank=True)
    response_due=models.DateTimeField('Срок реакции')
    created_at=models.DateTimeField('Создано',auto_now_add=True,db_index=True)
    updated_at=models.DateTimeField('Обновлено',auto_now=True)
    class Meta:
        verbose_name = 'Обращение'
        verbose_name_plural = 'Обращения'
        constraints=[models.CheckConstraint(condition=models.Q(status__in=['new','in_progress','closed']),name='ticket_status_valid'),models.CheckConstraint(condition=models.Q(priority__in=['low','medium','high']),name='ticket_priority_valid')]
    def __str__(self): return self.subject

class Comment(models.Model):
    ticket=models.ForeignKey(Ticket,verbose_name='Обращение',on_delete=models.CASCADE,related_name='comments')
    author=models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name='Автор',on_delete=models.PROTECT)
    text=models.TextField('Комментарий')
    created_at=models.DateTimeField('Создано',auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

class TicketEvent(models.Model):
    ticket=models.ForeignKey(Ticket,verbose_name='Обращение',on_delete=models.CASCADE,related_name='events')
    user=models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name='Пользователь',on_delete=models.PROTECT)
    old_status=models.CharField('Прежний статус',max_length=20,choices=Ticket.Status.choices)
    new_status=models.CharField('Новый статус',max_length=20,choices=Ticket.Status.choices)
    created_at=models.DateTimeField('Создано',auto_now_add=True)

    class Meta:
        verbose_name = 'Событие обращения'
        verbose_name_plural = 'События обращений'
