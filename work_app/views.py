import io
import datetime
import json
import random
import html
import re
import os
import time
import calendar

import requests
import pandas
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse, HttpResponseRedirect
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from xml.etree import ElementTree
from bs4 import BeautifulSoup

import my_site.settings as settings_set
from .models import Word, WordTraining, Topic, UserSettings, EssayTheme, UserEssay
from .models import UserLog
from .models import WordPicture
from .models import CalendarTask
from .models import CompletedTask
from .models import GrammarSection, GrammarRule
from .forms import TopicForm, RegisterForm
from django.db import connection
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
			params = {
				'form': reg_form
				}
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
		print(username,password,user)
		if user is not None:
			login(request,user)
			return HttpResponseRedirect("/")
		else:
			return render(request, "login_page.html",
						 {"info": "login or password is not correct!"})


def logout_view(request):
	logout(request)
	return HttpResponseRedirect("/")


@login_required(login_url="/login/")
@only_get
def index(request):
	if request.method == "GET":
		user = request.user
		username = request.user.username
		additional_stylesheet = get_user_stylesheet("welcome_page", user)
		params = {
			'username':username,
			'additional_stylesheet': additional_stylesheet
			}
		return render(request,"welcome_page.html", params)
	else:
		return HttpResponse(status=501)


@login_required(login_url = "/login/")
@only_get_post
def cabinet(request):
	if request.method == "GET":
		user = request.user
		additional_stylesheet = get_user_stylesheet("cabinet", user)
		current_settings = get_current_settings(user)
		training_words_amount = get_amount_training_words(user)
		user_log = get_user_log(user)
		params = {
		'current_settings': current_settings,
		'amount': training_words_amount	,
		'additional_stylesheet': additional_stylesheet,
		'user_log': user_log,
		'username': user.username
		}
		return render(request, "cabinet.html", params)
	elif request.method == "POST":
		user = request.user
		if request.headers["operation"] == "clear_trainings":
			clear_all_trainings(user)
			return HttpResponse(status=200)
		elif request.headers["operation"] == "settings":
			user = request.user
			main_theme = request.POST.get("main_theme", "blue")
			write_settings(main_theme, user)
			return HttpResponse(status=200)
		elif request.headers["operation"] == "clear_log":
			UserLog.objects.filter(user = user).delete()
			return HttpResponse(status=200)
		elif request.headers["operation"] == "clear_essays":
			UserEssay.objects.filter(user = user).delete()
			return HttpResponse(status=200)


def get_current_settings(user):
	settings_value = UserSettings.objects.filter(user=user).values()
	return settings_value


def get_user_log(user, date=None):
	if date == None:
		selection = UserLog.objects.filter(user=user).values("date", "event")
	else:
		selection = UserLog.objects.filter(user=user, date_level_gr=date).values("date", "event")
	events = [{"date": x["date"], "event": x["event"]} for x in selection]
	return events
	
		
def write_settings(main_theme,user):
	user_settings = UserSettings.objects.filter(user_id = user.id).all()
	if len(user_settings) == 0:
		settings_new = UserSettings(user = user, main_theme = main_theme)
		settings_new.save()
	else:
		user_settings[0].main_theme = main_theme
		user_settings[0].save()


def get_amount_training_words(user):
	amount = WordTraining.objects.filter(user_id=user.id).count()
	return amount


#Settings section
@csrf_exempt
@login_required(login_url = "/login/")
@only_get_post
def initial_settings(request):
	#Here we will handle our file with words
	if request.method == "POST":   
		if request.FILES.get("my_file", "not_found") != "not_found":
			xlsx_file = request.FILES.get("my_file", "not_found")
			xlsx_content = xlsx_file.read()
			write_words(xlsx_content)
			return HttpResponse(status=200)
		elif request.FILES.get("topics_file", "not_found") != "not_found":
			xlsx_file = request.FILES.get("topics_file", "not_found")
			xlsx_content = xlsx_file.read()
			write_topics_xlsx(xlsx_content)
			my_dict = {}
			my_dict["main_content"] = ""
			return render(request,"settings.html", my_dict)
		elif request.FILES.get("essays_file","not_found") != "not_found":
			content = request.FILES.get("essays_file", "not_found")
			write_essays_themes(content)
			return HttpResponse(status=200)
		elif request.FILES.get("grammar_file", "not_found") != "not_found":
			content = request.FILES.get("grammar_file", "not_found")
			content = content.read()
			write_grammar(content)
			return HttpResponse(status=200)
		elif request.headers.get("operation", "") == "load_pictures":
			load_pictures()
			return HttpResponse(status=200)
		elif request.headers.get("operation", "") == "clear_pictures":
			clear_pictures()
			return HttpResponse(status=200)
		elif request.headers.get("operation", "") == "load_all_data":
			load_all_data()
			return HttpResponse(status=200)
		else:
			return HttpResponse("Error!")
	elif request.method == "GET":
		user = request.user
		additional_stylesheet = get_user_stylesheet("settings", user)
		params = {
			'additional_stylesheet': additional_stylesheet
			}
		rend_page = render(request,"settings.html",params)
		return rend_page


def load_all_data():
	files_catalog = os.path.join(settings_set.BASE_DIR, r'my_site/files')
	print(files_catalog)
	words_path = os.path.join(files_catalog, "Words.xlsx")
	topics_path = os.path.join(files_catalog, "Topics.xlsx")
	grammar_path = os.path.join(files_catalog, "grammar.xml")
	essays_path = os.path.join(files_catalog, "Essays_themes.txt")
	with open(words_path, 'rb') as words_reader:
		words_content = words_reader.read()
		write_words(words_content)
	with open(topics_path, 'rb') as topics_reader:
		topics_content = topics_reader.read()
		write_topics_xlsx(topics_content)
	with open(grammar_path, 'rb') as grammar_reader:
		grammar_content = grammar_reader.read()
		write_grammar(grammar_content)
	with open(essays_path, 'rb') as essays_reader:
		essays_content = essays_reader
		write_essays_themes(essays_content)


def write_words(content):
	delete_all_words()
	xlsx_read = pandas.read_excel(io.BytesIO(content))
	for index,row in xlsx_read.iterrows():
		new_word = Word(
			word = row["Word"].strip(),
			translation = nan(row["Translating"]),
			transcription = nan(row["Transcription"]),
			first_letter=row["Word"][0].lower(),
			example=nan(row["Example"]), category=nan(row["Category"])
			)
		new_word.save(using = 'default')
	
	
def write_grammar(content):
	GrammarSection.objects.all().delete()
	text = content.decode("utf-8")
	root = ElementTree.fromstring(text)
	main_list = list(root)[0]
	for section in main_list:
		current_section = ""
		for clause in section:
			if clause.tag == "h3":
				section_text = clause.text
				new_section = GrammarSection(name=section_text)
				new_section.save()
				current_section = new_section
			elif clause.tag == "ul":
				for clause_elem in clause:
					clause_list = list(clause_elem)
					rule = clause_list[0].text.strip()
					if len(clause_list) > 1:
						example = clause_list[1].text.strip()
					else:
						example = ""
					new_rule = GrammarRule(section = current_section, rule = rule, example = example)
					new_rule.save()


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


def write_essays_themes(content):
	EssayTheme.objects.all().delete()
	topics_array = content.readlines()
	for topic in topics_array:
		new_topic = EssayTheme(theme=topic.decode('utf-8'))
		new_topic.save()
	
	
def write_topics_xlsx(file_content):
	delete_all_topics()
	xlsx_read = pandas.read_excel(io.BytesIO(file_content))
	for index,row in xlsx_read.iterrows():
		new_topic = Topic(topic=row["Topic"], paragraph=row["Paragraph"], subject=row["Subject"])
		new_topic.save()

def delete_all_topics():
	Topic.objects.all().delete()


def save_styles_in_file(params):
	styles_dict = {}
	conf_file_path = get_settings_path()
	for x in params:
		styles_dict[x] = params[x]
	text_json = json.dumps(styles_dict)
	with open(conf_file_path,'w') as fw:
		fw.write(text_json)


def clear_all_trainings(user=None):
	if user == None:
		WordTraining.objects.all().delete()
	else:
		WordTraining.objects.filter(user_id=user.id).delete()
		 
		 
def nan(str_val):
	if str_val != "nan":
		return str_val
	else:
		return ""


def delete_all_words():
	Word.objects.all().delete()    


#---------------------------------------------------------------------
#Trainings section
@login_required(login_url="/login/")
@only_get_post
def trainings(request):
	if request.method == "GET":
		user = request.user
		additional_stylesheet = get_user_stylesheet("trainings", user)
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
	

def get_amount_of_words(letter):
	words = Word.objects.filter(first_letter=letter)
	amount_of_words = len(words)
	return amount_of_words


def process_amount_of_words(request,letter):
	if request.POST.get("words_amount",0) != 0:
		return get_amount_of_words(letter)
	else:
		return 0


@login_required(login_url="/login/")
@only_get_post
def essay_writing(request):
	user = request.user
	additional_stylesheet = get_user_stylesheet("essay_writing", user)
	params = {
		'additional_stylesheet': additional_stylesheet
		}
	if request.method == "GET":
		return render(request, "essay_writing.html", params)
	elif request.method == "POST":
		if request.headers["operation"] == "get_random_essay":
			essay_dict = get_random_essay_theme()
			return JsonResponse(essay_dict)
		elif request.headers["operation"] == "add_to_collection":
			user = request.user
			theme_id = request.POST["theme_id"]
			essay_text = request.POST["essay_text"]
			new_essay = UserEssay(user=user, theme_id=theme_id, essay=essay_text)
			new_essay.save()
			

def get_random_essay_theme():
	selection = EssayTheme.objects.all().values("id", "theme")
	themes_list = [theme for theme in selection]
	theme = random.choice(themes_list)
	value = {
		'id': theme["id"],
		'theme': theme["theme"]
		}
	return value


def get_user_stylesheet(name,user=None):
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


@csrf_exempt
@login_required(login_url='/login/')
@only_get_post
def word_translation(request):
	if request.method == "GET":
		user = request.user
		letters = [{'lower': letter.lower(), 'upper': letter.upper()} for letter in get_letters_list()]
		additional_stylesheet = get_user_stylesheet("training_word_translation", user)
		print(additional_stylesheet)
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
		total_array = get_array_of_words(letter, quantity, training_words,user)
		if show_picture:
			append_pictures(total_array)
		str_repr = str(total_array)
		return HttpResponse(str_repr)
	
	
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

   
@csrf_exempt
@login_required(login_url="/login/")
@only_get_post
def translation_word(request):
	if request.method == "GET":
		user = request.user
		letters = [{'lower': letter.lower(), 'upper': letter.upper()} for letter in get_letters_list()]
		additional_stylesheet = get_user_stylesheet("training_word_translation", user)
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
		print(quantity,letter,user,training_words)
		total_array = get_array_of_words(letter, quantity, training_words, user)
		str_repr = str(total_array)
		return HttpResponse(str_repr)


@login_required(login_url='/login/')
@only_get_post
def make_a_sentence(request):
	if request.method == "GET":
		user = request.user
		letters = [{'lower': letter.lower(),'upper': letter.upper()} for letter in get_letters_list()]
		additional_stylesheet = get_user_stylesheet("categories_training", user)
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
		total_array = get_array_of_words(letter, quantity, training_words, user)
		str_repr = json.dumps(total_array, ensure_ascii=False).encode('utf8')
		return HttpResponse(str_repr)	


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
				cursor.execute(query,[user.id])
			else:
				query = query + " AND work_app_word.first_letter = %s"
				cursor.execute(query,[user.id, letter])
			selector = cursor.fetchall()
			for x in selector:
				word = {'word':x[0],'translation':x[1],'transcription':x[2],'id':x[3]}
				total_array.append(word)
	else:
		if letter == "all":
			selection = Word.objects.all().values()
		else:
			selection = Word.objects.filter(first_letter=letter).values()
		total_array = [x for x in selection]
	random.shuffle(total_array)
	total_array = total_array[0:min(quantity,len(total_array))]
	return total_array


@login_required(login_url="/login/")
@only_get_post
def phrasal_verbs(request):
	if request.method == "GET":
		user = request.user
		phrasal_verbs = get_phrasal_verbs_list()
		additional_stylesheet = get_user_stylesheet("categories_training", user)
		params = {
			'phrasal_verbs': phrasal_verbs,
			'additional_stylesheet': additional_stylesheet
			}
		return render(request,"phrasal_verbs.html", params)
	elif request.method == "POST":
		ph_word = request.POST["phrasal_verb"]
		response = str(get_phrasal_verbs(ph_word))
		return HttpResponse(response)


def get_phrasal_verbs_list():
	query = "SELECT work_app_word.* FROM work_app_word WHERE work_app_word.category =  'Phrasal verb'"
	selector = Word.objects.raw(query)
	selector = Word.objects.filter(category = 'Phrasal verb').distinct()
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


@login_required(login_url="/login/")
@only_get_post
def words_series(request):
	if request.method == "GET":
		user = request.user
		letters = [{'lower': letter.lower(),'upper': letter.upper()} for letter in get_letters_list()]
		additional_stylesheet = get_user_stylesheet("categories_training", user)
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
		words = get_array_of_words(letter, quantity, training_words, user)
		words_str = json.dumps(words)
		return HttpResponse(words_str)


#Grammar training section---------------------------------------------
@login_required(login_url="/login/")
@only_get_post
def grammar_training(request):
	if request.method == "GET":
		user = request.user
		grammar_sections = get_grammar_sections()
		print(grammar_sections)
		additional_stylesheet = get_user_stylesheet("categories_training", user)
		params = {
			'grammar_sections': grammar_sections,
			'additional_stylesheet': additional_stylesheet
			}
		return render(request,"grammar_training.html", params)
	elif request.method == "POST":
		section = request.POST.get("section", "all")
		section = section.replace("_"," ")
		random_rule = get_grammar_rule(section)
		rule_dict = {
			"rule": random_rule
			}
		return JsonResponse(rule_dict)
	
	
class GrammarParser(html.parser.HTMLParser):
	grammar_sections = []
	grammar_rules = []
	current_tag = ""
	current_class = ""
	section = ""
	section_flag = False
	
	def handle_starttag(self, tag, attrs):
		self.current_tag = tag
		if len(attrs) > 0:
			self.current_class = attrs[0][1]
			
	def handle_data(self, data):
		if self.current_tag == "h3":
			if self.section == "":
				self.grammar_sections.append(data.strip())
			if data.strip() == self.section:
				self.section_flag = True
			else:
				self.section_flag = False
		if self.section_flag:
			if self.current_class == "clause_point":
				self.grammar_rules.append(data)
	
	def get_grammar_sections(self):
		return self.grammar_sections
	
	def get_grammar_rules(self):
		return self.grammar_rules
	
	
def get_grammar_sections():
	parser = GrammarParser()
	data = get_grammar_text_data()	
	parser.feed(data)
	grammar_sections = parser.get_grammar_sections()
	print(grammar_sections)
	formatted_sections = [{'val': x.replace(" ", "_"), 'repr': x} for x in grammar_sections]
	return formatted_sections


def get_grammar_rule(grammar_section):
	parser = GrammarParser()
	data = get_grammar_text_data()
	parser.section = grammar_section
	parser.feed(data)
	grammar_rules = parser.get_grammar_rules()
	random_rule =random.choice(grammar_rules)
	return random_rule
	

def get_grammar_text_data():
	template_path = os.path.join(settings_set.BASE_DIR, r'my_site/templates/grammar.html')
	with open(template_path, 'r', encoding="utf-8") as fr:
		data = fr.read()
		data = data.replace("\t", "")
		data = data.replace("\n", "")
		first_tag = data.find("<ul>")
		data = data[first_tag:]
	return data


#Categories training----------------------------------------------------------------
@login_required(login_url = "/login/")
@only_get_post
def categories_training(request):
	if request.method == "GET":
		user = request.user
		categories_list = get_list_of_categories()
		additional_stylesheet = get_user_stylesheet("categories_training", user)
		parameters = {
			'categories_list': categories_list,
			'additional_stylesheet': additional_stylesheet
			}
		return render(request, "categories_training.html", parameters)
	elif request.method == "POST":
		category = request.POST["category"]
		words = words_of_category(category)
		json_object = {
		'words': words
		}
		json_response = JsonResponse(json_object)
		return json_response


def words_of_category(category):
	words_list = []
	words = Word.objects.filter(category = category).distinct()
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


#Topics training ----------------------------------------------------------------
@login_required(login_url = "/login/")
@only_get
def topics(request):
	user = request.user
	topics_list = get_topics_list()
	additional_stylesheet = get_user_stylesheet("topics", user)
	params = {
		'topics_list':topics_list,
		'additional_stylesheet': additional_stylesheet
		}
	return render(request,"topics.html",params)


def get_topics_list():
	topics = Topic.objects.all().values()
	topics_list = [topic for topic in topics]
	return topics_list


@login_required(login_url="/login/")
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
		subjects_list = get_subjects()
		if len(subjects_list) > 0:
			paragraphs_list = get_paragraphs(subjects_list[0])
		else:
			paragraphs_list = []
		additional_stylesheet = get_user_stylesheet("categories_training", user)
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
			paragraphs_list = get_paragraphs(subject)
			paragraphs_dict = {"paragraphs": paragraphs_list}
			response_json = JsonResponse(paragraphs_dict)
			return response_json
		elif action == "topics_list":
			topics_list = get_topics(paragraph,subject)
			topics_dict = {"topics": topics_list}
			response_json = JsonResponse(topics_dict)
			return response_json


def get_subjects():
	subjects = Topic.objects.values("subject").distinct()
	subjects_list = [x["subject"] for x in subjects]
	return subjects_list


def get_paragraphs(subject=None):
	if subject == None:
		paragraphs = Topic.objects.values("paragraph").distinct()
	else:
		paragraphs = Topic.objects.filter(subject=subject).values("paragraph").distinct()
	paragraphs_list = [ {'value': x["paragraph"].replace(" ","@"), 'repr': x["paragraph"]} for x in paragraphs]
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

def t(var):
	return HttpResponse(str(var))


#------------------------------------------------------------------------------------
#Dictionary
@login_required(login_url = "/login/")
@only_get_post
def dictionary(request):
	if request.method == "GET":
		user = request.user
		words_list = get_words()
		letters_list = get_letters_list()
		dictionary_style = build_style_string()
		addinional_stylesheet = get_user_stylesheet("dictionary", user)
		words_dict = {
		'words_list':words_list,
		'letters_list': letters_list,
		'dictionary_style': dictionary_style,
		'additional_stylesheet': addinional_stylesheet
		}
		return render(request, "dictionary.html", words_dict)
	elif request.method == "POST":
		if request.headers["operation"] == "picture_uploading":
			picture_url = request.POST.get("picture_url","")
			if picture_url == "":
				picture_file = request.FILES["picture_file"]
				word = request.POST["picture_word"]
				translation = request.POST["picture_translation"]
				binary_data = picture_file.read()
				save_picture_on_server(binary_data,word,translation)
				return HttpResponse(status = 200)
			else:
				word = request.POST["picture_word"]
				translation = request.POST["picture_translation"]
				result = requests.get(picture_url)
				binary_data = result.content
				save_picture_on_server(binary_data,word,translation)
				return HttpResponse(status=200)
		elif request.headers["operation"] == "words_to_training":
			words_to_training = request.POST["words_to_training"]
			user = request.user
			add_words_to_training(words_to_training,user)
			return HttpResponse(status=200)


@login_required(login_url = "/login/")
def dictionary_letter(request,letter):
	if request.method == "GET":
		user = request.user
		letter_low = letter.lower()
		words_list = get_words(letter_low,user)
		letters_list = get_letters_list()
		addinional_stylesheet = get_user_stylesheet("dictionary", user)
		dictionary_style = build_style_string()
		words_dict = {
		'words_list':words_list,
		'letters_list': letters_list,
		'dictionary_style': dictionary_style,
		'additional_stylesheet': addinional_stylesheet
		}
		return render(request, "dictionary.html", words_dict) 
	elif request.method == "POST":
		if request.headers["operation"] == "words_to_training":
			words_to_training = request.POST["words_to_training"]
			user = request.user
			add_words_to_training(words_to_training, user)
			return HttpResponse(status=200)
		

def get_letters_list():
	a_ord = ord("A")
	z_ord = ord("Z")
	letters_list = [chr(i) for i in range(a_ord, z_ord+1)]
	return letters_list


def save_picture_on_server(binary_data,word,translation):
	dirname = os.path.join(settings_set.BASE_DIR,r"my_site/static_files/words_pictures")
	basename = "{}_{}.jpg".format(word,translation).replace(" ", "_")
	file_name = os.path.join(dirname,basename) 
	with open(file_name,'wb') as fw:
		fw.write(binary_data)


def get_list_of_styles():
	path = get_settings_path()
	json_text = ""
	with open(path,'r') as fr:
		json_text = fr.read()
	settings_dict = json.loads(json_text)
	return settings_dict


def build_style_string():
	settings_dict = get_list_of_styles()
	if len(settings_dict) == 0:
		return ""
	style_str = "style = '"
	for x in settings_dict:
		if settings_dict[x] == "default":
			continue
		style_str = style_str + str(x).replace("_","-") + ":" + str(settings_dict[x]) + "; " 
	style_str = style_str + "'"
	return style_str


def get_settings_path():
	path = os.path.join(settings_set.BASE_DIR,r"my_site/static_files/text/settings.json")
	return path


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
	
	
def log(user,event):
	curr_date = datetime.datetime.now()
	new_event = UserLog(user=user, event=event, date=curr_date)
	new_event.save()
			

def remove_words_from_training(words_to_training):
	array = words_to_training.split(";")
	text_message = ""
	try:
		for x in array:
			obj = Word.objects.filter(word=x)
			for y in obj:
				y.to_training = False
				y.save()
	except:
		text_message = "Error" + str(array)
	return text_message
	

#Translator-----------------------------------------------------------------
@login_required(login_url="/login/")
@only_get_post
def translator(request):
	if request.method == "GET":
		user = request.user
		additional_stylesheet = get_user_stylesheet("translator", user)
		params = {
			"additional_stylesheet": additional_stylesheet
			}
		return render(request, "translator.html", params)
	elif request.method == "POST":
		user = request.user
		words_to_training = request.POST["words"]
		add_words_to_training(words_to_training, user)
		return HttpResponse(status = 200)
		
	 
   #---------------------------------------------------------------------------

#Grammar
def grammar(request):
	user = request.user
	additional_stylesheet = get_user_stylesheet("grammar", user)
	sections = get_grammar_list()
	params = {
		'additional_stylesheet': additional_stylesheet,
		'sections': sections
		}
	return render(request,"grammar.html",params)


def get_grammar_list():
	all_sections = GrammarSection.objects.all()
	main_list = []
	for section in all_sections:
		rules = GrammarRule.objects.filter(section=section).values("rule","example")
		rules_list = [{"rule": rule["rule"],"example": rule["example"]} for rule in rules]
		new_elem = {
			"section": section.name,
			"rules": rules_list
		}
		main_list.append(new_elem)
	return main_list


def my_essays(request):
	user = request.user
	essays_list = get_essays_list(user)
	additional_stylesheet = get_user_stylesheet("my_essays", user)
	print(essays_list)
	params = {
		"essays_list": essays_list,
		"additional_stylesheet": additional_stylesheet
		}
	return render(request, "my_essays.html", params)

def get_essays_list(user):
	selection = UserEssay.objects.filter(user=user)
	essays_list = [{"theme": elem.theme.theme, "essay": elem.essay} for elem in selection]
	return essays_list


#toefl---------------------------------------------------------------------
def toefl(request):
	return render(request, "toefl.html")    


#--------------------------------------------------------
#Files
@login_required(login_url="/login/")
@only_get
def files(request):
	if request.method == "GET":
		user = request.user
		files_list = get_list_of_files()
		additional_stylesheet = get_user_stylesheet("files", user=user)
		params = {
			'files_list': files_list,
			'additional_stylesheet': additional_stylesheet
			}
		return render(request,"files.html",params)


def get_file(request,filename):
	if request.method == "GET":
		path_file = get_files_path() + "/" + filename
		with open(path_file,'rb') as fr:
			content = fr.read()
		response = HttpResponse(content)
		response["content-type"] = "application/octet-stream"
		response["content-disposition"] = "attachment; filename=" + filename
		return response
	elif request.method == "POST":
		return HttpResponse("It is not ready yet!")


def get_list_of_files():
	path = get_files_path()
	list_of_files = os.listdir(path)
	return list_of_files


def get_files_path():
	return os.path.join(settings_set.BASE_DIR, r"my_site/files")


@login_required(login_url="/login/")
@only_get_post
def calendar_view(request):
	if request.method == "GET":
		if request.headers.get("operation", "") != "get_tasks":
			user = request.user
			additional_stylesheet = get_user_stylesheet("style", user)
			month = int(request.GET.get("month", datetime.datetime.now().month))
			year = int(request.GET.get("year", datetime.datetime.now().year))
			if len(request.GET) == 0:
				new_path = request.path + "?month={}&year={}".format(month, year)
				return HttpResponseRedirect(new_path)
			weeks_list = get_month_data(month, year, user)
			url = request.path
			months_list = get_months_list(url, year)
			params = {
				'additional_stylesheet': additional_stylesheet,
				'weeks_list': weeks_list,
				'months_list': months_list,
				'current_month': calendar.month_name[month],
				'trainings_list': get_trainings_list(),
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
		

def get_months_list(url, year):
	names = calendar.month_name
	months_list = [
					{
	                 'name': names[i],
				     'number': i,
					 'url': "{}?month={}&year={}".format(url, i, year) 
					 }  
				  for i in range(13)]
	return months_list[1:]


def get_trainings_list():
	trainings_list = [
		              "",
		              "Word-Translation",
					  "Translation-Word",
					  "Essay writing",
					  "Words series",
					  "Make a sentence",
					  "Grammar training",
					  "Topics training",
					  ]
	return trainings_list
	


def get_month_data(month, year, user):
	month_range = calendar.monthcalendar(year, month)
	weeks_list = []
	for week in month_range:
		week_list = []
		week_day = 0
		for day in week:
			if day != 0:
				date = datetime.datetime(year, month, day)
				tasks_amount = get_trainings_amount(date, user)
				compl_tasks = get_compl_tasks_amount(date, user)
				print(date, tasks_amount, compl_tasks)
			else:
				tasks_amount = 0
				compl_tasks = 0
			day_dict = {
						"number": day,
						"weekday": week_day,
						"amount": tasks_amount,
						"completed": compl_tasks
						}
			week_day += 1
			week_list.append(day_dict)
		weeks_list.append(week_list)
	return weeks_list




def get_trainings_amount(date, user):
	with connection.cursor() as cursor:
		query = """
		SELECT
		SUM(t.amount) AS amount
		FROM
		work_app_calendartask AS t
		WHERE
		t.user_id = %s
		AND
		t.date = %s
		"""
		cursor.execute(query, [user.id, date])
		selector = cursor.fetchall()
		tasks = selector[0][0]
		return tasks
	
	
def get_compl_tasks_amount(date, user):
	with connection.cursor() as cursor:
		query = """
		SELECT
		Count(t.training)
		FROM
		work_app_completedtask AS t
		WHERE
		t.user_id = %s
		AND
		date_trunc('day', t.date) = %s
		"""
		cursor.execute(query, [user.id, date])
		result = cursor.fetchall()
		tasks_amount = result[0][0]
		return tasks_amount
		

@login_required(login_url='/login/')
@only_get
def api_list(request):
	if request.method == "GET":
		user = request.user
		api_list = get_api_list()	
		additional_stylesheet = get_user_stylesheet("api_list", user)
		params = {
			"api_list": api_list,
			"additional_stylesheet": additional_stylesheet
			}
		return render(request, "api_list.html", params)


def get_api_list():
	api_list = [
	"get_auth_token",
    "get_translation",
    "training_letter",
    "get_topics",
	"get_grammar",
	"get_essays",
	"logs"
	]
	return api_list
	


