
__author__ = "an.luzgarev"

"""
Class for keeping functions for topic section
"""

import random

from .models import Topic


def get_subjects():
	subjects = Topic.objects.values("subject").distinct()
	subjects_list = [x["subject"] for x in subjects]
	return subjects_list


def get_paragraphs(subject=None):
	if subject == None:
		paragraphs = Topic.objects.values("paragraph").distinct()
		paragraphs = paragraphs.order_by("paragraph")
	else:
		paragraphs = Topic.objects.filter(subject=subject).values("paragraph")
		paragraphs = paragraphs.distinct().order_by("paragraph")
	paragraphs_list = [{'value': x["paragraph"].replace(" ","@"),
					    'repr': x["paragraph"]} for x in paragraphs]
	paragraphs_list.append({'value':'all','repr':'All'})
	return paragraphs_list


def get_topics(paragraph=None, subject=None):
	if paragraph == None:
		topics = Topic.objects.values("topic").distinct()
	else:
		topics = Topic.objects.filter(paragraph = paragraph).values("topic").distinct()
	topics_list = [x["topic"] for x in topics]
	random.shuffle(topics_list)
	return topics_list


def get_topics_list():
	topics = Topic.objects.all().values()
	topics_list = [topic for topic in topics]
	return topics_list


