from django import forms
from .models import Topic


class TopicForm(forms.ModelForm):
	class Meta():
		model = Topic
		fields = ['topic','paragraph','subject']
		labels = {
		'topic': "Topic",
		'paragraph': "Paragraph",
		'subject': "Subject"
		}