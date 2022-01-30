
__author__ = "an.luzgarev"

"""
Module for grammar functions
"""

import random

from django.db import connection

from .models import GrammarSection, GrammarRule


def get_grammar_sections():
	grammar_sections = GrammarSection.objects.all().values("name")
	grammar_sections = [section["name"] for section in grammar_sections]
	return grammar_sections


def get_grammar_rules(grammar_section):
	print(grammar_section)
	with connection.cursor() as cursor:
		query = """
		SELECT
		r.rule
		FROM
		work_app_grammarrule AS r
		LEFT JOIN
		work_app_grammarsection AS s
		ON r.section_id = s.id
		WHERE
		s.name = %s
		"""
		cursor.execute(query, [grammar_section])
		grammar_rules = cursor.fetchall()
		grammar_rules_list = [x[0] for x in grammar_rules]
		random.shuffle(grammar_rules_list) 
		return grammar_rules_list
	
	
def get_grammar_list():
	all_sections = GrammarSection.objects.all()
	main_list = []
	for section in all_sections:
		rules = GrammarRule.objects.filter(section=section).values("rule", "example")
		rules_list = [{"rule": rule["rule"],"example": rule["example"]} for rule in rules]
		new_elem = {"section": section.name, "rules": rules_list}
		main_list.append(new_elem)
	return main_list