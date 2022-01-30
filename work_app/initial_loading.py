
__author__ = "an.luzgarev"

"""Contains functions for loading initial data
(words, essay themes, topics, grammar)"""

import io
import os

import pandas
from xml.etree import ElementTree

import my_site.settings as settings_set
from .models import Word, Topic, EssayTheme
from .models import GrammarSection, GrammarRule


def load_all_data()-> None:
	"""Loads all the data from the files in the project catalog: 
	words, topics, grammar, essay themes"""
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
			translation = row["Translating"],
			transcription = row["Transcription"],
			first_letter=row["Word"][0].lower(),
			example=row["Example"],
			category=row["Category"]
			)
		if type(row["Translating"]) != str:
			new_word.translation = ""
			new_word.transcription = ""
			new_word.example = ""
			new_word.category = ""
		new_word.save()
	
	
def delete_all_words():
	Word.objects.all().delete()   	
	
	
def write_grammar(content):
	GrammarSection.objects.all().delete()
	text = content.decode("utf-8")
	root = ElementTree.fromstring(text)
	main_list = list(root)[0]
	for section in main_list:
		current_section = ""
		for clause in section:
			if clause.tag == "h3":
				section_text = clause.text.strip()
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
					new_rule = GrammarRule(section=current_section,
										   rule=rule,
										   example=example)
					new_rule.save()


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
		if type(row["Topic"]) == str:
			new_topic = Topic(topic=row["Topic"],
					    paragraph=row["Paragraph"],
					    subject=row["Subject"])
			new_topic.save()


def delete_all_topics():
	Topic.objects.all().delete()	

					







					