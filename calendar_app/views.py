import datetime
import calendar
from django.shortcuts import render, render_to_response




def calendar(request):
	return render(request,"calendar.html")

def get_week_information():
	pass