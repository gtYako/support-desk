from django import forms
from rest_framework import serializers

DEMO_NAMES = {'applicant': 'Заявитель', 'worker': 'Исполнитель', 'admin': 'Администратор'}

def user_label(user):
    return user.get_full_name() or DEMO_NAMES.get(user.username, user.username)

class UserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, user):
        return user_label(user)

class UserRelatedField(serializers.PrimaryKeyRelatedField):
    def display_value(self, user):
        return user_label(user)
