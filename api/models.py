from django.db import models

# Create your models here.

#We are going to create Python model
class Word(models.Model):
    #It is a general class for words we will be learning
    word = models.CharField(max_length = 100)
    translation = models.CharField(max_length = 300)
    first_letter = models.CharField(max_length = 1)
    transcription = models.CharField(max_length = 100)
    other_forms = models.CharField(max_length = 200)
    example = models.CharField(max_length = 500) 
    category = models.CharField(max_length = 100) 
    additional = models.CharField(max_length = 100) 
    to_training = models.BooleanField(default = False)
    def __str__(self):
        str_repr = "{}/{}/{}".format(self.word,self.translation,self.transcription)
        return str_repr

class Topic(models.Model):
    topic = models.CharField(max_length = 500)
    paragraph = models.CharField(max_length = 200)
    subject = models.CharField(max_length = 100)
    def __str__(self):
        return "Topic: {}, paragraph: {}, subject: {}".format(self.topic, self.paragraph, self.subject)

class Events(models.Model):
    date = models.DateField()
    event = models.CharField(max_length = 100)
    event_description = models.TextField()
    def __str__(self):
        return "{}: {}".format(self.date,self.event)

