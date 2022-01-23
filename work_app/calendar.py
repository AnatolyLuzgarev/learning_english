
__author__ = "an.luzgarev"

"""
Module for work with calendar
"""

import calendar
import datetime

from django.db import connection


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