
__author__ = "an.luzgarev"

"""
Module containts functions for work with pictures
"""

import re
import time
import random

import requests
from .models import WordPicture
from bs4 import BeautifulSoup
from django.db import connection


def get_words_for_pictures():
	with connection.cursor() as cursor:
		query = """SELECT DISTINCT
		work_app_word.word AS word,
		work_app_word.translation AS translation,
		work_app_word.transcription AS transcription,
		work_app_word.id AS id
		FROM
		work_app_word 
		LEFT JOIN
		wordpicture
		ON
		work_app_word.id = wordpicture.word_id
		WHERE wordpicture.word_id IS NULL
		"""
		cursor.execute(query)
		selector = cursor.fetchall()
		words_list = [word for word in selector]
		return words_list


def get_picture_urls(word):
	url_pattern = "https://yandex.ru/images/search?from=tabbar&text={}"
	url = url_pattern.format(word)
	response = requests.get(url)
	text = response.text
	print(text)
	soup = BeautifulSoup(text, 'html.parser')
	elems = soup.select(".serp-controller__content div div")
	pattern = r':"https:[^\:}]*\.jpg"'
	patterner = re.compile(pattern)
	curr_amount = 0
	url_list = []
	for x in elems:
		results = patterner.findall(str(x))
		if len(results) > 0:
			url_list = [*url_list,results[0][2:-1]]
			curr_amount = curr_amount + 1
		else:
			continue
		if curr_amount == 5:
			break
	return url_list


def clear_pictures():
	WordPicture.objects.all().delete()


def load_pictures():
    words = get_words_for_pictures()
    for word in words[:50]:
        url_list = get_picture_urls(word[0])
        for url in url_list:
            word_picture = WordPicture(word_id=word[3], url=url)
            word_picture.save()
        time.sleep(60)
		
		
def append_pictures(words):
    for word in words:
        word["picture_url"] = get_random_picture_url(word["id"])
		

def get_random_picture_url(word_id):
	selection = WordPicture.objects.filter(word_id=word_id)
	pict_list = list(selection)
	if len(pict_list) > 0:
		random_pict = random.choice(pict_list).url
	else:
		random_pict = ""
	return random_pict			
		