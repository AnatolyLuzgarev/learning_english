import datetime

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

#We are going to create Python model
class Word(models.Model):
    #It is a general class for words we will be learning
    word = models.CharField(max_length=100)
    translation = models.CharField(max_length=300)
    first_letter = models.CharField(max_length=1)
    transcription = models.CharField(max_length=100)
    other_forms = models.CharField(max_length=200)
    example = models.CharField(max_length=500) 
    category = models.CharField(max_length=100) 
    additional = models.CharField(max_length=100) 
    to_training = models.BooleanField(default=False)
	   
    def __str__(self):
        str_repr = "{}/{}/{}".format(self.word, self.translation, self.transcription)
        return str_repr


class WordTraining(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    
    class Meta():
        db_table = "WordTraining"
    
    def __str__(self):
        str_repr = "user: {}, word: {}".format(self.user, self.word)
        return str_repr
		
		
class Topic(models.Model):
    topic = models.CharField(max_length=500)
    paragraph = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    
    def __str__(self):
        return "Topic: {}, paragraph: {}, subject: {}".format(self.topic, self.paragraph, self.subject)


class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField()
    event = models.CharField(max_length=500)
    
    def __str__(self):
        return "{}: {}".format(self.date, self.event)
	
	
class UserSettings(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, unique=True)
	main_theme = models.CharField(max_length=100)
	
	
class EssayTheme(models.Model):
	theme = models.CharField(max_length=500)
	
	def __str__(self):
		return self.theme
	
	
class UserEssay(models.Model):
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	theme = models.ForeignKey(EssayTheme, on_delete=models.CASCADE)
	essay = models.TextField()
	
	def __str__(self):
		return "{}/{}/{}".format(self.user, self.theme, self.essay)
	
	
class UserLog(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	date = models.DateTimeField(default=datetime.datetime.now(), editable=False)
	event = models.CharField(max_length=500)
	
	def __str__(self):
		return "User {} at {} {}".format(self.user, self.date, self.event)
	
	
class WordPicture(models.Model):
	word = models.ForeignKey(Word, on_delete=models.CASCADE)
	url = models.CharField(max_length=1000)
	
	class Meta():
		db_table = "wordpicture"
		
	def __str__(self):
		return "{}: {}".format(self.word.word, self.url)
	
	
class GrammarSection(models.Model):
	name = models.CharField(max_length=200)
	
	def __str__(self):
		return self.name


class GrammarRule(models.Model):
	section = models.ForeignKey(GrammarSection, on_delete=models.CASCADE)
	rule = models.CharField(max_length=200)
	example = models.TextField()
	
	def __str__(self):
		return "{}/{}".format(self.section, self.rule)
	
	
class CalendarTask(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	date = models.DateField(default=datetime.datetime.now)
	training = models.CharField(max_length=100)
	amount = models.IntegerField()

	def __str__(self):
		return "{}/{}/{}/{}".format(self.user, self.date, self.training, self.amount)


class CompletedTask(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	date = models.DateTimeField(default=datetime.datetime.now())	
	training = models.CharField(max_length=100)
	
	def __str__(self):
		return "{}{}{}".format(self.user, self.date, self.training)
	
	
	
	