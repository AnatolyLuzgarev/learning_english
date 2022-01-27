
_author_ = "an.luzgarev"

"""
Module contains different functions for working with user settings
"""

import work_app.words_trainings as words_tr
from .models import UserSettings
from .models import WordTraining
from .models import UserLog
from .models import UserEssay


def process_post(operation, main_theme, user):
	if operation == "clear_trainings":
		words_tr.clear_all_trainings(user)
	elif operation == "settings":
		write_settings(main_theme, user)
	elif operation == "clear_log":
		UserLog.objects.filter(user = user).delete()
	elif operation == "clear_essays":
		UserEssay.objects.filter(user = user).delete()


def get_current_settings(user):
	settings_value = UserSettings.objects.filter(user=user).values()
	return settings_value

			
def write_settings(main_theme,user):
	user_settings = UserSettings.objects.filter(user_id=user.id).all()
	if len(user_settings) == 0:
		settings_new = UserSettings(user=user, main_theme=main_theme)
		settings_new.save()
	else:
		user_settings[0].main_theme = main_theme
		user_settings[0].save()


def get_amount_training_words(user):
	amount = WordTraining.objects.filter(user_id=user.id).count()
	return amount


def get_user_stylesheet(name, user=None):
	user_settings = UserSettings.objects.filter(user=user).values("main_theme")
	if len(user_settings) == 0:
		style_dict = {
			'main': 'styles_blue',
			'additional': "{}_blue".format(name),
			'theme': name
			}
		return style_dict
	else:
		style_dict = {
			'main': "styles_{}".format(user_settings[0]["main_theme"].lower()),
			'additional': name,
			'theme': "{}_{}".format(name,user_settings[0]["main_theme"].lower())
			}
		return style_dict