#Importing standart django tools
import random

from django.db import models
from django.db import connection
from django.http import HttpResponse
#Create your views here.
from rest_framework.response import Response 
from rest_framework.views import APIView

from work_app.models import Word
from work_app.models import GrammarRule
from work_app.models import UserEssay
from work_app.models import Topic
from work_app.views import log
from work_app.views import get_user_log
from .serializers import TopicSerializer
from .serializers import WordSerializer
from .serializers import GrammarSerializer
from .serializers import EssaySerializer


class Translation(APIView):
	def get(self,request,word):
		objects = Word.objects.filter(word = word).values("id","translation","transcription")
		return Response({'translation':objects})


class Training(APIView):
	def get(self,request):
		if request.user.is_authenticated:
			to_training = request.GET.get("to_training", False)
			letter = request.GET.get("first_letter", "all")
			quantity = int(request.GET.get("amount", 10))
			user = request.user
			words = self.get_array_of_words(letter, quantity, to_training, user)
			return Response(words)
		else:
			letter = request.GET.get("first_letter", "all")
			amount = int(request.GET.get("amount", 10))
			if letter == "all":
				objects = models.Word.objects.all()	
			else:
				objects = models.Word.objects.filter(first_letter=letter)
			objects_list = list(objects)
			sample_amount = min(amount,len(objects_list))
			sample = random.sample(objects_list,sample_amount)
			data = WordSerializer(sample, many=True).data
		return Response({'words': data})
	
	def get_array_of_words(self, letter, quantity, training_words=False, user=None):
		total_array = []
		if training_words:
			with connection.cursor() as cursor:
				query = """SELECT
				work_app_word.word AS word,
				work_app_word.translation AS translation,
				work_app_word.transcription AS transcription,
				work_app_word.id AS id
				FROM
				work_app_word 
				INNER JOIN
				wordtraining
				ON work_app_word.id = wordtraining.word_id
				WHERE wordtraining.user_id = %s 
				"""
				if letter == "all":
					cursor.execute(query, [user.id])
				else:
					query = query + " AND work_app_word.first_letter = %s"
					cursor.execute(query,[user.id, letter])
				selector = cursor.fetchall()
				for x in selector:
					word = {'word': x[0], 'translation': x[1], 'transcription': x[2],'id': x[3]}
					total_array.append(word)
		else:
			if letter == "all":
				selection = Word.objects.all().values()
			else:
				selection = Word.objects.filter(first_letter=letter).values()
			total_array = [x for x in selection]
		random.shuffle(total_array)
		total_array = total_array[0:min(quantity, len(total_array))]
		return total_array


class Topics(APIView):
	def get(self, request):
		objects = Topic.objects.all()
		serializer = TopicSerializer(objects, many=True)
		return Response({'objects': serializer.data})
	
	def post(self, request):
		topic = request.data.get('topic')
		serializer = TopicSerializer(data=topic)
		if serializer.is_valid(raise_exception=True):
			serializer.save()
		return Response("Article is saved!")


class Grammar(APIView):
	def get(self, request):
		grammar_rules = GrammarRule.objects.all()
		data = GrammarSerializer(grammar_rules, many=True).data
		return Response(data)
		
	
class Essay(APIView):
	def get(self, request):
		if request.user.is_authenticated:
			selection = self.get_essays_list(request.user)
			data = EssaySerializer(selection, many=True).data
			return Response(data)
	
	def get_essays_list(self, user):
		selection = UserEssay.objects.filter(user=user)
		return selection

	
class Log(APIView):
	def get(self, request):
		user = request.user
		log = self.get_user_log(user)
		return Response(log)
	
	def post(self, request):
		if request.user.is_authenticated:
			user = request.user
			text = request.POST.get("log_text", "")
			log(user,text)
			return HttpResponse(status=200)
	
	def get_user_log(self, user):
		log = get_user_log(user)
		return log
			
			
