
__author__ = "an.luzgarev"

import datetime
import json
import os
import calendar

import requests
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

import my_site.settings as settings_set
import work_app.initial_loading as i_load
import work_app.dictionary as dict_module
import work_app.logs as logs
import work_app.pictures as pictures
import work_app.calendar as cal
import work_app.essays as essays
import work_app.grammar as grammar_module
import work_app.topics as topics_module
import work_app.words_trainings as words_tr
import work_app.cabinet as cabinet_module
import work_app.files as files_module
import work_app.consts as consts
from .models import UserEssay
from .models import CalendarTask
from .models import CompletedTask
from .forms import TopicForm, RegisterForm
from .decorators import only_get
from .decorators import only_get_post
#Create your views here.


@csrf_exempt
@only_get_post
def register_view(request):
	if request.method == "GET":
		reg_form = RegisterForm()
		params = {'form': reg_form}
		return render(request, "register_page.html", params)
	elif request.method == "POST":
		reg_form = RegisterForm(request.POST)
		try:
			username = request.POST["username"]
			password = request.POST["password"]
			email = request.POST["email"]
			new_user = User.objects.create_user(username=username, password=password, email=email)
			new_user.save()
			return HttpResponseRedirect("/login")
		except:
			params = {'form': reg_form}
			return render(request, "register_page.html", params)
		
                                                                               		
@csrf_exempt
@only_get_post
def login_view(request):
	if request.method == "GET":
		return render(request, "login_page.html")
	elif request.method == "POST":
		username = request.POST["login"]
		password = request.POST["password"]
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request,user)
			return HttpResponseRedirect("/")
		else:
			return render(request, "login_page.html",
						 {"info": "login or password is not correct!"})


def logout_view(request):
	logout(request)
	return HttpResponseRedirect("/")


@login_required
@only_get
def index(request):
	user = request.user
	username = request.user.username
	additional_stylesheet = cabinet_module.get_user_stylesheet("welcome_page", user)
	params = {
		'username': username,
		'additional_stylesheet': additional_stylesheet
		}
	return render(request,"welcome_page.html", params)


@login_required
@only_get_post
def cabinet(request):
	if request.method == "GET":
		user = request.user
		additional_stylesheet = cabinet_module.get_user_stylesheet("cabinet", user)
		current_settings = cabinet_module.get_current_settings(user)
		training_words_amount = cabinet_module.get_amount_training_words(user)
		user_log = logs.get_user_log(user)
		params = {
		'current_settings': current_settings,
		'amount': training_words_amount,
		'additional_stylesheet': additional_stylesheet,
		'user_log': user_log,
		'username': user.username
		}
		return render(request, "cabinet.html", params)
	elif request.method == "POST":
		user = request.user
		operation = request.headers["operation"]
		main_theme = request.POST.get("main_theme", "blue")
		cabinet_module.process_post(operation, main_theme, user)
		return HttpResponse(status=200)
	

#Settings section
@csrf_exempt
@login_required
@only_get_post
def initial_settings(request):
	#Here we will handle our file with words
	if request.method == "POST":   
		if request.FILES.get("my_file", "not_found") != "not_found":
			xlsx_file = request.FILES.get("my_file", "not_found")
			xlsx_content = xlsx_file.read()
			i_load.write_words(xlsx_content)
			return HttpResponse(status=200)
		elif request.FILES.get("topics_file", "not_found") != "not_found":
			xlsx_file = request.FILES.get("topics_file", "not_found")
			xlsx_content = xlsx_file.read()
			i_load.write_topics_xlsx(xlsx_content)
			my_dict = {}
			my_dict["main_content"] = ""
			return render(request,"settings.html", my_dict)
		elif request.FILES.get("essays_file","not_found") != "not_found":
			content = request.FILES.get("essays_file", "not_found")
			i_load.write_essays_themes(content)
			return HttpResponse(status=200)
		elif request.FILES.get("grammar_file", "not_found") != "not_found":
			content = request.FILES.get("grammar_file", "not_found")
			content = content.read()
			i_load.write_grammar(content)
			return HttpResponse(status=200)
		elif request.headers.get("operation", "") == "load_pictures":
			pictures.load_pictures()
			return HttpResponse(status=200)
		elif request.headers.get("operation", "") == "clear_pictures":
			pictures.clear_pictures()
			return HttpResponse(status=200)
		elif request.headers.get("operation", "") == "load_all_data":
			i_load.load_all_data()
			return HttpResponse(status=200)
		else:
			return HttpResponse("Error!")
	elif request.method == "GET":
		user = request.user
		additional_stylesheet = cabinet_module.get_user_stylesheet("settings", user)
		params = {'additional_stylesheet': additional_stylesheet}
		rend_page = render(request, "settings.html", params)
		return rend_page

	
#---------------------------------------------------------------------
#Trainings section
@login_required
@only_get_post
def trainings(request):
	if request.method == "GET":
		user = request.user
		additional_stylesheet = cabinet_module.get_user_stylesheet("trainings", user)
		params = {
			'additional_stylesheet': additional_stylesheet
			}
		return render(request, "trainings.html", params)
	elif request.method == "POST":
		user = request.user
		training = request.POST["training"]
		compl_task = CompletedTask(user=user, 
								  training=training, 
								  date = datetime.datetime.now())
		compl_task.save()
	

@login_required
@only_get_post
def essay_writing(request):
	user = request.user
	additional_stylesheet = cabinet_module.get_user_stylesheet("essay_writing", user)
	params = {'additional_stylesheet': additional_stylesheet}
	if request.method == "GET":
		return render(request, "essay_writing.html", params)
	elif request.method == "POST":
		if request.headers["operation"] == "get_random_essay":
			essay_dict = essays.get_random_essay_theme()
			return JsonResponse(essay_dict)
		elif request.headers["operation"] == "add_to_collection":
			user = request.user
			theme_id = request.POST["theme_id"]
			essay_text = request.POST["essay_text"]
			new_essay = UserEssay(user=user, theme_id=theme_id, essay=essay_text)
			new_essay.save()
			

@csrf_exempt
@login_required
@only_get_post
def word_translation(request):
	if request.method == "GET":
		user = request.user
		letters = [{'lower': letter.lower(), 'upper': letter.upper()} 
			      for letter in dict_module.get_letters_list()]
		additional_stylesheet = cabinet_module.get_user_stylesheet("training_word_translation", user)
		params = {
		'letters': letters,
		'additional_stylesheet': additional_stylesheet
		}
		return render(request, "word_translation.html", params)
	elif request.method == "POST":
		quantity = int(request.POST.get("quantity", 0));
		letter = request.POST.get("letter", "all")
		training_words = request.POST.get("training_words", False)
		show_picture = request.POST.get("show_picture", False)
		user = request.user
		total_array = words_tr.get_array_of_words(letter, quantity, training_words,user)
		if show_picture:
			pictures.append_pictures(total_array)
		str_repr = str(total_array)
		return HttpResponse(str_repr)
	
	   
@csrf_exempt
@login_required
@only_get_post
def translation_word(request):
	if request.method == "GET":
		user = request.user
		letters = [{'lower': letter.lower(), 'upper': letter.upper()} 
			 for letter in dict_module.get_letters_list()]
		additional_stylesheet = cabinet_module.get_user_stylesheet("training_word_translation", user)
		params = {
			'letters': letters,
			'additional_stylesheet': additional_stylesheet
			}
		return render(request,"translation_word.html", params)
	elif request.method == "POST":
		quantity = int(request.POST.get("quantity", 0))
		letter = request.POST.get("letter", "all").lower()
		training_words = request.POST.get("training_words", False)
		user = request.user
		total_array = words_tr.get_array_of_words(letter, quantity, training_words, user)
		str_repr = str(total_array)
		return HttpResponse(str_repr)


@login_required
@only_get_post
def make_a_sentence(request):
	if request.method == "GET":
		user = request.user
		letters = [{'lower': letter.lower(),'upper': letter.upper()} 
			 for letter in dict_module.get_letters_list()]
		additional_stylesheet = cabinet_module.get_user_stylesheet("categories_training", user)
		params = {
			'letters': letters,
			'additional_stylesheet': additional_stylesheet
			}
		return render(request,"make_a_sentence.html", params)
	elif request.method == "POST":
		user = request.user
		quantity = int(request.POST.get("quantity", 0));
		letter = request.POST.get("letter", "all")
		training_words = request.POST.get("training_words", False)
		total_array = words_tr.get_array_of_words(letter, quantity, training_words, user)
		str_repr = json.dumps(total_array, ensure_ascii=False).encode('utf8')
		return HttpResponse(str_repr)	


@login_required
@only_get_post
def phrasal_verbs(request):
	if request.method == "GET":
		user = request.user
		phrasal_verbs = words_tr.get_phrasal_verbs_list()
		additional_stylesheet = cabinet_module.get_user_stylesheet("categories_training", user)
		params = {
			'phrasal_verbs': phrasal_verbs,
			'additional_stylesheet': additional_stylesheet
			}
		return render(request, "phrasal_verbs.html", params)
	elif request.method == "POST":
		ph_word = request.POST["phrasal_verb"]
		response = str(words_tr.get_phrasal_verbs(ph_word))
		return HttpResponse(response)


@login_required
@only_get_post
def words_series(request):
	if request.method == "GET":
		user = request.user
		letters = [{'lower': letter.lower(),'upper': letter.upper()} 
			       for letter in dict_module.get_letters_list()]
		additional_stylesheet = cabinet_module.get_user_stylesheet("categories_training", user)
		params = {
		'letters': letters,
		'additional_stylesheet': additional_stylesheet
		}
		return render(request,"words_series.html", params)
	elif request.method == "POST":
		letter = request.POST.get("first_letter", "all")
		quantity = int(request.POST["quantity"])
		user = request.user
		training_words = request.POST.get("training_words", False)
		words = words_tr.get_array_of_words(letter, quantity, training_words, user)
		words_str = json.dumps(words)
		return HttpResponse(words_str)


#Grammar training section---------------------------------------------
@login_required
@only_get_post
def grammar_training(request):
	if request.method == "GET":
		user = request.user
		grammar_sections = grammar_module.get_grammar_sections()
		additional_stylesheet = cabinet_module.get_user_stylesheet("categories_training", user)
		params = {
			'grammar_sections': grammar_sections,
			'additional_stylesheet': additional_stylesheet
			}
		return render(request,"grammar_training.html", params)
	elif request.method == "POST":
		section = request.POST.get("section", "all")
		section = section.replace("_", " ")
		random_rule = grammar_module.get_grammar_rule(section)
		rule_dict = {"rule": random_rule}
		return JsonResponse(rule_dict)
	
	
#Categories training----------------------------------------------------------------
@login_required
@only_get_post
def categories_training(request):
	if request.method == "GET":
		user = request.user
		categories_list = words_tr.get_list_of_categories()
		additional_stylesheet = cabinet_module.get_user_stylesheet("categories_training", user)
		parameters = {
			'categories_list': categories_list,
			'additional_stylesheet': additional_stylesheet
			}
		return render(request, "categories_training.html", parameters)
	elif request.method == "POST":
		category = request.POST["category"]
		words = words_tr.words_of_category(category)
		json_object = {'words': words}
		json_response = JsonResponse(json_object)
		return json_response


#Topics training ----------------------------------------------------------------
@login_required
@only_get
def topics(request):
	user = request.user
	topics_list = topics_module.get_topics_list()
	additional_stylesheet = cabinet_module.get_user_stylesheet("topics", user)
	params = {
		'topics_list':topics_list,
		'additional_stylesheet': additional_stylesheet
		}
	return render(request,"topics.html",params)


@login_required
@only_get_post
def new_topic(request):
	if request.method == "GET":
		params = {'form': TopicForm()}
		response = render(request, "new_topic.html", params)
		return response
	elif request.method == "POST":
		model_form = TopicForm(request.POST)
		model_form.save()
		return HttpResponseRedirect("/topics")
	else:
		return HttpResponse("Internal error: 500")


@csrf_exempt
@only_get_post
def topics_training(request):
	if request.method == "GET":
		user = request.user
		subjects_list = topics_module.get_subjects()
		if len(subjects_list) > 0:
			paragraphs_list = topics_module.get_paragraphs(subjects_list[0])
		else:
			paragraphs_list = []
		additional_stylesheet = cabinet_module.get_user_stylesheet("categories_training", user)
		parameters = {
		'subjects_list': subjects_list,
		'paragraphs_list': paragraphs_list,
		'additional_stylesheet': additional_stylesheet
		}
		response = render(request, "topics_training.html", parameters)
		return response
	elif request.method == "POST":
		headers = request.headers
		subject = request.POST["subject"]
		paragraph = request.POST["paragraph"].replace("@", " ")
		action = headers["action"]
		if action == "paragraphs_list":
			paragraphs_list = topics_module.get_paragraphs(subject)
			paragraphs_dict = {"paragraphs": paragraphs_list}
			response_json = JsonResponse(paragraphs_dict)
			return response_json
		elif action == "topics_list":
			topics_list = topics_module.get_topics(paragraph,subject)
			topics_dict = {"topics": topics_list}
			response_json = JsonResponse(topics_dict)
			return response_json


#------------------------------------------------------------------------------------
#Dictionary
@login_required
@only_get_post
def dictionary(request):
	if request.method == "GET":
		user = request.user
		words_list = dict_module.get_words()
		letters_list = dict_module.get_letters_list()
		addinional_stylesheet = cabinet_module.get_user_stylesheet("dictionary", user)
		words_dict = {
		'words_list':words_list,
		'letters_list': letters_list,
		'additional_stylesheet': addinional_stylesheet
		}
		return render(request, "dictionary.html", words_dict)
	elif request.method == "POST":
		if request.headers["operation"] == "picture_uploading":
			picture_url = request.POST.get("picture_url", "")
			if picture_url == "":
				picture_file = request.FILES["picture_file"]
				word = request.POST["picture_word"]
				translation = request.POST["picture_translation"]
				binary_data = picture_file.read()
				dict_module.save_picture_on_server(binary_data,word,translation)
				return HttpResponse(status = 200)
			else:
				word = request.POST["picture_word"]
				translation = request.POST["picture_translation"]
				result = requests.get(picture_url)
				binary_data = result.content
				dict_module.save_picture_on_server(binary_data, word, translation)
				return HttpResponse(status=200)
		elif request.headers["operation"] == "words_to_training":
			words_to_training = request.POST["words_to_training"]
			user = request.user
			dict_module.add_words_to_training(words_to_training, user)
			return HttpResponse(status=200)


@login_required
def dictionary_letter(request, letter):
	if request.method == "GET":
		user = request.user
		letter_low = letter.lower()
		words_list = dict_module.get_words(letter_low, user)
		letters_list = dict_module.get_letters_list()
		addinional_stylesheet = cabinet_module.get_user_stylesheet("dictionary", user)
		words_dict = {
		'words_list':words_list,
		'letters_list': letters_list,
		'additional_stylesheet': addinional_stylesheet
		}
		return render(request, "dictionary.html", words_dict) 
	elif request.method == "POST":
		if request.headers["operation"] == "words_to_training":
			words_to_training = request.POST["words_to_training"]
			user = request.user
			dict_module.add_words_to_training(words_to_training, user)
			return HttpResponse(status=200)
		

def get_settings_path():
	path = os.path.join(settings_set.BASE_DIR, r"my_site/static_files/text/settings.json")
	return path

	
#Translator-----------------------------------------------------------------
@login_required
@only_get_post
def translator(request):
	if request.method == "GET":
		user = request.user
		additional_stylesheet = cabinet_module.get_user_stylesheet("translator", user)
		params = {"additional_stylesheet": additional_stylesheet}
		return render(request, "translator.html", params)
	elif request.method == "POST":
		user = request.user
		words_to_training = request.POST["words"]
		dict_module.add_words_to_training(words_to_training, user)
		return HttpResponse(status=200)
		
	 
#---------------------------------------------------------------------------
#Grammar
@login_required
@only_get
def grammar(request):
	user = request.user
	additional_stylesheet = cabinet_module.get_user_stylesheet("grammar", user)
	sections = grammar_module.get_grammar_list()
	params = {
		'additional_stylesheet': additional_stylesheet,
		'sections': sections
		}
	return render(request,"grammar.html",params)


@login_required
@only_get
def my_essays(request):
	user = request.user
	essays_list = essays.get_essays_list(user)
	additional_stylesheet = cabinet_module.get_user_stylesheet("my_essays", user)
	params = {
		"essays_list": essays_list,
		"additional_stylesheet": additional_stylesheet
		}
	return render(request, "my_essays.html", params)


#toefl---------------------------------------------------------------------
def toefl(request):
	return render(request, "toefl.html")    


#--------------------------------------------------------
#Files
@login_required
@only_get
def files(request):
	user = request.user
	files_list = files_module.get_list_of_files()
	additional_stylesheet = cabinet_module.get_user_stylesheet("files", user=user)
	params = {
		'files_list': files_list,
		'additional_stylesheet': additional_stylesheet
		}
	return render(request,"files.html",params)


@login_required
@only_get
def get_file(request, filename):
	path_file = files_module.get_files_path() + "/" + filename
	with open(path_file,'rb') as fr:
		content = fr.read()
	response = HttpResponse(content)
	response["content-type"] = "application/octet-stream"
	response["content-disposition"] = "attachment; filename=" + filename
	return response


@login_required
@only_get_post
def calendar_view(request):
	if request.method == "GET":
		if request.headers.get("operation", "") != "get_tasks":
			user = request.user
			additional_stylesheet = cabinet_module.get_user_stylesheet("style", user)
			month = int(request.GET.get("month", datetime.datetime.now().month))
			year = int(request.GET.get("year", datetime.datetime.now().year))
			if len(request.GET) == 0:
				new_path = request.path + "?month={}&year={}".format(month, year)
				return HttpResponseRedirect(new_path)
			weeks_list = cal.get_month_data(month, year, user)
			url = request.path
			months_list = cal.get_months_list(url, year)
			params = {
				'additional_stylesheet': additional_stylesheet,
				'weeks_list': weeks_list,
				'months_list': months_list,
				'current_month': calendar.month_name[month],
				'trainings_list': cal.get_trainings_list(),
				'trainings_amount': range(5)
				}
			return render(request, "calendar.html", params)
		else:
			user = request.user
			year = int(request.GET.get("year", 2022))
			month = int(request.GET.get("month", 1))
			day = int(request.GET.get("day", 1))
			training_date = datetime.date(year, month, day)
			tasks = CalendarTask.objects.filter(user=user, date=training_date)
			tasks_list = []
			for task in tasks:
				task_dict = {'task': task.training, 'amount': task.amount}
				tasks_list.append(task_dict)
			json_resp = {'tasks': tasks_list}
			return JsonResponse(json_resp)
	elif request.method == "POST":
		user = request.user
		year = int(request.POST.get("year", 2022))
		month_param = request.POST["month"].strip()
		month = int(list(calendar.month_name).index(month_param))
		day = int(request.POST["day"])
		date = datetime.date(year, month, day)
		CalendarTask.objects.filter(user=user, date=date).delete()
		for x in range(5):
			task = request.POST["training_{}".format(x)]
			amount = request.POST["amount_{}".format(x)]
			if task != "":
				new_task = CalendarTask(user=user, date=date, training=task, amount=amount)
				new_task.save()
		return HttpResponse(status=200)
		

@login_required
@only_get
def api_list(request):
	if request.method == "GET":
		user = request.user
		api_list = consts.API_LIST
		additional_stylesheet = cabinet_module.get_user_stylesheet("api_list", user)
		params = {
			"api_list": api_list,
			"additional_stylesheet": additional_stylesheet
			}
		return render(request, "api_list.html", params)



	


