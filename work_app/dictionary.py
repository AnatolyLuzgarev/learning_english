
__author__ = "an.luzgarev"

"""
This module contains functions for working with the dictionary
"""

import os
import json

import my_site.settings as settings_set
from .models import Word
from .models import WordTraining
from work_app.logs import log

def get_words(letter=None, user=None):
	if letter == None:
		selection = Word.objects.all().values()
	elif letter == "training":
		selection = WordTraining.objects.filter(user=user)
		words = [row.word for row in selection]
		selection = [{'word': row.word, 'translation': row.translation, 'transcription':row.transcription} for row in words] 
	else:
		selection = Word.objects.filter(first_letter=letter).values()
	return selection


def add_words_to_training(words_to_training, user):
	list_id = json.loads(words_to_training)
	words_str = ""
	for word_id in list_id:
		word = Word.objects.get(id=word_id)
		words_str = words_str + ", " + word.word
		word_training = WordTraining(word=word, user=user)
		word_training.save()
	words_str = words_str[2:]
	event = "added words: {} to training".format(words_str)
	log(user,event)
	
	
def get_letters_list():
	a_ord = ord("A")
	z_ord = ord("Z")
	letters_list = [chr(i) for i in range(a_ord, z_ord+1)]
	return letters_list


def save_picture_on_server(binary_data, word, translation):
	dirname = os.path.join(settings_set.BASE_DIR, r"my_site/static_files/words_pictures")
	basename = "{}_{}.jpg".format(word, translation).replace(" ", "_")
	file_name = os.path.join(dirname, basename) 
	with open(file_name,'wb') as fw:
		fw.write(binary_data)