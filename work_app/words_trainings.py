
__author__ = "an.luzgarev"


import random

from django.db import connection
from .models import Word
from .models import WordTraining


"""
Module contains functions for creating new trainings
"""

def get_array_of_words(letter, quantity, training_words=False, user=None):
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
				word = {'word': x[0],
			            'translation': x[1],
						'transcription': x[2],
						'id': x[3]}
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


def words_of_category(category):
	words_list = []
	words = Word.objects.filter(category=category).distinct()
	for x in words:
		words_list.append(x.word)
	return words_list


def get_list_of_categories():
	categories_list = []
	objects = Word.objects.values("category").distinct()
	for x in objects:
		if x['category'] != 'nan' and x['category'] != 'Phrasal verb':
			categories_list.append(x['category'])
	return categories_list


def get_phrasal_verbs(word):
	query = """SELECT 
	work_app_word.* 
	FROM work_app_word 
	WHERE work_app_word.category =  'Phrasal verb'"""
	selector = Word.objects.raw(query)
	words_array = []
	for x in selector:
		arr = x.word.split(" ")
		if arr[0] == word:
			words_array.append({"word": x.word, "translation": x.translation})
	return words_array
	return words_array


def get_phrasal_verbs_list():
	query = "SELECT work_app_word.* FROM work_app_word WHERE work_app_word.category =  'Phrasal verb'"
	selector = Word.objects.raw(query)
	selector = Word.objects.filter(category='Phrasal verb').distinct()
	words_array = [x.word for x in selector]
	words_array = process_phrasal_verbs_array(words_array)
	words_array = prosses_phrasal_verbs_doubles(words_array)
	return words_array


def process_phrasal_verbs_array(array):
	array_words = []
	for x in array:
		arr = x.split(" ")
		curr_word = arr[0]
		array_words.append(curr_word)
	return array_words


def prosses_phrasal_verbs_doubles(array):
	array_2 = []
	for x in array:
		try:
			array_2.index(x)
		except:
			array_2.append(x)
	return array_2


def get_amount_of_words(letter):
	words = Word.objects.filter(first_letter=letter)
	amount_of_words = len(words)
	return amount_of_words


def process_amount_of_words(request,letter):
	if request.POST.get("words_amount", 0) != 0:
		return get_amount_of_words(letter)
	else:
		return 0


def clear_all_trainings(user=None):
	if user == None:
		WordTraining.objects.all().delete()
	else:
		WordTraining.objects.filter(user_id=user.id).delete()

