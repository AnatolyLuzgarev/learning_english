
__author__ = "an.luzgarev"

"""
Module for keeping essay functions
"""

import random

from .models import EssayTheme, UserEssay


def get_random_essay_theme():
	selection = EssayTheme.objects.all().values("id", "theme")
	themes_list = [theme for theme in selection]
	theme = random.choice(themes_list)
	value = {
		'id': theme["id"],
		'theme': theme["theme"]
		}
	return value


def get_essays_list(user):
	selection = UserEssay.objects.filter(user=user)
	essays_list = [{"theme": elem.theme.theme, "essay": elem.essay} for elem in selection]
	return essays_list