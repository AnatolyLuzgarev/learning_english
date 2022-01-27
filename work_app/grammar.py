
__author__ = "an.luzgarev"

"""
Module for grammar functions
"""

import os
import random

import html

import my_site.settings as settings_set
from .models import GrammarSection, GrammarRule


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
	
	
def get_grammar_sections_old():
	parser = GrammarParser()
	data = get_grammar_text_data()	
	parser.feed(data)
	grammar_sections = parser.get_grammar_sections()
	formatted_sections = [{'val': x.replace(" ", "_"), 'repr': x} for x in grammar_sections]
	return formatted_sections


def get_grammar_sections():
	grammar_sections = GrammarSection.objects.all().values("name")
	formatted_sections = []
	for section in grammar_sections:
		row = {'val': section["name"].replace(" ", "_"), 'repr': section["name"]}
		formatted_sections.append(row)
	return formatted_sections


def get_grammar_rule(grammar_section):
	parser = GrammarParser()
	data = get_grammar_text_data()
	parser.section = grammar_section
	parser.feed(data)
	grammar_rules = parser.get_grammar_rules()
	random_rule =random.choice(grammar_rules)
	return random_rule


def get_grammar_rule_new(grammar_section):
	grammar_rules = GrammarRule.objects.filter(section=grammar_section).values("rule")
	grammar_rules_list = list(grammar_rules)
	random_rule = random.choice(grammar_rules_list)
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


def get_grammar_list():
	all_sections = GrammarSection.objects.all()
	main_list = []
	for section in all_sections:
		rules = GrammarRule.objects.filter(section=section).values("rule", "example")
		rules_list = [{"rule": rule["rule"],"example": rule["example"]} for rule in rules]
		new_elem = {
			"section": section.name,
			"rules": rules_list
		}
		main_list.append(new_elem)
	return main_list