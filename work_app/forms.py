from django import forms
from .models import Topic
from django.contrib.auth.models import User


class TopicForm(forms.ModelForm):
	class Meta():
		model = Topic
		fields = ['topic','paragraph','subject']
		labels = {
		'topic': "Topic",
		'paragraph': "Paragraph",
		'subject': "Subject"
		}

class RegisterForm(forms.ModelForm):
	username = forms.CharField(max_length=100)
	password = forms.CharField(max_length=100, widget=forms.PasswordInput)
	email = forms.EmailField()
	
	class Meta():
		model = User
		fields = ['username','password','email']