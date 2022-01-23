
__author__ = "an.luzgarev"

"""
Different functions for logging
"""

import datetime

from .models import UserLog


def log(user, event):
	curr_date = datetime.datetime.now()
	new_event = UserLog(user=user, event=event, date=curr_date)
	new_event.save()
	
	
def get_user_log(user, date=None):
	if date == None:
		selection = UserLog.objects.filter(user=user).values("date", "event")
	else:
		selection = UserLog.objects.filter(user=user, date_level_gr=date).values("date", "event")
	events = [{"date": x["date"], "event": x["event"]} for x in selection]
	return events